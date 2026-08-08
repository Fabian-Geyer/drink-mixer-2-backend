from fastapi.testclient import TestClient
from httpx import Response


def _create(client: TestClient, name: str = "Vodka", alcohol_percentage: int = 40) -> Response:
    return client.post(
        "/api/ingredients",
        json={"name": name, "alcohol_percentage": alcohol_percentage},
    )


def test_create_ingredient(client: TestClient) -> None:
    response = _create(client)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Vodka"
    assert body["alcohol_percentage"] == 40
    assert "id" in body
    assert "timestamp" in body


def test_create_ingredient_duplicate_name_rejected(client: TestClient) -> None:
    _create(client)

    response = _create(client)

    assert response.status_code == 409


def test_create_ingredient_rejects_out_of_range_alcohol_percentage(client: TestClient) -> None:
    response = _create(client, alcohol_percentage=150)

    assert response.status_code == 422


def test_create_ingredient_rejects_empty_name(client: TestClient) -> None:
    response = _create(client, name="")

    assert response.status_code == 422


def test_list_ingredients_ordered_by_name(client: TestClient) -> None:
    _create(client, name="Wodka")
    _create(client, name="Apfelsaft")

    response = client.get("/api/ingredients")

    assert response.status_code == 200
    names = [ingredient["name"] for ingredient in response.json()]
    assert names == ["Apfelsaft", "Wodka"]


def test_get_ingredient(client: TestClient) -> None:
    ingredient_id = _create(client).json()["id"]

    response = client.get(f"/api/ingredients/{ingredient_id}")

    assert response.status_code == 200
    assert response.json()["id"] == ingredient_id


def test_get_ingredient_not_found(client: TestClient) -> None:
    response = client.get("/api/ingredients/999")

    assert response.status_code == 404


def test_update_ingredient_partial(client: TestClient) -> None:
    ingredient_id = _create(client).json()["id"]

    response = client.put(f"/api/ingredients/{ingredient_id}", json={"alcohol_percentage": 37})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Vodka"
    assert body["alcohol_percentage"] == 37


def test_update_ingredient_rejects_duplicate_name(client: TestClient) -> None:
    _create(client, name="Vodka")
    other_id = _create(client, name="Wodka").json()["id"]

    response = client.put(f"/api/ingredients/{other_id}", json={"name": "Vodka"})

    assert response.status_code == 409


def test_update_ingredient_not_found(client: TestClient) -> None:
    response = client.put("/api/ingredients/999", json={"name": "Vodka"})

    assert response.status_code == 404


def test_delete_ingredient(client: TestClient) -> None:
    ingredient_id = _create(client).json()["id"]

    response = client.delete(f"/api/ingredients/{ingredient_id}")

    assert response.status_code == 204
    assert client.get(f"/api/ingredients/{ingredient_id}").status_code == 404


def test_delete_ingredient_not_found(client: TestClient) -> None:
    response = client.delete("/api/ingredients/999")

    assert response.status_code == 404
