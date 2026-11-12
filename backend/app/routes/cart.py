from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.repositories.cart_repository import add_item, get_cart_items, remove_item, update_item
from app.repositories.product_repository import get_product_by_id
from app.schemas.cart import CartItemCreate, CartItemRead, CartItemUpdate, CartSummary

router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("", response_model=CartSummary)
def get_cart(db: Session = Depends(get_db)):
    items = get_cart_items(db)
    total = sum((item.product.price * item.quantity) for item in items)
    return {
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "created_at": item.created_at,
                "product_name": item.product.name,
                "product_price": item.product.price,
                "product_image": item.product.image_url,
            }
            for item in items
        ],
        "total": total,
    }


@router.post("", response_model=CartItemRead)
def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db)):
    product = get_product_by_id(db, item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_item = add_item(db, item.product_id, quantity=item.quantity)
    return {
        "id": new_item.id,
        "product_id": new_item.product_id,
        "quantity": new_item.quantity,
        "created_at": new_item.created_at,
        "product_name": product.name,
        "product_price": product.price,
        "product_image": product.image_url,
    }


@router.put("/{item_id}", response_model=CartItemRead)
def update_cart_item(item_id: int, item: CartItemUpdate, db: Session = Depends(get_db)):
    updated = update_item(db, item_id, item.quantity)
    if not updated:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {
        "id": updated.id,
        "product_id": updated.product_id,
        "quantity": updated.quantity,
        "created_at": updated.created_at,
        "product_name": updated.product.name,
        "product_price": updated.product.price,
        "product_image": updated.product.image_url,
    }


@router.delete("/{item_id}")
def delete_cart_item(item_id: int, db: Session = Depends(get_db)):
    removed = remove_item(db, item_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Cart item removed"}
