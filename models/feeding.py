from datetime import datetime

from pydantic import BaseModel

from models.food import Food
from models.cat import Cat

class Feeding(BaseModel):
    ID_feeding: int = None
    timestamp: datetime
    food_ID: int = None
    cat_ID: int = None

class FeedingWithDetails(BaseModel):
    ID_feeding: int
    timestamp: str
    food: Food  # Embedded Food details
    cat: Cat  # Embedded Cat details