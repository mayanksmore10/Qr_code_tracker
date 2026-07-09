from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    place = Column(String, nullable=True)
    suburb = Column(String, nullable=True)
    road = Column(String, nullable=True)
    pincode = Column(String, nullable=True)

    permission_granted = Column(Boolean, default=False)

    timestamp = Column(DateTime, default=lambda: datetime.now(IST))