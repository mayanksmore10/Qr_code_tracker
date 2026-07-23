import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load .env from the project root (one level above this file's directory)
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_RENDER_URL")

if not DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL not found. Looked for .env at: {_ENV_PATH}\n"
        "Make sure the .env file exists and contains DATABASE_URL."
    )

engine_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(engine_url, pool_pre_ping=True)


def load_visits() -> pd.DataFrame:
    return pd.read_sql("SELECT * FROM visits", engine)


if __name__ == "__main__":
    data = load_visits()
    print(f"Loaded {len(data)} rows")
    print(data.head())