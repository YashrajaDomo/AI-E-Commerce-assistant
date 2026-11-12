import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ecommerce.db")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_product_listing():
    response = client.get("/api/products")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) > 0
    assert "name" in payload[0]


def test_product_search():
    response = client.get("/api/products/search?q=laptop")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) > 0
    assert any("Laptop" in product["name"] or "Laptop" in product["category"] for product in payload)


def test_product_filtering():
    response = client.get("/api/products/filter?category=Laptops&max_price=70000")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) > 0
    assert all(product["category"] == "Laptops" for product in payload)


def test_product_details():
    response = client.get("/api/products/1")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1


def test_cart_lifecycle():
    add_response = client.post("/api/cart", json={"product_id": 1, "quantity": 2})
    assert add_response.status_code == 200
    item = add_response.json()
    assert item["quantity"] == 2

    cart_response = client.get("/api/cart")
    assert cart_response.status_code == 200
    assert cart_response.json()["total"] > 0

    delete_response = client.delete(f"/api/cart/{item['id']}")
    assert delete_response.status_code == 200


def test_chat_fallback_mode():
    response = client.post("/api/chat", json={"message": "Show me laptops under 50000"})
    assert response.status_code == 200
    payload = response.json()
    assert "laptops" in payload["message"].lower() or len(payload["products"]) > 0
