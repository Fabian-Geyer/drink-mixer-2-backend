from itertools import count

from fastapi.testclient import TestClient
from httpx import Response

_ingredient_name_seq = count()


def _create_ingredient(
    client: TestClient, name: str | None = None, alcohol_percentage: int = 0
) -> int:
    if name is None:
        name = f"Orangesaft {next(_ingredient_name_seq)}"
    response = client.post(
        "/api/ingredients",
        json={"name": name, "alcohol_percentage": alcohol_percentage},
    )
    id_: int = response.json()["id"]
    return id_


def _create_cocktail(
    client: TestClient, name: str = "Screwdriver", ingredients: list[dict] | None = None
) -> Response:
    if ingredients is None:
        ingredients = [{"ingredient_id": _create_ingredient(client), "amount": 1}]
    return client.post("/api/cocktails", json={"name": name, "ingredients": ingredients})


def test_create_cocktail(client: TestClient) -> None:
    orange_id = _create_ingredient(client, name="Orangesaft")
    vodka_id = _create_ingredient(client, name="Wodka", alcohol_percentage=40)

    response = _create_cocktail(
        client,
        ingredients=[
            {"ingredient_id": orange_id, "amount": 2},
            {"ingredient_id": vodka_id, "amount": 1},
        ],
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Screwdriver"
    ingredients = {item["id"]: item for item in body["ingredients"]}
    assert ingredients[orange_id]["amount_percentage"] == 67
    assert ingredients[vodka_id]["amount_percentage"] == 33


def test_create_cocktail_duplicate_name_rejected(client: TestClient) -> None:
    _create_cocktail(client, name="Screwdriver")

    response = _create_cocktail(client, name="Screwdriver")

    assert response.status_code == 409


def test_create_cocktail_rejects_unknown_ingredient(client: TestClient) -> None:
    response = _create_cocktail(client, ingredients=[{"ingredient_id": 999, "amount": 1}])

    assert response.status_code == 400


def test_create_cocktail_rejects_empty_ingredients(client: TestClient) -> None:
    response = _create_cocktail(client, ingredients=[])

    assert response.status_code == 422


def test_create_cocktail_rejects_empty_name(client: TestClient) -> None:
    response = _create_cocktail(client, name="")

    assert response.status_code == 422


def test_create_cocktail_rejects_non_positive_amount(client: TestClient) -> None:
    ingredient_id = _create_ingredient(client)

    response = _create_cocktail(client, ingredients=[{"ingredient_id": ingredient_id, "amount": 0}])

    assert response.status_code == 422


def test_list_cocktails_ordered_by_name(client: TestClient) -> None:
    _create_cocktail(client, name="Wodka Lemon")
    _create_cocktail(client, name="Apfel-O")

    response = client.get("/api/cocktails")

    assert response.status_code == 200
    names = [cocktail["name"] for cocktail in response.json()]
    assert names == ["Apfel-O", "Wodka Lemon"]


def test_get_cocktail(client: TestClient) -> None:
    cocktail_id = _create_cocktail(client).json()["id"]

    response = client.get(f"/api/cocktails/{cocktail_id}")

    assert response.status_code == 200
    assert response.json()["id"] == cocktail_id


def test_get_cocktail_not_found(client: TestClient) -> None:
    response = client.get("/api/cocktails/999")

    assert response.status_code == 404


def test_update_cocktail_name(client: TestClient) -> None:
    cocktail_id = _create_cocktail(client, name="Screwdriver").json()["id"]

    response = client.put(f"/api/cocktails/{cocktail_id}", json={"name": "Screwdriver 2.0"})

    assert response.status_code == 200
    assert response.json()["name"] == "Screwdriver 2.0"


def test_update_cocktail_replaces_ingredients(client: TestClient) -> None:
    ingredient_id = _create_ingredient(client)
    cocktail_id = _create_cocktail(
        client, ingredients=[{"ingredient_id": ingredient_id, "amount": 1}]
    ).json()["id"]
    other_id = _create_ingredient(client, name="Wodka", alcohol_percentage=40)

    response = client.put(
        f"/api/cocktails/{cocktail_id}",
        json={"ingredients": [{"ingredient_id": other_id, "amount": 3}]},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["ingredients"]) == 1
    assert body["ingredients"][0]["id"] == other_id
    assert body["ingredients"][0]["amount_percentage"] == 100


def test_update_cocktail_rejects_duplicate_name(client: TestClient) -> None:
    _create_cocktail(client, name="Screwdriver")
    other_id = _create_cocktail(client, name="Apfel-O").json()["id"]

    response = client.put(f"/api/cocktails/{other_id}", json={"name": "Screwdriver"})

    assert response.status_code == 409


def test_update_cocktail_not_found(client: TestClient) -> None:
    response = client.put("/api/cocktails/999", json={"name": "Screwdriver"})

    assert response.status_code == 404


def test_delete_cocktail(client: TestClient) -> None:
    cocktail_id = _create_cocktail(client).json()["id"]

    response = client.delete(f"/api/cocktails/{cocktail_id}")

    assert response.status_code == 204
    assert client.get(f"/api/cocktails/{cocktail_id}").status_code == 404


def test_delete_cocktail_does_not_delete_shared_ingredient(client: TestClient) -> None:
    ingredient_id = _create_ingredient(client)
    cocktail_id = _create_cocktail(
        client, ingredients=[{"ingredient_id": ingredient_id, "amount": 1}]
    ).json()["id"]

    client.delete(f"/api/cocktails/{cocktail_id}")

    assert client.get(f"/api/ingredients/{ingredient_id}").status_code == 200


def test_delete_cocktail_not_found(client: TestClient) -> None:
    response = client.delete("/api/cocktails/999")

    assert response.status_code == 404
