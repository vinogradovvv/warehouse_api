from typing import Annotated, Dict, Optional, Sequence

from fastapi import APIRouter, Body, Depends, Path, status
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app import schemas
from app.db.database import get_session
from app.db.db_models import Product
from app.exceptions import (
    NoProductException,
    ProductExistsException,
    ProductUpdateException,
)

router = APIRouter(
    prefix="/api/v1/products", tags=["products"], dependencies=[Depends(get_session)]
)


@router.post(
    "",
    response_model=schemas.CreateProductResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"model": schemas.FailResponse},
    },
)
async def add_product(
    name: Annotated[str, Body()],
    description: Annotated[Optional[str], Body()],
    price: Annotated[int | float, Body(gt=0)],
    amount: Annotated[int, Body(gt=0)],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | int]:
    """
    Endpoint to add new product.
    :param name: product name (str)
    :param description: product description (str)
    :param price: product price (int | float)
    :param amount: product amount (int)
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | int]
    """
    new_product = Product(
        **{
            "name": name,
            "price": price,
            "amount": amount,
        }
    )
    if description:
        new_product.description = description  # type: ignore
    session.add(new_product)
    try:
        await session.commit()
    except IntegrityError:
        raise ProductExistsException
    return {"result": True, "product_id": int(new_product.id)}


@router.get(
    "",
    response_model=schemas.ProductsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_products(
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | Sequence[Product]]:
    """
    Endpoint to get list of all products.
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | Sequence[Product]]
    """
    res = await session.execute(select(Product))
    products = res.scalars().all()
    return {"result": True, "products": products}


@router.get(
    "/{id}",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def get_product_by_id(
    id: Annotated[int, Path(gt=0)], session: AsyncSession = Depends(get_session)
) -> Dict[str, bool | str | Product]:
    """
    Endpoint to get product with given id.
    :param id: product id (int)
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | str | Product]
    """
    product = await Product.get_product_by_id(session=session, id=id)
    if not product:
        raise NoProductException
    return {"result": True, "product": product}


@router.put(
    "/{id}",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def edit_product(
    id: Annotated[int, Path(gt=0)],
    product_update: Annotated[schemas.UpdateProduct, Body()],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, bool | str | Product]:
    """
    Endpoint to edit product with given id.
    :param id: product id (int)
    :param product_update: Edited params (Dict)
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | str | Product]
    """
    product = await Product.get_product_by_id(session=session, id=id)
    if not product:
        raise NoProductException
    update_data = {
        k: v for k, v in product_update.model_dump().items() if v is not None
    }
    if len(update_data) == 0:
        raise ProductUpdateException
    await session.execute(
        update(Product).filter(Product.id == id).values(**update_data)
    )
    await session.commit()
    return {"result": True, "product": product}


@router.delete(
    "/{id}",
    response_model=schemas.Response,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": schemas.FailResponse},
        422: {"model": schemas.FailResponse},
    },
)
async def delete_product(
    id: Annotated[int, Path(gt=0)], session: AsyncSession = Depends(get_session)
) -> Dict[str, bool | str]:
    """
    Endpoint to delete product with given id.
    :param id: product id (int)
    :param session: Asynchronous session (AsyncSession)
    :return: Dict[str, bool | str]
    """
    product = await Product.get_product_by_id(session=session, id=id)
    if not product:
        raise NoProductException
    await session.delete(product)
    await session.commit()
    return {"result": True}
