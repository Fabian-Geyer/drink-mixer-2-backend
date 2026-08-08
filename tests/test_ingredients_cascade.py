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


def test_delete_ingredient_deletes_dependent_cocktail(client: TestClient) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    cocktail_id = _create_cocktail(client, "Screwdriver", [orange_id])

    response = client.delete(f"/api/ingredients/{orange_id}")

    assert response.status_code == 204
    assert client.get(f"/api/cocktails/{cocktail_id}").status_code == 404


def test_delete_ingredient_does_not_affect_unrelated_cocktail(client: TestClient) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    vodka_id = _create_ingredient(client, "Wodka")
    unrelated_cocktail_id = _create_cocktail(client, "Straight Vodka", [vodka_id])
    _create_cocktail(client, "Screwdriver", [orange_id, vodka_id])

    client.delete(f"/api/ingredients/{orange_id}")

    assert client.get(f"/api/cocktails/{unrelated_cocktail_id}").status_code == 200


def test_delete_ingredient_clears_referencing_slot(client: TestClient, db_session: Session) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    db_session.add(Slot(id=1, ingredient_id=orange_id, amount_percentage=100))
    db_session.commit()

    response = client.delete(f"/api/ingredients/{orange_id}")

    assert response.status_code == 204
    slot = client.get("/api/slots").json()[0]
    assert slot["ingredient_id"] == 0


def test_delete_ingredient_does_not_clear_unrelated_slot(
    client: TestClient, db_session: Session
) -> None:
    orange_id = _create_ingredient(client, "Orangesaft")
    vodka_id = _create_ingredient(client, "Wodka")
    db_session.add(Slot(id=1, ingredient_id=vodka_id, amount_percentage=100))
    db_session.commit()

    client.delete(f"/api/ingredients/{orange_id}")

    slot = client.get("/api/slots").json()[0]
    assert slot["ingredient_id"] == vodka_id
