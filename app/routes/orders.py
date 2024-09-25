from typing import Annotated, Dict, List, Literal, Sequence

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app import schemas
from app.db.database import get_session
from app.db.db_models import Order, OrderItem, Product
from app.exceptions import NoOrderException, NoProductException, ProductAmountException

router = APIRouter(
    prefix="/api/v1/orders", tags=["orders"], dependencies=[Depends(get_session)]
)


@router.post(
    "",
    response_model=schemas.CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def create_order(
    order_products: Annotated[List[schemas.OrderRequestItem], Body()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | int]:
    """
    Endpoint to create new order.
    :param order_products: Products id and amounts (List[Dict])
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | int]
    """
    new_order = Order()
    for item in order_products:
        product = await Product.get_product_by_id(session=session, id=item.product_id)
        if not product:
            raise NoProductException
        if product.amount < item.product_amount:
            raise ProductAmountException
        new_order.order_products.append(
            OrderItem(product=product, amount=item.product_amount)
        )
        product.amount -= item.product_amount

    session.add(new_order)
    await session.commit()
    return {"result": True, "order_id": int(new_order.id)}


@router.get(
    "",
    response_model=schemas.OrdersResponse,
    status_code=status.HTTP_200_OK,
)
async def get_orders(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | Sequence[Order]]:
    """
    Endpoint to get list of all orders.
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | Sequence[Order]]
    """
    res = await session.execute(
        select(Order).options(selectinload(Order.order_products))
    )
    orders = res.scalars().all()
    return {"result": True, "orders": orders}


@router.get(
    "/{id}",
    response_model=schemas.OrderResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def get_order_by_id(
    id: Annotated[int, Path(gt=0)], session: AsyncSession = Depends(get_session)
) -> Dict[str, bool | str | Order]:
    """
    Endpoint to get order with given id.
    :param id: order id (int)
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | str | Order]
    """
    order = await Order.get_order_by_id(session=session, id=id)
    if not order:
        raise NoOrderException
    return {"result": True, "order": order}


@router.patch(
    "/{id}/status",
    response_model=schemas.Response,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def change_order_status(
    id: Annotated[int, Path(gt=0)],
    status: Annotated[Literal["processing", "sent", "delivered"], Body()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | str]:
    """
    Endpoint to change status of order with given id.
    :param id: order id (int)
    :param status: order status (Literal['processing', 'sent', 'delivered'])
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | str]
    """
    order = await Order.get_order_by_id(session=session, id=id)
    if not order:
        raise NoOrderException
    order.status = status
    await session.commit()
    return {"result": True, "status": order.status}
