from datetime import datetime

from pydantic import BaseModel

class Poop(BaseModel):
    ID_poop: int = None
    weight: int
    timestamp: datetime = None
    feeding_ID: int = None