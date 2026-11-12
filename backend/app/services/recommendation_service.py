from app.models.product import Product


def score_recommendation(product: Product, query: str) -> int:
    query_lower = query.lower()
    score = 0

    if product.category.lower() in query_lower:
        score += 5

    for keyword in query_lower.split():
        if not keyword:
            continue
        if keyword in product.name.lower():
            score += 3
        if keyword in product.description.lower():
            score += 2

    if product.rating >= 4:
        score += 2
    if product.stock > 0:
        score += 1
    if product.price < 20000:
        score += 1

    return score


def recommend_products(products: list[Product], query: str) -> list[Product]:
    scored = [(product, score_recommendation(product, query)) for product in products]
    scored.sort(key=lambda item: (-item[1], -item[0].rating, item[0].price))
    return [product for product, _ in scored]
