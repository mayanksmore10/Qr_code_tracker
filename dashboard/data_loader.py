import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found.")

engine_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(engine_url)


def load_visits(start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
    query = "SELECT * FROM visits"
    conditions = []
    params = {}

    if start_date:
        conditions.append("timestamp >= %(start_date)s")
        params["start_date"] = start_date
    if end_date:
        conditions.append("timestamp <= %(end_date)s")
        params["end_date"] = end_date

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    df = pd.read_sql(query, engine, params=params if params else None)

    if df.empty:
        return df

    return df


if __name__ == "__main__":
    data = load_visits()
    print(f"Loaded {len(data)} rows")
    print(data.head())