from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base
from app.models.product import Product

PRODUCTS = [
    {
        "name": "Apple iPhone 15",
        "description": "A high-end smartphone with a vibrant OLED display and excellent camera quality.",
        "category": "Mobile Phones",
        "price": 79999,
        "rating": 4.8,
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Samsung Galaxy S24",
        "description": "Feature-rich Android smartphone designed for productivity, camera work, and everyday use.",
        "category": "Mobile Phones",
        "price": 74999,
        "rating": 4.7,
        "stock": 18,
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "OnePlus 12",
        "description": "Fast performance and smooth display for users who want premium mobile features.",
        "category": "Mobile Phones",
        "price": 69999,
        "rating": 4.6,
        "stock": 22,
        "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "HP Pavilion Laptop",
        "description": "Balanced laptop for work, study, and light creative tasks with dependable performance.",
        "category": "Laptops",
        "price": 65999,
        "rating": 4.4,
        "stock": 15,
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Dell Inspiron Laptop",
        "description": "Reliable laptop built for everyday productivity and long study sessions.",
        "category": "Laptops",
        "price": 58999,
        "rating": 4.3,
        "stock": 20,
        "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Lenovo IdeaPad Laptop",
        "description": "Affordable and comfortable laptop for home usage and office tasks.",
        "category": "Laptops",
        "price": 48999,
        "rating": 4.2,
        "stock": 28,
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Sony WH-1000XM5",
        "description": "Upgraded wireless headphones with active noise cancellation and comfortable design.",
        "category": "Audio",
        "price": 29999,
        "rating": 4.9,
        "stock": 26,
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Boat Rockerz Headphones",
        "description": "Budget-friendly wireless headphones with solid sound and long battery life.",
        "category": "Audio",
        "price": 3999,
        "rating": 4.1,
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Logitech Wireless Mouse",
        "description": "Ergonomic mouse designed for smooth control and comfortable all-day use.",
        "category": "Accessories",
        "price": 1999,
        "rating": 4.4,
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Mechanical Keyboard",
        "description": "Tactile keyboard built for gamers and professionals who prefer satisfying key feedback.",
        "category": "Accessories",
        "price": 6999,
        "rating": 4.6,
        "stock": 35,
        "image_url": "https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Nike Running Shoes",
        "description": "Comfortable sneakers for daily jogging and active travel with responsive cushioning.",
        "category": "Fashion",
        "price": 5999,
        "rating": 4.5,
        "stock": 32,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Adidas Sneakers",
        "description": "Versatile sneakers made for casual style, walking, and light exercise.",
        "category": "Fashion",
        "price": 4999,
        "rating": 4.3,
        "stock": 38,
        "image_url": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "ASUS Gaming Laptop",
        "description": "Gaming laptop with a strong graphics card, fast refresh rate, and premium build quality.",
        "category": "Laptops",
        "price": 89999,
        "rating": 4.8,
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Acer Predator Laptop",
        "description": "High-performance gaming laptop for demanding games and multitasking workflows.",
        "category": "Laptops",
        "price": 96999,
        "rating": 4.7,
        "stock": 10,
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "JBL Flip 6",
        "description": "Portable Bluetooth speaker with deep bass and a rugged body for travel and outdoor use.",
        "category": "Audio",
        "price": 12999,
        "rating": 4.5,
        "stock": 33,
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Apple AirPods Pro",
        "description": "Premium wireless earbuds with active noise cancellation and reliable voice clarity.",
        "category": "Audio",
        "price": 24999,
        "rating": 4.8,
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Dell USB-C Dock",
        "description": "Useful docking station for connecting monitors, accessories, and external devices.",
        "category": "Accessories",
        "price": 8999,
        "rating": 4.2,
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1585794937776-5d2cff4bca53?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Premium Office Chair",
        "description": "Comfort-focused chair built to improve posture and support long work hours.",
        "category": "Accessories",
        "price": 14999,
        "rating": 4.4,
        "stock": 14,
        "image_url": "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Puma Running Shoes",
        "description": "Lightweight everyday sneakers designed to feel comfortable for city walking and exercise.",
        "category": "Fashion",
        "price": 5299,
        "rating": 4.3,
        "stock": 41,
        "image_url": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Noise Cancelling Earbuds",
        "description": "Compact wireless earbuds offering decent audio quality and comfort for daily commuting.",
        "category": "Audio",
        "price": 4999,
        "rating": 4.1,
        "stock": 58,
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Realme Narzo 70",
        "description": "Affordable smartphone with an excellent display, smooth performance, and daily usability.",
        "category": "Mobile Phones",
        "price": 17999,
        "rating": 4.2,
        "stock": 48,
        "image_url": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=900&q=80",
    },
]


def seed_database() -> None:
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {})
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        existing_count = session.query(Product).count()
        if existing_count > 0:
            return

        for item in PRODUCTS:
            product = Product(
                name=item["name"],
                description=item["description"],
                category=item["category"],
                price=item["price"],
                rating=item["rating"],
                stock=item["stock"],
                image_url=item["image_url"],
                created_at=datetime.utcnow(),
            )
            session.add(product)

        session.commit()


if __name__ == "__main__":
    seed_database()
    print("Seed data inserted successfully.")
