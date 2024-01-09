from datetime import date

from pydantic import BaseModel

class Cat(BaseModel):
    ID_cat: int = None
    name: str
    birthdate: date
    gender: str
    color: str
    chipped: bool