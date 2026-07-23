"""
Full sync migration: ensure ALL columns defined in models.Visit exist on
the remote Render 'visits' table.  Safe to run multiple times (IF NOT EXISTS).
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

DATABASE_URL = os.getenv("DATABASE_RENDER_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_RENDER_URL not set in .env")

engine_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(engine_url)

COLUMNS = [
    ("latitude",          "DOUBLE PRECISION"),
    ("longitude",         "DOUBLE PRECISION"),
    ("place",             "TEXT"),
    ("suburb",            "TEXT"),
    ("road",              "TEXT"),
    ("pincode",           "TEXT"),
    ("device_type",       "TEXT"),
    ("permission_granted","BOOLEAN DEFAULT FALSE"),
    ("hour",              "INTEGER"),
    ("date",              "DATE"),
    ("timestamp",         "TIMESTAMP"),
]

with engine.begin() as conn:
    for col_name, col_type in COLUMNS:
        stmt = f"ALTER TABLE visits ADD COLUMN IF NOT EXISTS {col_name} {col_type};"
        conn.execute(text(stmt))
        print(f"  ensured: {col_name} {col_type}")

print("\nMigration complete — all columns ensured on 'visits' table.")

