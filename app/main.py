from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db import db_models
from app.db.database import engine
from app.routes import orders, products


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # await conn.run_sync(db_models.Base.metadata.drop_all)
        await conn.run_sync(db_models.Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="Warehouse_API",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exception):
    print(exception.errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": exception.errors()[0]["type"],
                "error_message": exception.errors()[0]["msg"],
            }
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exception):
    if "result" in exception.__dict__:
        return JSONResponse(
            status_code=exception.status_code,
            content=jsonable_encoder(
                {
                    "result": exception.result,
                    "error_type": exception.error_type,
                    "error_message": exception.error_message,
                }
            ),
        )
    return JSONResponse(
        status_code=exception.status_code,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": exception.detail,
                "error_message": exception.detail,
            }
        ),
    )


app.include_router(products.router)
app.include_router(orders.router)
