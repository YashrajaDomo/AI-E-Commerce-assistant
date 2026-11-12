import os
from datetime import datetime

import requests
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from common.database import Base, build_database, get_session_factory
from common.health import add_database_readiness, router as health_router

engine, SessionLocal = build_database("orders_db")
get_db = get_session_factory(SessionLocal)
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8000")
PAYMENTS_URL = os.getenv("PAYMENTS_URL", "http://payments:8000")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    total: Mapped[float] = mapped_column(Float, nullable=False)
    payment_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    items: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OrderLineInput(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1, le=99)


class OrderInput(BaseModel):
    items: list[OrderLineInput] = Field(min_length=1)


def get_catalog_product(product_id: int) -> dict:
    try:
        response = requests.get(f"{CATALOG_URL}/api/products/{product_id}", timeout=5)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Product catalog is unavailable") from error


def serialize(order: Order) -> dict:
    return {
        "id": order.id,
        "status": order.status,
        "total": order.total,
        "payment_id": order.payment_id,
        "items": order.items,
        "created_at": order.created_at,
    }


app = FastAPI(title="AI Shop - Orders", version="1.0.0")
app.include_router(health_router)
add_database_readiness(app, engine)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/api/orders", status_code=201)
def create_order(payload: OrderInput, db: Session = Depends(get_db)):
    order_items = []
    for line in payload.items:
        product = get_catalog_product(line.product_id)
        if product["stock"] < line.quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Insufficient stock for {product['name']}",
            )
        order_items.append(
            {
                "product_id": product["id"],
                "name": product["name"],
                "unit_price": product["price"],
                "quantity": line.quantity,
            }
        )

    total = round(
        sum(item["unit_price"] * item["quantity"] for item in order_items),
        2,
    )
    order = Order(status="payment_pending", total=total, items=order_items)
    db.add(order)
    db.commit()
    db.refresh(order)

    try:
        response = requests.post(
            f"{PAYMENTS_URL}/api/payments",
            json={"order_id": order.id, "amount": total},
            timeout=10,
        )
        response.raise_for_status()
        payment = response.json()
    except requests.RequestException as error:
        order.status = "payment_failed"
        db.commit()
        raise HTTPException(status_code=502, detail="Demo payment service is unavailable") from error

    order.payment_id = payment["id"]
    order.status = "confirmed" if payment["status"] == "authorized" else "payment_failed"
    db.commit()
    db.refresh(order)
    return {**serialize(order), "payment": payment}


@app.get("/api/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize(order)
