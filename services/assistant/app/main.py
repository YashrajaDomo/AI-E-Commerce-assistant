import os
import re
import logging
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, HTTPException
from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from common.health import router as health_router

logger = logging.getLogger(__name__)
CATALOG_URL = os.getenv("CATALOG_URL", "http://catalog:8000")
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "ai_assistant")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

mongo_client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=3000)
chat_history = mongo_client[MONGO_DATABASE]["conversations"]


class ChatInput(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


def parse_intent(message: str) -> tuple[str | None, int | None, str]:
    lowered = message.lower()
    category_map = {
        "laptop": "Laptops",
        "headphone": "Audio",
        "earbud": "Audio",
        "speaker": "Audio",
        "phone": "Mobile Phones",
        "mobile": "Mobile Phones",
        "mouse": "Accessories",
        "keyboard": "Accessories",
        "shoe": "Fashion",
        "sneaker": "Fashion",
    }
    category = next((value for key, value in category_map.items() if key in lowered), None)

    max_price = None
    price_match = re.search(r"(?:under|below|less than|upto|up to)\s*(?:₹|rs\.?\s*)?([\d,]+)", lowered)
    if price_match:
        max_price = int(price_match.group(1).replace(",", ""))

    stop_words = {
        "i", "need", "want", "show", "me", "find", "some", "a", "an", "the",
        "for", "under", "below", "less", "than", "upto", "up", "to", "with",
        "good", "best", "please", "recommend", "cheapest", "cheap", "lowest",
        "price", "prices", "highly", "rated", "rating", "top", "compare",
        "and", "vs", "versus",
    }
    keywords = " ".join(
        word for word in re.findall(r"[a-z0-9]+", lowered)
        if word not in stop_words and not word.isdigit()
    )
    if category:
        category_words = category.lower().split()
        keywords = " ".join(word for word in keywords.split() if word not in category_words)
    return category, max_price, keywords


def find_products(message: str) -> list[dict]:
    category, max_price, keywords = parse_intent(message)
    params: dict[str, str | int] = {}
    if category:
        params["category"] = category
    if max_price is not None:
        params["max_price"] = max_price
    if "highly rated" in message.lower() or "top rated" in message.lower():
        params["min_rating"] = 4.5
    if keywords:
        params["q"] = keywords

    try:
        response = requests.get(f"{CATALOG_URL}/api/products", params=params, timeout=5)
        response.raise_for_status()
        products = response.json()
        if not products and "q" in params:
            params.pop("q")
            response = requests.get(f"{CATALOG_URL}/api/products", params=params, timeout=5)
            response.raise_for_status()
            products = response.json()
        lowered = message.lower()
        if "cheapest" in lowered or "lowest price" in lowered:
            products.sort(key=lambda product: product["price"])
        elif "highly rated" in lowered or "top rated" in lowered:
            products.sort(key=lambda product: (-product["rating"], product["price"]))
        return products[:3]
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Product catalog is unavailable") from error


def fallback_response(products: list[dict]) -> str:
    if not products:
        return "I couldn't find products matching that request. Try another category or budget."
    names = ", ".join(product["name"] for product in products)
    return f"Here are some products that match your request: {names}."


def compare_products(message: str) -> tuple[str, list[dict]] | None:
    if "compare" not in message.lower() or " and " not in message.lower():
        return None

    names = message.lower().split("compare", 1)[1].split(" and ", 1)
    if len(names) != 2:
        return None

    products = []
    try:
        for name in names:
            response = requests.get(
                f"{CATALOG_URL}/api/products",
                params={"q": name.strip()},
                timeout=5,
            )
            response.raise_for_status()
            matches = response.json()
            if matches:
                products.append(matches[0])
    except requests.RequestException as error:
        raise HTTPException(status_code=502, detail="Product catalog is unavailable") from error

    if len(products) != 2:
        return None

    cheaper = min(products, key=lambda product: product["price"])
    higher_rated = max(products, key=lambda product: product["rating"])
    summary = (
        f"{cheaper['name']} is cheaper, while {higher_rated['name']} has the higher rating. "
        f"{products[0]['name']} costs ₹{products[0]['price']} and is rated {products[0]['rating']}; "
        f"{products[1]['name']} costs ₹{products[1]['price']} and is rated {products[1]['rating']}."
    )
    return summary, products


def generate_response(message: str, products: list[dict]) -> str:
    if not OPENAI_API_KEY or not products:
        return fallback_response(products)
    try:
        completion = OpenAI(api_key=OPENAI_API_KEY, timeout=12).chat.completions.create(
            model=AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Recommend only from the provided catalog. Do not invent prices, "
                        "ratings, stock, specifications, or discounts. If a fact is missing, "
                        "say you do not have that information."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Customer request: {message}\nCatalog products: {products}",
                },
            ],
            temperature=0.2,
        )
        return completion.choices[0].message.content or fallback_response(products)
    except OpenAIError:
        logger.warning("AI provider request failed; returning catalog-based fallback response")
        return fallback_response(products)


app = FastAPI(title="AI Shop - Assistant", version="1.0.0")
app.include_router(health_router)


@app.on_event("startup")
def startup() -> None:
    mongo_client.admin.command("ping")
    chat_history.create_index("created_at")


@app.get("/ready", tags=["health"])
def readiness() -> dict[str, str]:
    try:
        mongo_client.admin.command("ping")
    except PyMongoError as error:
        raise HTTPException(status_code=503, detail="Conversation database is unavailable") from error
    return {"status": "ready"}


@app.on_event("shutdown")
def shutdown() -> None:
    mongo_client.close()


@app.post("/api/chat")
def chat(payload: ChatInput):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    comparison = compare_products(message)
    if comparison:
        response_text, products = comparison
    else:
        products = find_products(message)
        response_text = generate_response(message, products)
    chat_history.insert_one(
        {
            "message": message,
            "response": response_text,
            "product_ids": [product["id"] for product in products],
            "created_at": datetime.now(timezone.utc),
        }
    )
    return {"message": response_text, "products": products}
