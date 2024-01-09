from datetime import datetime

from pydantic import BaseModel

class Weight(BaseModel):
    ID_weight: int = None
    weight: int
    timestamp: datetime = None
    cat_ID: int = None