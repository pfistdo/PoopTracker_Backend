from typing import Optional
from fastapi import APIRouter, HTTPException

from database.db_connector import get_mysql_connection
from models.cat import Cat

router = APIRouter()

# Fetch all cats
@router.get("/cats/", response_model=list[Cat])
@router.get("/cats/{count}", response_model=list[Cat])
def get_all_cats(count: Optional[int] = None):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor(dictionary=True)

        if count is None:
            query = "SELECT * FROM cat"
        else:
            query = f"SELECT * FROM cat ORDER BY ID_cat DESC LIMIT {count}"

        cursor.execute(query)
        cats = cursor.fetchall()
        cursor.close()
        cnx.close()
        return cats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insert new cat
@router.post("/cats/", response_model=Cat)
def insert_cat(cat: Cat):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor()
        query = """
            INSERT INTO cat (name, birthdate, gender, color, chipped)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (cat.name, cat.birthdate, cat.gender, cat.color, cat.chipped)
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()
        cnx.close()
        return cat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))