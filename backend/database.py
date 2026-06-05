import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres123@localhost:5432/ai_interview_db"
)


def create_sqlalchemy_engine(url: str):
    if url.startswith("sqlite://"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)


try:
    engine = create_sqlalchemy_engine(DATABASE_URL)
    # test the connection before creating tables
    with engine.connect() as connection:
        pass
    print(f"Connected to database: {DATABASE_URL}")
except SQLAlchemyError as exc:
    print(f"Warning: could not connect to PostgreSQL at {DATABASE_URL}. Falling back to SQLite.")
    print(f"Error: {exc}")
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_sqlalchemy_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.create_all(bind=engine)
print("Database initialized successfully")
print(f"Using database URL: {DATABASE_URL}")