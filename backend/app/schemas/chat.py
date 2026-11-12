from pydantic import BaseModel

from app.schemas.product import ProductRead


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    products: list[ProductRead] = []
