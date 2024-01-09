from pydantic import BaseModel

class Telephone_Number(BaseModel):
    ID_telephone_number: int = None
    name: str
    telnr: str