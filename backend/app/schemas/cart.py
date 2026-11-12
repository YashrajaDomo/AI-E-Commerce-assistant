from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    created_at: datetime
    product_name: str | None = None
    product_price: float | None = None
    product_image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CartSummary(BaseModel):
    items: list[CartItemRead]
    total: float
