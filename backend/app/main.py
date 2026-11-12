from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routes.cart import router as cart_router
from app.routes.chat import router as chat_router
from app.routes.products import router as product_router
from seed import seed_database

Base.metadata.create_all(bind=engine)
seed_database()

app = FastAPI(
    title="AI Shop Assistant",
    description="Simple AI e-commerce assistant built with FastAPI and SQLite.",
    version="1.0.0",
)

origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:80",
    "http://127.0.0.1:80",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    seed_database()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(product_router)
app.include_router(cart_router)
app.include_router(chat_router)
