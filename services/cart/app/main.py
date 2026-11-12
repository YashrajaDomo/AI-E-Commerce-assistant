import os
from datetime import datetime

import requests
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, Session, mapped_column

from common.database import Base, build_database, get_session_factory
from common.health import add_database_readiness, router as health_router

engine, SessionLocal = build_database("cart_db")
get_db = get_session_factory(SessionLocal)
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8000")


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CartItemInput(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class QuantityInput(BaseModel):
    quantity: int = Field(ge=1)


def get_product(product_id: int) -> dict:
    try:
        response = requests.get(f"{CATALOG_URL}/api/products/{product_id}", timeout=5)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="Product not found")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Product catalog is unavailable") from error


def serialize(item: CartItem) -> dict:
    product = get_product(item.product_id)
    return {
        "id": item.id,
        "product_id": item.product_id,
        "quantity": item.quantity,
        "created_at": item.created_at,
        "product_name": product["name"],
        "product_price": product["price"],
        "product_image": product.get("image_url"),
    }


app = FastAPI(title="AI Shop - Cart", version="1.0.0")
app.include_router(health_router)
add_database_readiness(app, engine)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/api/cart")
def get_cart(db: Session = Depends(get_db)):
    items = db.query(CartItem).order_by(CartItem.created_at.desc()).all()
    result = [serialize(item) for item in items]
    return {
        "items": result,
        "total": round(sum(item["product_price"] * item["quantity"] for item in result), 2),
    }


@app.post("/api/cart")
def add_to_cart(payload: CartItemInput, db: Session = Depends(get_db)):
    get_product(payload.product_id)
    item = db.query(CartItem).filter(CartItem.product_id == payload.product_id).first()
    if item:
        item.quantity += payload.quantity
    else:
        item = CartItem(product_id=payload.product_id, quantity=payload.quantity)
        db.add(item)
    db.commit()
    db.refresh(item)
    return serialize(item)


@app.put("/api/cart/{item_id}")
def update_cart_item(item_id: int, payload: QuantityInput, db: Session = Depends(get_db)):
    item = db.get(CartItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = payload.quantity
    db.commit()
    db.refresh(item)
    return serialize(item)


@app.delete("/api/cart/{item_id}")
def delete_cart_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(CartItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return {"message": "Cart item removed"}
