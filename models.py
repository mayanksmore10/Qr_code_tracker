from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from database import Base

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    qr_id = Column(String, nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    place = Column(String, nullable=True)
    suburb = Column(String, nullable=True)
    road = Column(String, nullable=True)
    pincode = Column(String, nullable=True)

    permission_granted = Column(Boolean, default=False)

    timestamp = Column(DateTime, default=datetime.utcnow)