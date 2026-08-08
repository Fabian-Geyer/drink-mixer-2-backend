from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from coma2.database import get_db
from coma2.ingredients.models import Ingredient
from coma2.slots.models import Slot
from coma2.slots.schemas import SlotRead, SlotUpdate

router = APIRouter(prefix="/api/slots", tags=["slots"])

# Slots represent fixed physical dispenser ports, so there's no create
# endpoint - the set of slots is established once (see the seed script) and
# only ever updated in place.


@router.get("", response_model=list[SlotRead])
def list_slots(db: Session = Depends(get_db)) -> list[Slot]:
    return list(db.scalars(select(Slot).order_by(Slot.id)))


@router.patch("/{slot_id}", response_model=SlotRead)
def update_slot(slot_id: int, payload: SlotUpdate, db: Session = Depends(get_db)) -> Slot:
    slot = db.get(Slot, slot_id)
    if slot is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Slot not found")

    updates = payload.model_dump(exclude_unset=True)
    ingredient_id = updates.get("ingredient_id")
    if (
        ingredient_id is not None
        and ingredient_id != 0
        and db.get(Ingredient, ingredient_id) is None
    ):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ingredient id does not exist")

    for field, value in updates.items():
        setattr(slot, field, value)

    db.commit()
    db.refresh(slot)
    return slot
