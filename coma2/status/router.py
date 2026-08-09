import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from coma2.cocktails.service import get_cocktail_with_ingredients, is_cocktail_available
from coma2.config import settings
from coma2.database import get_db
from coma2.slots.models import Slot
from coma2.slots.schemas import SlotRead
from coma2.status.models import Order
from coma2.status.schemas import MachineStatus, OrderCreate, OrderRead

router = APIRouter(prefix="/api/status", tags=["status"])


def _now() -> datetime:
    # Naive UTC, to compare directly against `created_at` (SQLite's func.now()
    # is stored naive/UTC too) without a tz-aware/naive mismatch.
    return datetime.now(UTC).replace(tzinfo=None)


def get_latest_order(db: Session) -> Order | None:
    return db.scalar(select(Order).order_by(Order.id.desc()).limit(1))


def compute_machine_status(
    latest_order: Order | None, now: datetime
) -> tuple[Literal["idle", "mixing"], float | None]:
    if latest_order is None:
        return "idle", None
    seconds_remaining = (
        latest_order.duration_seconds - (now - latest_order.created_at).total_seconds()
    )
    if seconds_remaining <= 0:
        return "idle", None
    return "mixing", seconds_remaining


def pick_slot_for_ingredient(slots: list[Slot], ingredient_id: int) -> Slot | None:
    """The fullest slot loaded with this ingredient (drink from the fullest first)."""
    candidates = [slot for slot in slots if slot.ingredient_id == ingredient_id]
    if not candidates:
        return None
    return max(candidates, key=lambda slot: (slot.amount_percentage, -slot.id))


def build_status_payload(db: Session) -> MachineStatus:
    latest_order = get_latest_order(db)
    state, seconds_remaining = compute_machine_status(latest_order, _now())
    slots = list(db.scalars(select(Slot).order_by(Slot.id)))
    current_order = (
        OrderRead.model_validate(latest_order) if state == "mixing" and latest_order else None
    )
    return MachineStatus(
        state=state,
        current_order=current_order,
        seconds_remaining=seconds_remaining,
        slots=[SlotRead.model_validate(slot) for slot in slots],
    )


@router.get("", response_model=MachineStatus)
def get_status(db: Session = Depends(get_db)) -> MachineStatus:
    return build_status_payload(db)


@router.post("/orders", response_model=MachineStatus, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> MachineStatus:
    state, _ = compute_machine_status(get_latest_order(db), _now())
    if state == "mixing":
        raise HTTPException(status.HTTP_409_CONFLICT, "Machine is currently mixing another order.")

    cocktail = get_cocktail_with_ingredients(db, payload.cocktail_id)
    if cocktail is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cocktail not found")

    loaded_ingredient_ids = {
        ingredient_id
        for (ingredient_id,) in db.execute(select(Slot.ingredient_id))
        if ingredient_id != 0
    }
    if not is_cocktail_available(cocktail, loaded_ingredient_ids):
        raise HTTPException(status.HTTP_409_CONFLICT, "Cocktail is not currently available.")

    slots = list(db.scalars(select(Slot).order_by(Slot.id)))
    picks: list[tuple[Slot, int]] = []
    for link in cocktail.ingredients:
        slot = pick_slot_for_ingredient(slots, link.ingredient_id)
        if slot is None or slot.amount_percentage < link.amount:
            raise HTTPException(status.HTTP_409_CONFLICT, f"Insufficient {link.ingredient.name}.")
        picks.append((slot, link.amount))

    order = Order(
        cocktail_id=cocktail.id,
        cocktail_name=cocktail.name,
        duration_seconds=settings.mixing_duration_seconds,
    )
    db.add(order)
    for slot, amount in picks:
        slot.amount_percentage = max(0, slot.amount_percentage - amount)
    db.commit()

    return build_status_payload(db)


async def _event_stream(db: Session) -> AsyncGenerator[str, None]:
    yield "retry: 3000\n\n"
    while True:
        # Reused session held for the connection's lifetime (so it goes
        # through the same get_db DI/test-override path as every other
        # route) - expire_all() forces each tick to re-read current rows
        # rather than serving stale identity-map copies.
        db.expire_all()
        payload = build_status_payload(db)
        yield f"data: {json.dumps(payload.model_dump(mode='json'))}\n\n"
        await asyncio.sleep(1)


@router.get("/stream")
async def stream_status(db: Session = Depends(get_db)) -> StreamingResponse:
    return StreamingResponse(_event_stream(db), media_type="text/event-stream")
