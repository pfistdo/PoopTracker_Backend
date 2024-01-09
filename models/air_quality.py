from datetime import datetime

from pydantic import BaseModel

class Air_Quality(BaseModel):
    ID_air_quality: int = None
    lpg: int
    co: int
    smoke: int
    timestamp: datetime = None