from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from database import get_mysql_connection

app = FastAPI()

# Entity classes
class Food(BaseModel):
    ID_food: int = None
    name: str
    meat: str
    protein: int = None
    fat: int = None
    ash: int = None
    fibres: int = None
    moisture: int = None
    timestamp: datetime = None

class Poop(BaseModel):
    ID_poop: int = None
    weight: int
    air_quality: int
    food_ID: int = None
    timestamp: datetime = None

## ####################################################
## Endpoints
## ####################################################

# Fetch all foods
@app.get("/foods/", response_model=list[Food])
def get_all_foods():
    cnx = get_mysql_connection()
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT * FROM food"
    cursor.execute(query)
    foods = cursor.fetchall()
    cursor.close()
    cnx.close()
    return foods

# Fetch all poops
@app.get("/poops/", response_model=list[Poop])
def get_all_poops():
    cnx = get_mysql_connection()
    cursor = cnx.cursor(dictionary=True)
    query = "SELECT * FROM poop"
    cursor.execute(query)
    poops = cursor.fetchall()
    cursor.close()
    cnx.close()
    return poops

# Insert a new food
@app.post("/foods/", response_model=Food)
def create_food(food: Food):
    cnx = get_mysql_connection()
    cursor = cnx.cursor()
    query = "INSERT INTO food (name, meat, protein, fat, ash, fibres, moisture) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (food.name, food.meat, food.protein, food.fat, food.ash, food.fibres, food.moisture))
    cnx.commit()
    food.ID_food = cursor.lastrowid
    cursor.close()
    cnx.close()
    return food

# Insert a new poop
@app.post("/poops/", response_model=Poop)
def create_poop(poop: Poop):
    cnx = get_mysql_connection()
    cursor = cnx.cursor()

    # Get the timestamp 12 hours ago
    timestamp_threshold = datetime.now() - timedelta(hours=12)
    
    # Query to get the last inserted food ID within the last 12 hours
    select_food_query = "SELECT ID_food FROM food WHERE timestamp >= %s ORDER BY timestamp DESC LIMIT 1"
    cursor.execute(select_food_query, (timestamp_threshold,))
    result = cursor.fetchone()

    if result:
        food_ID = result[0]
        query = "INSERT INTO poop (weight, air_quality, food_ID) VALUES (%s, %s, %s)"
        cursor.execute(query, (poop.weight, poop.air_quality, food_ID))
        cnx.commit()
        poop.ID_poop = cursor.lastrowid
    else:
        raise HTTPException(status_code=404, detail="No food found in the last 12 hours")

    cursor.close()
    cnx.close()
    return poop

# Reroute to the docs
@app.get("/")
async def docs_redirect():
    return RedirectResponse(url='/docs')