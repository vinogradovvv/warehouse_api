from fastapi import status
from starlette.exceptions import HTTPException


class WarehouseException(HTTPException):
    """Custom exception"""

    def __init__(self):
        self.result = False
        self.status_code = None
        self.error_type = None
        self.error_message = None


class ProductExistsException(WarehouseException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.error_type = "Product already exists."
        self.error_message = (
            "Product with given name and price already exists in the database."
        )


class NoProductException(WarehouseException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_type = "Product not found."
        self.error_message = "There is no such product in the database."


class ProductUpdateException(WarehouseException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.error_type = "No parameters."
        self.error_message = "Please provide at least one parameter to update."


class ProductAmountException(WarehouseException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.error_type = "Not enough product."
        self.error_message = "There is not enough product on the warehouse."


class NoOrderException(WarehouseException):
    def __init__(self):
        super().__init__()
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_type = "Order not found."
        self.error_message = "There is no such order in the database."
