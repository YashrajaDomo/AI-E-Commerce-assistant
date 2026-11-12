import re
from typing import Any

from app.config import settings
from app.repositories.product_repository import get_all_products
from app.services.recommendation_service import recommend_products
from app.utils.search_utils import extract_price_keywords, get_category_from_text

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


def parse_user_query(message: str) -> dict[str, Any]:
    lower_message = message.lower()
    category = get_category_from_text(lower_message)
    min_price, max_price, keywords = extract_price_keywords(lower_message)

    normalized_keywords = []
    for token in keywords:
        if token not in {"laptop", "laptops", "headphone", "headphones", "phone", "phones", "mobile", "gaming", "programming", "student"}:
            normalized_keywords.append(token)

    return {
        "category": category,
        "min_price": min_price,
        "max_price": max_price,
        "keywords": normalized_keywords,
        "text": message,
    }


def generate_product_response(message: str, products: list) -> str:
    if not products:
        return "I couldn't find any products matching that request. Try a different category or price range."

    if len(products) == 1:
        product = products[0]
        return f"Here is a product that matches your request: {product.name} at ₹{product.price}."

    product_names = ", ".join(product.name for product in products[:3])
    return f"Here are some matches: {product_names}."


def compare_products(products: list) -> str:
    if len(products) < 2:
        return "I need at least two products to compare them."

    first, second = products[:2]
    if first.price < second.price:
        cheaper = first.name
        more_expensive = second.name
    else:
        cheaper = second.name
        more_expensive = first.name

    if first.rating >= second.rating:
        higher_rating = first.name
    else:
        higher_rating = second.name

    return (
        f"{cheaper} is cheaper, while {higher_rating} has the higher rating. "
        f"{more_expensive} may be a better choice if you value premium features."
    )


def generate_recommendation(message: str, products: list) -> list:
    parsed = parse_user_query(message)
    keywords = " ".join(parsed["keywords"]) or message
    return recommend_products(products, keywords)


def get_openai_response(message: str) -> str | None:
    if not settings.OPENAI_API_KEY or OpenAI is None:
        return None

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        completion = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful shopping assistant. Use only facts provided by the product list and do not invent prices, ratings, or specifications."},
                {"role": "user", "content": message},
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content
    except Exception:
        return None
