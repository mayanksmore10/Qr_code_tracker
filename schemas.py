from pydantic import BaseModel
from typing import Optional


class VisitCreate(BaseModel):
    qr_id: str
    permission_granted: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None