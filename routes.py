from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from database import get_mysql_connection
from typing import Optional

from typing import Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
##############################
#### Enable CORS 
##############################
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Entity classes
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

class Cat(BaseModel):
    ID_cat: int = None
    name: str
    weight: float
    timestamp: datetime = None

class Feeding(BaseModel):
    ID_feeding: int = None
    timestamp: datetime = None
    food_ID: int = None
    cat_ID: int = None

class FeedingWithDetails(BaseModel):
    ID_feeding: int
    timestamp: str
    food: Food  # Embedded Food details
    cat: Cat  # Embedded Cat details

class Poop(BaseModel):
    ID_poop: int = None
    weight: int
    timestamp: datetime = None
    feeding_ID: int = None

class Cat(BaseModel):
    ID_cat: int = None
    name: str
    weight: float
    timestamp: datetime = None

class Air_Quality(BaseModel):
    ID_air_quality: int = None
    lpg: int
    co: int
    smoke: int
    timestamp: datetime = None

class Telephone_Number(BaseModel):
    ID_telephone_number: int = None
    name: str
    telnr: str

## ####################################################
## Endpoints
## ####################################################

# Fetch all foods
@app.get("/foods/", response_model=list[Food])
@app.get("/foods/{count}", response_model=list[Food])
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

# Fetch all poops
@app.get("/poops/", response_model=list[Poop])
@app.get("/poops/{count}", response_model=list[Poop])
def get_all_poops(count: Optional[int] = None):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor(dictionary=True)

        if count is None:
            query = "SELECT * FROM poop"
        else:
            query = f"SELECT * FROM poop ORDER BY ID_poop DESC LIMIT {count}"

        cursor.execute(query)
        poops = cursor.fetchall()
        cursor.close()
        cnx.close()
        return poops
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insert a new poop
@app.post("/poops/", response_model=Poop)
def create_poop(poop: Poop):
    cnx = get_mysql_connection()
    cursor = cnx.cursor()

    # Get the timestamp 12 hours ago
    timestamp_threshold = datetime.now() - timedelta(hours=12)
    
    # Query to get the last inserted food ID within the last 12 hours
    select_feeding_query = "SELECT ID_feeding FROM feeding WHERE timestamp >= %s ORDER BY timestamp DESC LIMIT 1"
    cursor.execute(select_feeding_query, (timestamp_threshold,))
    result = cursor.fetchone()

    if result:
        feeding_ID = result[0]
    else:
        print("No feeding found in the last 12 hours. Using 1 as feeding_ID.")
        feeding_ID = 1
    query = "INSERT INTO poop (weight, feeding_ID) VALUES (%s, %s)"
    cursor.execute(query, (poop.weight, feeding_ID))
    cnx.commit()
    poop.ID_poop = cursor.lastrowid
    cursor.close()
    cnx.close()
    return poop

# Fetch all cats
@app.get("/cats/", response_model=list[Cat])
@app.get("/cats/{count}", response_model=list[Cat])
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
@app.post("/cats/", response_model=Cat)
def insert_cat(cat: Cat):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor()
        query = """
            INSERT INTO cat (name, weight)
            VALUES (%s, %s)
        """
        values = (cat.name, cat.weight)
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()
        cnx.close()
        return cat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Fetch all air qualities
@app.get("/air_qualities/", response_model=list[Air_Quality])
@app.get("/air_qualities/{count}", response_model=list[Air_Quality])
def get_all_air_qualities(count: Optional[int] = None):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor(dictionary=True)

        if count is None:
            query = "SELECT * FROM air_quality"
        else:
            query = f"SELECT * FROM air_quality ORDER BY ID_air_quality DESC LIMIT {count}"

        cursor.execute(query)
        air_qualities = cursor.fetchall()
        cursor.close()
        cnx.close()
        return air_qualities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insert new air quality
@app.post("/air_qualities/", response_model=Air_Quality)
def insert_air_quality(air_quality: Air_Quality):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor()
        query = """
            INSERT INTO air_quality (lpg, co, smoke)
            VALUES (%s, %s, %s)
        """
        values = (air_quality.lpg, air_quality.co, air_quality.smoke)
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()
        cnx.close()
        return air_quality
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fetch all telephone numbers
@app.get("/telephone_numbers/", response_model=list[Telephone_Number])
@app.get("/telephone_numbers/{count}", response_model=list[Telephone_Number])
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
@app.post("/telephone_numbers/", response_model=Telephone_Number)
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
    
# Fetch all feedings
@app.get("/feedings/", response_model=list[FeedingWithDetails])
@app.get("/feedings/{count}", response_model=list[FeedingWithDetails])
def get_all_feedings_with_details(count: Optional[int] = None):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor(dictionary=True)

        if count is None:
            query = """
                SELECT feeding.ID_feeding, feeding.timestamp, food.ID_food AS food_ID, food.name AS food_name, 
                food.meat AS food_meat, food.protein AS food_protein, food.fat AS food_fat, food.ash AS food_ash, 
                food.fibres AS food_fibres, food.moisture AS food_moisture, food.timestamp as food_timestamp, 
                cat.ID_cat AS cat_ID, cat.name AS cat_name, cat.weight AS cat_weight, cat.timestamp as cat_timestamp
                FROM feeding
                INNER JOIN food ON feeding.food_ID = food.ID_food
                INNER JOIN cat ON feeding.cat_ID = cat.ID_cat
            """
        else:
            query = f"""
                SELECT feeding.ID_feeding, feeding.timestamp, food.ID_food AS food_ID, food.name AS food_name, 
                food.meat AS food_meat, food.protein AS food_protein, food.fat AS food_fat, food.ash AS food_ash, 
                food.fibres AS food_fibres, food.moisture AS food_moisture, food.timestamp as food_timestamp, 
                cat.ID_cat AS cat_ID, cat.name AS cat_name, cat.weight AS cat_weight, cat.timestamp as cat_timestamp
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
                "weight": feeding_data["cat_weight"],
                "timestamp": feeding_data["cat_timestamp"],
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
@app.post("/feedings/", response_model=Feeding)
def insert_feeding(feeding: Feeding):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor()
        query = """
            INSERT INTO feeding (food_ID, cat_ID)
            VALUES (%s, %s)
        """
        values = (feeding.food_ID, feeding.cat_ID)
        cursor.execute(query, values)
        cnx.commit()
        cursor.close()
        cnx.close()
        return feeding
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Reroute to the docs
@app.get("/")
async def docs_redirect():
    return RedirectResponse(url='/docs')