from typing import Iterable

from app.models.product import Product


def normalize_text(value: str) -> str:
    return value.lower().strip()


def score_product_match(query: str, product: Product) -> int:
    if not query:
        return 0

    normalized_query = normalize_text(query)
    score = 0
    search_fields = [
        product.name,
        product.category,
        product.description,
    ]

    for field in search_fields:
        lowered_field = normalize_text(field)
        if normalized_query in lowered_field:
            if field == product.name:
                score += 3
            elif field == product.category:
                score += 2
            else:
                score += 1

    for keyword in normalized_query.split():
        if not keyword:
            continue
        if keyword in normalize_text(product.name):
            score += 1
        if keyword in normalize_text(product.category):
            score += 1
        if keyword in normalize_text(product.description):
            score += 1

    return score


def extract_price_keywords(text: str) -> tuple[int | None, int | None, list[str]]:
    normalized = text.lower()
    max_price = None
    min_price = None
    numbers = []

    for value in normalized.split():
        if value.isdigit():
            numbers.append(int(value))

    if "under" in normalized or "below" in normalized:
        for keyword in ["under", "below"]:
            index = normalized.find(keyword)
            if index != -1:
                remainder = normalized[index + len(keyword):]
                match = __import__("re").search(r"\d+", remainder)
                if match:
                    max_price = int(match.group())
                    break

    if "above" in normalized or "over" in normalized or "more than" in normalized:
        for keyword in ["above", "over", "more than"]:
            index = normalized.find(keyword)
            if index != -1:
                remainder = normalized[index + len(keyword):]
                match = __import__("re").search(r"\d+", remainder)
                if match:
                    min_price = int(match.group())
                    break

    keywords = [
        word for word in normalized.replace("?", " ").split() if word.isalpha() and word not in {"i", "a", "for", "under", "below", "over", "above", "show", "me", "need", "find", "the"}
    ]

    return min_price, max_price, keywords


def get_category_from_text(text: str) -> str | None:
    normalized = text.lower()
    categories = {
        "laptop": "Laptops",
        "laptops": "Laptops",
        "phone": "Mobile Phones",
        "phones": "Mobile Phones",
        "mobile": "Mobile Phones",
        "headphone": "Audio",
        "headphones": "Audio",
        "earbuds": "Audio",
        "speaker": "Audio",
        "mouse": "Accessories",
        "keyboard": "Accessories",
        "shoes": "Fashion",
        "sneakers": "Fashion",
        "running shoes": "Fashion",
    }

    for keyword, category in categories.items():
        if keyword in normalized:
            return category
    return None
