from datetime import datetime

from pydantic import BaseModel

class Food(BaseModel):
    ID_food: int = None
    name: str
    meat: str
    protein: int
    fat: int
    ash: int
    fibres: int
    moisture: int
    timestamp: datetime = None