from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator
from starlette.exceptions import HTTPException


def validate_positive_value(val: int):
    if val <= 0:
        raise HTTPException(422, "Value must be greater than 0.")
    return val


class Response(BaseModel):
    result: bool


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    amount: int


class CreateProductResponse(Response):
    product_id: int


class ProductsResponse(Response):
    model_config = ConfigDict(from_attributes=True)
    products: List[Product]


class ProductResponse(Response):
    model_config = ConfigDict(from_attributes=True)
    product: Product


class UpdateProduct(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    amount: Optional[int] = None

    _validate_price = field_validator("price")(validate_positive_value)
    _validate_amount = field_validator("amount")(validate_positive_value)


class Statuses(Enum):
    processing = "processing"
    sent = "sent"
    delivered = "delivered"


class OrderProduct(BaseModel):
    id: int
    name: str
    description: str
    price: float


class OrderItem(BaseModel):
    id: int
    amount: int
    product: OrderProduct


class Order(BaseModel):
    id: int
    create_date: datetime
    status: Statuses
    order_products: List[OrderItem]


class CreateOrderResponse(Response):
    order_id: int


class OrdersResponse(Response):
    model_config = ConfigDict(from_attributes=True)
    orders: List[Order]


class OrderResponse(Response):
    model_config = ConfigDict(from_attributes=True)
    order: Order


class OrderRequestItem(BaseModel):
    product_id: int
    product_amount: int

    _validate_product_id = field_validator("product_id")(validate_positive_value)
    _validate_product_amount = field_validator("product_amount")(
        validate_positive_value
    )


class FailResponse(BaseModel):
    result: bool
    error_type: str
    error_message: str
