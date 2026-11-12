from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.product_repository import get_all_products, get_product_by_id
from app.schemas.product import ProductRead
from app.services.search_service import search_products

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductRead])
def list_products(
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    min_rating: float | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if q:
        items = search_products(
            db,
            query=q,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
        )
        return items
    return get_all_products(
        db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        query=None,
    )


@router.get("/search", response_model=list[ProductRead])
def search_products_route(
    q: str = Query(..., min_length=1),
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    min_rating: float | None = Query(default=None),
    db: Session = Depends(get_db),
):
    items = search_products(
        db,
        query=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
    )
    return items


@router.get("/filter", response_model=list[ProductRead])
def filter_products(
    category: str | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    min_rating: float | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_all_products(
        db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        query=None,
    )


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
