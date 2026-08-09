import asyncio
import json
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from coma2.slots.models import Slot
from coma2.status.models import Order
from coma2.status.router import _event_stream, compute_machine_status, pick_slot_for_ingredient


def _create_ingredient(client: TestClient, name: str) -> int:
    response = client.post("/api/ingredients", json={"name": name, "alcohol_percentage": 0})
    id_: int = response.json()["id"]
    return id_


def _create_cocktail(client: TestClient, name: str, ingredients: list[tuple[int, int]]) -> int:
    response = client.post(
        "/api/cocktails",
        json={
            "name": name,
            "ingredients": [{"ingredient_id": i, "amount": amount} for i, amount in ingredients],
        },
    )
    id_: int = response.json()["id"]
    return id_


def _load_slot(
    db_session: Session, slot_id: int, ingredient_id: int, amount_percentage: int = 100
) -> None:
    db_session.add(
        Slot(id=slot_id, ingredient_id=ingredient_id, amount_percentage=amount_percentage)
    )
    db_session.commit()


def test_status_idle_with_no_orders(client: TestClient) -> None:
    response = client.get("/api/status")

    assert response.status_code == 200
    body = response.json()
    assert body["state"] == "idle"
    assert body["current_order"] is None
    assert body["seconds_remaining"] is None


def test_order_rejected_when_cocktail_missing_ingredient(
    client: TestClient, db_session: Session
) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    vodka_id = _create_ingredient(client, "Wodka")
    cocktail_id = _create_cocktail(client, "Screwdriver", [(orange_id, 50), (vodka_id, 50)])
    _load_slot(db_session, 1, orange_id)

    response = client.post("/api/status/orders", json={"cocktail_id": cocktail_id})

    assert response.status_code == 409


def test_order_rejected_when_slot_insufficient(client: TestClient, db_session: Session) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    cocktail_id = _create_cocktail(client, "Screwdriver", [(orange_id, 50)])
    _load_slot(db_session, 1, orange_id, amount_percentage=20)

    response = client.post("/api/status/orders", json={"cocktail_id": cocktail_id})

    assert response.status_code == 409
    slot = db_session.get(Slot, 1)
    assert slot is not None
    assert slot.amount_percentage == 20


def test_order_happy_path(client: TestClient, db_session: Session) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    vodka_id = _create_ingredient(client, "Wodka")
    cocktail_id = _create_cocktail(client, "Screwdriver", [(orange_id, 30), (vodka_id, 20)])
    _load_slot(db_session, 1, orange_id, amount_percentage=100)
    _load_slot(db_session, 2, vodka_id, amount_percentage=100)

    response = client.post("/api/status/orders", json={"cocktail_id": cocktail_id})

    assert response.status_code == 201
    body = response.json()
    assert body["state"] == "mixing"
    assert body["current_order"]["cocktail_id"] == cocktail_id
    assert body["current_order"]["cocktail_name"] == "Screwdriver"
    assert body["seconds_remaining"] > 0

    db_session.expire_all()
    orange_slot = db_session.get(Slot, 1)
    vodka_slot = db_session.get(Slot, 2)
    assert orange_slot is not None
    assert vodka_slot is not None
    assert orange_slot.amount_percentage == 70
    assert vodka_slot.amount_percentage == 80


def test_order_rejected_while_machine_busy(client: TestClient, db_session: Session) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    cocktail_id = _create_cocktail(client, "Screwdriver", [(orange_id, 10)])
    _load_slot(db_session, 1, orange_id, amount_percentage=100)

    first = client.post("/api/status/orders", json={"cocktail_id": cocktail_id})
    assert first.status_code == 201

    second = client.post("/api/status/orders", json={"cocktail_id": cocktail_id})
    assert second.status_code == 409


def test_pick_slot_for_ingredient_prefers_fullest() -> None:
    slots = [
        Slot(id=1, ingredient_id=5, amount_percentage=40),
        Slot(id=2, ingredient_id=5, amount_percentage=90),
    ]

    picked = pick_slot_for_ingredient(slots, 5)

    assert picked is not None
    assert picked.id == 2


def test_pick_slot_for_ingredient_ties_break_on_lowest_id() -> None:
    slots = [
        Slot(id=3, ingredient_id=5, amount_percentage=50),
        Slot(id=1, ingredient_id=5, amount_percentage=50),
    ]

    picked = pick_slot_for_ingredient(slots, 5)

    assert picked is not None
    assert picked.id == 1


def test_pick_slot_for_ingredient_none_when_not_loaded() -> None:
    slots = [Slot(id=1, ingredient_id=0, amount_percentage=0)]

    assert pick_slot_for_ingredient(slots, 5) is None


def test_compute_machine_status_idle_with_no_order() -> None:
    state, seconds_remaining = compute_machine_status(None, datetime(2026, 1, 1))

    assert state == "idle"
    assert seconds_remaining is None


def test_compute_machine_status_mixing_within_window() -> None:
    started = datetime(2026, 1, 1, 12, 0, 0)
    order = Order(
        id=1, cocktail_id=1, cocktail_name="Screwdriver", created_at=started, duration_seconds=8
    )

    state, seconds_remaining = compute_machine_status(order, started + timedelta(seconds=3))

    assert state == "mixing"
    assert seconds_remaining is not None
    assert 4.9 < seconds_remaining < 5.1


def test_compute_machine_status_idle_after_window() -> None:
    started = datetime(2026, 1, 1, 12, 0, 0)
    order = Order(
        id=1, cocktail_id=1, cocktail_name="Screwdriver", created_at=started, duration_seconds=8
    )

    state, seconds_remaining = compute_machine_status(order, started + timedelta(seconds=9))

    assert state == "idle"
    assert seconds_remaining is None


def test_event_stream_first_snapshot_is_valid(db_session: Session) -> None:
    # Drives the generator directly (not over real HTTP/TestClient streaming)
    # since the generator loops forever - this bounds the test to exactly
    # two chunks and closes it explicitly, rather than relying on ASGI
    # disconnect-cancellation plumbing in a synchronous test.
    async def _collect() -> tuple[str, str]:
        generator = _event_stream(db_session)
        retry_chunk = await generator.__anext__()
        data_chunk = await generator.__anext__()
        await generator.aclose()
        return retry_chunk, data_chunk

    retry_chunk, data_chunk = asyncio.run(_collect())

    assert retry_chunk.startswith("retry:")
    payload = json.loads(data_chunk.removeprefix("data:").strip())
    assert payload["state"] == "idle"
    assert payload["slots"] == []
