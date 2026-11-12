from sqlalchemy.orm import Session

from app.repositories.product_repository import get_all_products
from app.utils.search_utils import score_product_match


def search_products(
    db: Session,
    query: str,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
):
    products = get_all_products(
        db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        query=query,
    )

    scored = []
    for product in products:
        score = score_product_match(query, product)
        if score > 0:
            scored.append((product, score))

    if not scored:
        return []

    scored.sort(key=lambda item: (-item[1], -item[0].rating, item[0].price))
    return [product for product, _ in scored]
