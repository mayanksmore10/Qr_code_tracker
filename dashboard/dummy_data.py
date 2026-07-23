import os
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_RENDER_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found - make sure .env is in the current directory.")

engine_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = create_engine(engine_url)

IST = timezone(timedelta(hours=5, minutes=30)) 

NUM_RECORDS = 60
TABLE_NAME = "visits"
DAYS_SPREAD = 45 

PLACES = ["Panvel Station Road", "Kharghar Sector 12", "Vashi Plaza", "Nerul Market", "Belapur CBD", "Airoli Depot", "Thane Station"]
SUBURBS = ["Panvel", "arKhargh", "Vashi", "Nerul", "Belapur", "Airoli", "Thane"]
ROADS = ["Sion-Panvel Highway", "Palm Beach Road", "Uran Road", "Thane-Belapur Road", "CBD Belapur Station Road", "Thane-Belapur Road","Ghodbunder Road"]
PINCODES = ["410206", "410210", "400703", "400706", "400614", "400708", "400601"]
SUBURB_WEIGHTS = [0.28, 02.2, 0.15, 0.12, 0.1, 0.08, 0.05]

DEVICES = ["Mobile", "Desktop", "Tablet"]
DEVICE_WEIGHTS = [0.72, 0.20, 0.08]

BASE_LAT, BASE_LNG = 19.03, 73.11


def generate_record():
    days_ago = random.expovariate(1 / 12)
    days_ago = min(days_ago, DAYS_SPREAD)
    ts = datetime.now(IST) - timedelta(
        days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59)
    )

    suburb_index = random.choices(range(len(SUBURBS)), weights=SUBURB_WEIGHTS)[0]

    return {
        "timestamp": ts,
        "date": ts.date(),
        "hour":ts.hour,
        "latitude": BASE_LAT + random.uniform(-0.05, 0.05),
        "longitude": BASE_LNG + random.uniform(-0.05, 0.05),
        "place": PLACES[suburb_index],
        "suburb": SUBURBS[suburb_index],
        "road": ROADS[suburb_index],
        "pincode": PINCODES[suburb_index],
        "device_type": random.choices(DEVICES, weights=DEVICE_WEIGHTS)[0],
        "permission_granted": random.choices([True, False], weights=[0.9, 0.1])[0],
    }


def seed():
    records = [generate_record() for _ in range(NUM_RECORDS)]

    insert_sql = text(f"""
        INSERT INTO {TABLE_NAME}
            (timestamp, date, hour, latitude, longitude, place, suburb, road, pincode, device_type, permission_granted)
        VALUES
            (:timestamp, :date, :hour, :latitude, :longitude, :place, :suburb, :road, :pincode, :device_type, :permission_granted)
    """)

    with engine.begin() as conn:
        conn.execute(insert_sql, records)

    print(f"Inserted {len(records)} dummy records into '{TABLE_NAME}'.")


if __name__ == "__main__":
    confirm = input(
        f"This will insert {NUM_RECORDS} dummy rows into the '{TABLE_NAME}' table "
        f"on your REAL database. Continue? (y/n): "
    )
    if confirm.strip().lower() == "y":
        seed()
    else:
        print("Cancelled.")