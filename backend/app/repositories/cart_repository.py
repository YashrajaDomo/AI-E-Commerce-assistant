from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.product import Product


def get_cart_items(db: Session):
    return (
        db.query(CartItem)
        .join(Product, Product.id == CartItem.product_id)
        .order_by(CartItem.created_at.desc())
        .all()
    )


def add_item(db: Session, product_id: int, quantity: int = 1):
    item = db.query(CartItem).filter(CartItem.product_id == product_id).first()
    if item:
        item.quantity += quantity
        db.commit()
        db.refresh(item)
        return item

    item = CartItem(product_id=product_id, quantity=quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_item(db: Session, item_id: int, quantity: int):
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        return None
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def remove_item(db: Session, item_id: int):
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
