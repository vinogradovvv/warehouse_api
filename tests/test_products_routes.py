import pytest
from sqlalchemy.future import select

from app.db.db_models import Product


@pytest.mark.asyncio(loop_scope="session")
async def test_add_product_ok(test_client, test_session):
    products_number = len((await test_session.execute(select(Product))).scalars().all())
    response = await test_client.post(
        "/products",
        json={"name": "E46", "description": "330XD", "price": 10000, "amount": 2},
    )
    assert response.status_code == 201
    assert response.json()["result"] is True
    new_product_number = len(
        (await test_session.execute(select(Product))).scalars().all()
    )
    assert new_product_number - products_number == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_add_product_fail(test_client, test_session):
    response = await test_client.post(
        "/products",
        json={"name": 100, "description": "330XD", "price": 10000, "amount": 2},
    )
    assert response.status_code == 422
    assert response.json()["result"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_get_products_ok(test_client, test_session):
    response = await test_client.get("/products")
    assert response.status_code == 200
    assert response.json()["result"] is True
    assert response.json()["products"][0]["id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_product_by_id_ok(test_client, test_session):
    response = await test_client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["result"] is True
    assert response.json()["product"]["id"] == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_product_by_id_fail(test_client, test_session):
    response = await test_client.get("/products/8")
    assert response.status_code == 404
    assert response.json()["result"] is False
    response = await test_client.get("/products/test")
    assert response.status_code == 422
    assert response.json()["result"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_edit_product_by_id_ok(test_client, test_session):
    product = await Product.get_product_by_id(session=test_session, id=1)
    assert product.amount != 8
    response = await test_client.put("/products/1", json={"amount": 8})
    assert response.status_code == 200
    assert response.json()["result"] is True
    assert response.json()["product"]["amount"] == 8
    test_session.expire(product)
    product = await Product.get_product_by_id(session=test_session, id=1)
    assert product.amount == 8


@pytest.mark.asyncio(loop_scope="session")
async def test_edit_product_by_id_fail(test_client, test_session):
    response = await test_client.put("/products/8", json={"amount": 8})
    assert response.status_code == 404
    assert response.json()["result"] is False
    response = await test_client.put("/products/1", json={"test": 8})
    assert response.status_code == 422
    assert response.json()["result"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_product_by_id_ok(test_client, test_session):
    response = await test_client.post(
        "/products",
        json={"name": "E92", "description": "335D", "price": 20000, "amount": 1},
    )
    new_product_id = response.json()["product_id"]
    products = (await test_session.execute(select(Product))).scalars().all()
    products_ids = [product.id for product in products]
    assert new_product_id in products_ids
    response = await test_client.delete(f"/products/{new_product_id}")
    assert response.status_code == 200
    assert response.json()["result"] is True
    products = (await test_session.execute(select(Product))).scalars().all()
    products_ids = [product.id for product in products]
    assert new_product_id not in products_ids


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_product_by_id_fail(test_client, test_session):
    response = await test_client.delete("/products/8")
    assert response.status_code == 404
    assert response.json()["result"] is False
    response = await test_client.delete("/products/test")
    assert response.status_code == 422
    assert response.json()["result"] is False
