import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def build_database(database_name: str) -> tuple[Engine, sessionmaker[Session]]:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        url: str | URL = database_url
    else:
        url = URL.create(
            drivername="mysql+pymysql",
            username=os.getenv("DB_USER", f"{database_name}_user"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "mysql"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", database_name),
        )

    engine = create_engine(url, pool_pre_ping=True)
    return engine, sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session_factory(factory: sessionmaker[Session]):
    def get_db() -> Generator[Session, None, None]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    return get_db
