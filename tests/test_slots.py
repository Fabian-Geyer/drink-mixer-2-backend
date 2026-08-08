from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from coma2.slots.models import Slot


def _add_slot(db_session: Session, slot_id: int, ingredient_id: int = 0) -> None:
    db_session.add(Slot(id=slot_id, ingredient_id=ingredient_id, amount_percentage=0))
    db_session.commit()


def _create_ingredient(client: TestClient, name: str = "Vodka") -> int:
    response = client.post("/api/ingredients", json={"name": name, "alcohol_percentage": 40})
    id_: int = response.json()["id"]
    return id_


def test_list_slots_ordered_by_id(client: TestClient, db_session: Session) -> None:
    _add_slot(db_session, 2)
    _add_slot(db_session, 1)

    response = client.get("/api/slots")

    assert response.status_code == 200
    ids = [slot["id"] for slot in response.json()]
    assert ids == [1, 2]


def test_update_slot_ingredient_id(client: TestClient, db_session: Session) -> None:
    _add_slot(db_session, 1)
    ingredient_id = _create_ingredient(client)

    response = client.patch("/api/slots/1", json={"ingredient_id": ingredient_id})

    assert response.status_code == 200
    body = response.json()
    assert body["ingredient_id"] == ingredient_id


def test_update_slot_amount_percentage_only(client: TestClient, db_session: Session) -> None:
    _add_slot(db_session, 1, ingredient_id=0)

    response = client.patch("/api/slots/1", json={"amount_percentage": 75})

    assert response.status_code == 200
    body = response.json()
    assert body["amount_percentage"] == 75
    assert body["ingredient_id"] == 0


def test_update_slot_can_clear_with_zero(client: TestClient, db_session: Session) -> None:
    ingredient_id = _create_ingredient(client)
    _add_slot(db_session, 1, ingredient_id=ingredient_id)

    response = client.patch("/api/slots/1", json={"ingredient_id": 0})

    assert response.status_code == 200
    assert response.json()["ingredient_id"] == 0


def test_update_slot_rejects_unknown_ingredient(client: TestClient, db_session: Session) -> None:
    _add_slot(db_session, 1)

    response = client.patch("/api/slots/1", json={"ingredient_id": 999})

    assert response.status_code == 400


def test_update_slot_rejects_out_of_range_percentage(
    client: TestClient, db_session: Session
) -> None:
    _add_slot(db_session, 1)

    response = client.patch("/api/slots/1", json={"amount_percentage": 150})

    assert response.status_code == 422


def test_update_slot_not_found(client: TestClient) -> None:
    response = client.patch("/api/slots/999", json={"amount_percentage": 50})

    assert response.status_code == 404
