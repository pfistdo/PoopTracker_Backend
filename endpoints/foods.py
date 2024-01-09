from typing import Optional

from fastapi import APIRouter, HTTPException

from database.db_connector import get_mysql_connection
from models.food import Food

router = APIRouter()

# Fetch all foods
@router.get("/foods/", response_model=list[Food])
@router.get("/foods/{count}", response_model=list[Food])
def get_all_foods(count: Optional[int] = None):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor(dictionary=True)

        if count is None:
            query = "SELECT * FROM food"
        else:
            query = f"SELECT * FROM food ORDER BY ID_food DESC LIMIT {count}"

        cursor.execute(query)
        foods = cursor.fetchall()
        cursor.close()
        cnx.close()
        return foods
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insert a new food
@router.post("/foods/", response_model=Food)
def create_food(food: Food):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor()
        query = "INSERT INTO food (name, meat, protein, fat, ash, fibres, moisture) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (food.name, food.meat, food.protein, food.fat, food.ash, food.fibres, food.moisture))
        cnx.commit()
        food.ID_food = cursor.lastrowid
        cursor.close()
        cnx.close()
        return food
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))