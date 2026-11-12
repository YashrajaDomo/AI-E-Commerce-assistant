import re
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Float, Integer, String, or_
from sqlalchemy.orm import Mapped, Session, mapped_column

from common.database import Base, build_database, get_session_factory
from common.health import add_database_readiness, router as health_router

engine, SessionLocal = build_database("catalog_db")
get_db = get_session_factory(SessionLocal)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    category: str
    price: float
    rating: float
    stock: int
    image_url: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


PRODUCTS = [
    ("Apple iPhone 15", "Premium smartphone with a vibrant OLED display and advanced camera.", "Mobile Phones", 79999, 4.8, 25),
    ("Samsung Galaxy S24", "Android smartphone designed for productivity, photos, and daily use.", "Mobile Phones", 74999, 4.7, 18),
    ("OnePlus 12", "Fast smartphone with a smooth display and premium performance.", "Mobile Phones", 69999, 4.6, 22),
    ("HP Pavilion Laptop", "Balanced laptop for work, study, and light creative tasks.", "Laptops", 65999, 4.4, 15),
    ("Dell Inspiron Laptop", "Reliable laptop built for everyday productivity and study.", "Laptops", 58999, 4.3, 20),
    ("Lenovo IdeaPad Laptop", "Affordable laptop for home use, study, and office tasks.", "Laptops", 48999, 4.2, 28),
    ("Sony WH-1000XM5", "Wireless headphones with active noise cancellation and comfortable design.", "Audio", 29999, 4.9, 26),
    ("Boat Rockerz Headphones", "Budget wireless headphones with solid sound and long battery life.", "Audio", 3999, 4.1, 40),
    ("Logitech Wireless Mouse", "Ergonomic wireless mouse for smooth all-day use.", "Accessories", 1999, 4.4, 60),
    ("Mechanical Keyboard", "Tactile keyboard for gamers and professionals.", "Accessories", 6999, 4.6, 35),
    ("Nike Running Shoes", "Comfortable running shoes with responsive cushioning.", "Fashion", 5999, 4.5, 32),
    ("Adidas Sneakers", "Versatile sneakers for casual style, walking, and light exercise.", "Fashion", 4999, 4.3, 38),
    ("ASUS Gaming Laptop", "Gaming laptop with a fast display and dedicated graphics.", "Laptops", 89999, 4.8, 12),
    ("Acer Predator Laptop", "High-performance gaming laptop for demanding games.", "Laptops", 96999, 4.7, 10),
    ("JBL Flip 6", "Portable Bluetooth speaker with deep bass and rugged design.", "Audio", 12999, 4.5, 33),
    ("Apple AirPods Pro", "Wireless earbuds with active noise cancellation.", "Audio", 24999, 4.8, 30),
    ("Dell USB-C Dock", "Docking station for monitors, accessories, and external devices.", "Accessories", 8999, 4.2, 45),
    ("Premium Office Chair", "Comfort-focused chair designed for long work hours.", "Accessories", 14999, 4.4, 14),
    ("Puma Running Shoes", "Lightweight sneakers for city walking and exercise.", "Fashion", 5299, 4.3, 41),
    ("Noise Cancelling Earbuds", "Compact wireless earbuds for daily commuting.", "Audio", 4999, 4.1, 58),
    ("Realme Narzo 70", "Affordable smartphone with a bright display and smooth performance.", "Mobile Phones", 17999, 4.2, 48),
]


def seed_products() -> None:
    with SessionLocal() as db:
        if db.query(Product).first():
            return
        for name, description, category, price, rating, stock in PRODUCTS:
            db.add(Product(
                name=name,
                description=description,
                category=category,
                price=price,
                rating=rating,
                stock=stock,
                image_url=None,
            ))
        db.commit()


app = FastAPI(title="AI Shop - Product Catalog", version="1.0.0")
app.include_router(health_router)
add_database_readiness(app, engine)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    seed_products()


@app.get("/api/products", response_model=list[ProductRead])
def list_products(
    q: str | None = None,
    category: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)
    products = query.all()

    if q:
        terms = re.findall(r"[a-z0-9]+", q.lower())

        def score(product: Product) -> int:
            name, category_text, description = (
                product.name.lower(),
                product.category.lower(),
                product.description.lower(),
            )
            return (
                (3 if q.lower() in name else 0)
                + (2 if q.lower() in category_text else 0)
                + (1 if q.lower() in description else 0)
                + sum(
                    3 * (term in name) + 2 * (term in category_text) + (term in description)
                    for term in terms
                )
            )

        products = [product for product in products if score(product) > 0]
        products.sort(key=lambda product: (-score(product), -product.rating, product.price))
    else:
        products.sort(key=lambda product: (-product.rating, product.price))
    return products


@app.get("/api/products/search", response_model=list[ProductRead])
def search_products(
    q: str = Query(min_length=1),
    category: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    return list_products(
        q=q,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        db=db,
    )


@app.get("/api/products/filter", response_model=list[ProductRead])
def filter_products(
    category: str | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    return list_products(
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        db=db,
    )


@app.get("/api/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
