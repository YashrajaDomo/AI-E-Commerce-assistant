from typing import Iterable

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.product import Product


def get_all_products(
    db: Session,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    query: str | None = None,
):
    products = db.query(Product)

    if category:
        products = products.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        products = products.filter(Product.price >= min_price)
    if max_price is not None:
        products = products.filter(Product.price <= max_price)
    if min_rating is not None:
        products = products.filter(Product.rating >= min_rating)
    if query:
        text = f"%{query}%"
        products = products.filter(
            or_(
                Product.name.ilike(text),
                Product.description.ilike(text),
                Product.category.ilike(text),
            )
        )

    return products.order_by(Product.rating.desc(), Product.price.asc()).all()


def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_name(db: Session, product_name: str):
    return db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()


def get_products_by_ids(db: Session, product_ids: Iterable[int]):
    return db.query(Product).filter(Product.id.in_(list(product_ids))).all()
