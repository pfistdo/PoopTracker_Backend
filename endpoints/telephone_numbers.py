from typing import Optional
from fastapi import APIRouter, HTTPException

from database.db_connector import get_mysql_connection
from models.telephone_number import Telephone_Number

router = APIRouter()

# Fetch all telephone numbers
@router.get("/telephone_numbers/", response_model=list[Telephone_Number])
@router.get("/telephone_numbers/{count}", response_model=list[Telephone_Number])
def get_all_telephone_numbers(count: Optional[int] = None):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor(dictionary=True)

        if count is None:
            query = "SELECT * FROM telephone_number"
        else:
            query = f"SELECT * FROM telephone_number ORDER BY ID_telephone_number DESC LIMIT {count}"

        cursor.execute(query)
        telephone_numbers = cursor.fetchall()
        cursor.close()
        cnx.close()
        return telephone_numbers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insert new telephone number
@router.post("/telephone_numbers/", response_model=Telephone_Number)
def insert_telephone_number(telnr: Telephone_Number):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor()
        query = """
            INSERT INTO telephone_number (name, telnr)
            VALUES (%s, %s)
        """
        values = (telnr.name, telnr.telnr)
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()
        cnx.close()
        return telnr
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))