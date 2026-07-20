from pydantic import BaseModel
from typing import Optional


class VisitCreate(BaseModel):
    permission_granted: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    device_type: Optional[str] = None