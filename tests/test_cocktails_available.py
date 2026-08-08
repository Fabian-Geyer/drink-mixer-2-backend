from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from coma2.slots.models import Slot


def _create_ingredient(client: TestClient, name: str) -> int:
    response = client.post("/api/ingredients", json={"name": name, "alcohol_percentage": 0})
    id_: int = response.json()["id"]
    return id_


def _create_cocktail(client: TestClient, name: str, ingredient_ids: list[int]) -> int:
    response = client.post(
        "/api/cocktails",
        json={
            "name": name,
            "ingredients": [{"ingredient_id": i, "amount": 1} for i in ingredient_ids],
        },
    )
    id_: int = response.json()["id"]
    return id_


def _load_slot(db_session: Session, slot_id: int, ingredient_id: int) -> None:
    db_session.add(Slot(id=slot_id, ingredient_id=ingredient_id, amount_percentage=100))
    db_session.commit()


def test_available_empty_when_nothing_loaded(client: TestClient) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    _create_cocktail(client, "Screwdriver", [orange_id])

    response = client.get("/api/cocktails/available")

    assert response.status_code == 200
    assert response.json() == []


def test_available_excludes_cocktail_missing_an_ingredient(
    client: TestClient, db_session: Session
) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    vodka_id = _create_ingredient(client, "Wodka")
    _create_cocktail(client, "Screwdriver", [orange_id, vodka_id])
    _load_slot(db_session, 1, orange_id)

    response = client.get("/api/cocktails/available")

    assert response.status_code == 200
    assert response.json() == []


def test_available_includes_cocktail_once_all_ingredients_loaded(
    client: TestClient, db_session: Session
) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    vodka_id = _create_ingredient(client, "Wodka")
    cocktail_id = _create_cocktail(client, "Screwdriver", [orange_id, vodka_id])
    _load_slot(db_session, 1, orange_id)
    _load_slot(db_session, 2, vodka_id)

    response = client.get("/api/cocktails/available")

    assert response.status_code == 200
    body = response.json()
    assert [c["id"] for c in body] == [cocktail_id]


def test_available_sorted_by_name(client: TestClient, db_session: Session) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    _create_cocktail(client, "Wodka Lemon", [orange_id])
    _create_cocktail(client, "Apfel-O", [orange_id])
    _load_slot(db_session, 1, orange_id)

    response = client.get("/api/cocktails/available")

    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert names == ["Apfel-O", "Wodka Lemon"]


def test_available_ignores_empty_slots(client: TestClient, db_session: Session) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    _create_cocktail(client, "Screwdriver", [orange_id])
    _load_slot(db_session, 1, 0)

    response = client.get("/api/cocktails/available")

    assert response.status_code == 200
    assert response.json() == []
