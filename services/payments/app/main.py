from datetime import datetime

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from common.database import Base, build_database, get_session_factory
from common.health import add_database_readiness, router as health_router

engine, SessionLocal = build_database("payments_db")
get_db = get_session_factory(SessionLocal)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="authorized")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PaymentInput(BaseModel):
    order_id: int = Field(gt=0)
    amount: float = Field(gt=0)


app = FastAPI(title="AI Shop - Demo Payments", version="1.0.0")
app.include_router(health_router)
add_database_readiness(app, engine)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/api/payments", status_code=201)
def create_demo_payment(payload: PaymentInput, db: Session = Depends(get_db)):
    payment = Payment(
        order_id=payload.order_id,
        amount=payload.amount,
        status="authorized",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": payment.status,
        "created_at": payment.created_at,
        "mode": "demo",
    }


@app.get("/api/payments/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "id": payment.id,
        "order_id": payment.order_id,
        "amount": payment.amount,
        "status": payment.status,
        "created_at": payment.created_at,
        "mode": "demo",
    }
