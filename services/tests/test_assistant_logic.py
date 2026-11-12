import sys
from pathlib import Path
from unittest.mock import Mock

SERVICES_ROOT = Path(__file__).resolve().parents[1]
ASSISTANT_ROOT = SERVICES_ROOT / "assistant"
sys.path.insert(0, str(SERVICES_ROOT))
sys.path.insert(0, str(ASSISTANT_ROOT))

from app.main import compare_products, fallback_response, parse_intent


def test_parse_category_price_and_query_terms():
    category, max_price, keywords = parse_intent(
        "I need a laptop under ₹70,000 for programming"
    )

    assert category == "Laptops"
    assert max_price == 70000
    assert "programming" in keywords


def test_compare_uses_only_catalog_facts(monkeypatch):
    products = {
        "hp pavilion": {
            "id": 4,
            "name": "HP Pavilion Laptop",
            "price": 65999,
            "rating": 4.4,
        },
        "dell inspiron": {
            "id": 5,
            "name": "Dell Inspiron Laptop",
            "price": 58999,
            "rating": 4.3,
        },
    }

    def fake_get(_url, params, timeout):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = [products[params["q"]]]
        return response

    monkeypatch.setattr("app.main.requests.get", fake_get)
    comparison = compare_products("Compare HP Pavilion and Dell Inspiron")

    assert comparison is not None
    message, matches = comparison
    assert "Dell Inspiron Laptop is cheaper" in message
    assert "HP Pavilion Laptop has the higher rating" in message
    assert [product["id"] for product in matches] == [4, 5]


def test_fallback_is_clear_when_no_products_match():
    assert "couldn't find" in fallback_response([]).lower()
