import pytest
from sqlalchemy.future import select

from app.db.db_models import Order


@pytest.mark.asyncio(loop_scope="session")
async def test_add_order_ok(test_client, test_session):
    orders_number = len((await test_session.execute(select(Order))).scalars().all())
    response = await test_client.post(
        "/orders", json=[{"product_id": 1, "product_amount": 1}]
    )
    assert response.status_code == 201
    assert response.json()["result"] is True
    new_orders_number = len((await test_session.execute(select(Order))).scalars().all())
    assert new_orders_number - orders_number == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_add_order_fail(test_client, test_session):
    response = await test_client.post(
        "/orders", json=[{"product_id": 8, "product_amount": 1}]
    )
    assert response.status_code == 404
    assert response.json()["result"] is False

    response = await test_client.post(
        "/orders", json=[{"product_id": 1, "product_amount": 100}]
    )
    assert response.status_code == 422
    assert response.json()["result"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_get_orders_ok(test_client, test_session):
    response = await test_client.get("/orders")
    assert response.status_code == 200
    assert response.json()["result"] is True
    assert response.json()["orders"][0]["id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_by_id_ok(test_client, test_session):
    response = await test_client.get("/orders/1")
    assert response.status_code == 200
    assert response.json()["result"] is True
    assert response.json()["order"]["id"] == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_order_by_id_fail(test_client, test_session):
    response = await test_client.get("/orders/8")
    assert response.status_code == 404
    assert response.json()["result"] is False
    response = await test_client.get("/orders/test")
    assert response.status_code == 422
    assert response.json()["result"] is False


@pytest.mark.asyncio(loop_scope="session")
async def test_change_order_status_by_id_ok(test_client, test_session):
    order = await Order.get_order_by_id(session=test_session, id=1)
    order_status = order.status
    new_status = "sent"
    response = await test_client.patch("/orders/1/status", json=new_status)
    assert response.status_code == 200
    assert response.json()["result"] is True
    test_session.expire(order)
    order = await Order.get_order_by_id(session=test_session, id=1)
    assert order.status == new_status
    assert order_status != new_status


@pytest.mark.asyncio(loop_scope="session")
async def test_change_order_status_by_id_fail(test_client, test_session):
    response = await test_client.patch("/orders/8/status", json="sent")
    assert response.status_code == 404
    assert response.json()["result"] is False
    response = await test_client.patch("/orders/1/status", json="test")
    assert response.status_code == 422
    assert response.json()["result"] is False
