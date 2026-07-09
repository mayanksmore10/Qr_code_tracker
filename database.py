import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError(
        "DATABASE_URL not found. "
        "Locally: check your .env file. "
        "On Render: add DATABASE_URL in the Environment tab of your Web Service."
    )

# Render (and some other hosts) provide the URL with the legacy "postgres://" scheme.
# SQLAlchemy + psycopg2 requires "postgresql+psycopg2://", so we normalise it here.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+psycopg2" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    DATABASE_URL,
    # pool_pre_ping checks the connection before using it from the pool.
    # This prevents "connection closed" errors on Render's free tier, which
    # idles database connections after periods of inactivity.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()