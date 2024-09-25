from datetime import datetime
from typing import Any

from sqlalchemy import (
    DECIMAL,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, selectinload

from .database import Base


class Product(Base):
    """
    Products table
    """

    __tablename__ = "product"
    __table_args__ = (UniqueConstraint("name", "price"),)

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(12, 2), nullable=False)  # type: ignore
    amount = Column(Integer, default=0)
    orders = relationship('Order', secondary='order_item')

    @classmethod
    async def get_product_by_id(cls, session: AsyncSession, id: int) -> Any | None:
        """
        Returns product with given id or None.
        :param session: Asynchronous session (AsyncSession)
        :param id: product id (int)
        :return: Any | None
        """
        res = await session.execute(select(cls).filter(cls.id == id))
        return res.unique().scalar_one_or_none()


class Order(Base):
    """
    Orders table
    """

    __tablename__ = "order"

    id = Column(Integer, primary_key=True, nullable=False)
    create_date = Column(DateTime, default=datetime.now(), nullable=False)
    status = Column(String, default="processing", nullable=False)
    order_products = relationship("OrderItem", backref="order")
    products = relationship('Product', secondary='order_item')

    @classmethod
    async def get_order_by_id(cls, session: AsyncSession, id: int) -> Any | None:
        """
        Returns order with given id or None.
        :param session: Asynchronous session (AsyncSession)
        :param id: order id (int)
        :return: Any | None
        """
        res = await session.execute(
            select(cls).options(selectinload(cls.order_products)).filter(cls.id == id)
        )
        return res.unique().scalar_one_or_none()


class OrderItem(Base):
    """
    Order items table
    """

    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    product_id = Column(Integer, ForeignKey("product.id"))
    amount = Column(Integer, nullable=False)
    product = relationship("Product", lazy="joined")
