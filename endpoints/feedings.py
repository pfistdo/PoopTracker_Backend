from typing import Optional
from fastapi import APIRouter, HTTPException

from database.db_connector import get_mysql_connection
from models.feeding import Feeding, FeedingWithDetails

router = APIRouter()

# Fetch all feedings
@router.get("/feedings/", response_model=list[FeedingWithDetails])
@router.get("/feedings/{count}", response_model=list[FeedingWithDetails])
def get_all_feedings_with_details(count: Optional[int] = None):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor(dictionary=True)

        if count is None:
            query = """
                SELECT feeding.ID_feeding, feeding.timestamp, food.ID_food AS food_ID, food.name AS food_name, 
                food.meat AS food_meat, food.protein AS food_protein, food.fat AS food_fat, food.ash AS food_ash, 
                food.fibres AS food_fibres, food.moisture AS food_moisture, food.timestamp as food_timestamp, 
                cat.ID_cat AS cat_ID, cat.name AS cat_name, cat.birthdate AS cat_birthdate, cat.gender as cat_gender, 
                cat.color as cat_color, cat.chipped as cat_chipped
                FROM feeding
                INNER JOIN food ON feeding.food_ID = food.ID_food
                INNER JOIN cat ON feeding.cat_ID = cat.ID_cat
            """
        else:
            query = f"""
                SELECT feeding.ID_feeding, feeding.timestamp, food.ID_food AS food_ID, food.name AS food_name, 
                food.meat AS food_meat, food.protein AS food_protein, food.fat AS food_fat, food.ash AS food_ash, 
                food.fibres AS food_fibres, food.moisture AS food_moisture, food.timestamp as food_timestamp, 
                cat.ID_cat AS cat_ID, cat.name AS cat_name, cat.birthdate AS cat_birthdate, cat.gender as cat_gender, 
                cat.color as cat_color, cat.chipped as cat_chipped
                FROM feeding
                INNER JOIN food ON feeding.food_ID = food.ID_food
                INNER JOIN cat ON feeding.cat_ID = cat.ID_cat
                ORDER BY ID_feeding DESC 
                LIMIT {count}
            """
        cursor.execute(query)
        feedings_with_details = cursor.fetchall()
        cursor.close()
        cnx.close()

        feedings = []
        for feeding_data in feedings_with_details:
            feeding_timestamp = str(feeding_data["timestamp"])  # Convert timestamp to string
            food_data = {
                "ID_food": feeding_data["food_ID"],
                "name": feeding_data["food_name"],
                "meat": feeding_data["food_meat"],
                "protein": feeding_data["food_protein"],
                "fat": feeding_data["food_fat"],
                "ash": feeding_data["food_ash"],
                "fibres": feeding_data["food_fibres"],
                "moisture": feeding_data["food_moisture"],
                "timestamp": feeding_data["food_timestamp"],
            }
            cat_data = {
                "ID_cat": feeding_data["cat_ID"],
                "name": feeding_data["cat_name"],
                "birthdate": feeding_data["cat_birthdate"],
                "gender": feeding_data["cat_gender"],
                "color": feeding_data["cat_color"],
                "chipped": feeding_data["cat_chipped"],
            }
            feeding_with_details = FeedingWithDetails(
                ID_feeding=feeding_data["ID_feeding"],
                timestamp=feeding_timestamp,
                food=food_data,
                cat=cat_data,
            )
            feedings.append(feeding_with_details)

        return feedings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insert new feeding
@router.post("/feedings/", response_model=Feeding)
def insert_feeding(feeding: Feeding):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor()
        query = """
            INSERT INTO feeding (food_ID, cat_ID, timestamp)
            VALUES (%s, %s, %s)
        """
        values = (feeding.food_ID, feeding.cat_ID, feeding.timestamp)
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()
        cnx.close()
        return feeding
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))