from datetime import date, datetime, timedelta
import json
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from database import get_mysql_connection


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

##############################
#### Configure WebSocket
##############################
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
manager = ConnectionManager()

# Define an async function to notify clients
async def notify_clients(message: str):
    print(f"Trying to send data via websocket: {message}")
    await manager.broadcast(message)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

## ####################################################
## Entity classes
## ####################################################
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
    birthdate: date
    gender: str
    color: str
    chipped: bool

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

class Poop(BaseModel):
    ID_poop: int = None
    weight: int
    timestamp: datetime = None
    feeding_ID: int = None

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

class Weight(BaseModel):
    ID_weight: int = None
    weight: int
    timestamp: datetime = None
    cat_ID: int = None

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
async def create_poop(poop: Poop):
    try:
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
            print("No feeding found in the last 12 hours. Using 9 as feeding_ID.")
            feeding_ID = 9
        query = "INSERT INTO poop (weight, feeding_ID) VALUES (%s, %s)"
        cursor.execute(query, (poop.weight, feeding_ID))
        cnx.commit()

        # Fetch the timestamp of the inserted poop and create Poop object
        cursor.execute("SELECT timestamp FROM poop WHERE ID_poop = LAST_INSERT_ID()")
        poop_timestamp = cursor.fetchone()[0]
        formatted_timestamp = poop_timestamp.strftime("%Y-%m-%dT%H:%M:%S") # format timestamp for WebSocket
        poop.timestamp = poop_timestamp
        poop.ID_poop = cursor.lastrowid
        cursor.close()
        cnx.close()

        # Notify WebSocket clients with the JSON data
        poop_dict = dict(poop)
        poop_dict["timestamp"] = formatted_timestamp
        poop_dict["type"] = "poop" # to identify payload in frontend
        poop_json = json.dumps(poop_dict)
        await notify_clients(poop_json)

        return poop
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
async def insert_air_quality(air_quality: Air_Quality):
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

        cursor.execute("SELECT timestamp FROM air_quality WHERE ID_air_quality = LAST_INSERT_ID()")
        air_quality_timestamp = cursor.fetchone()[0]
        formatted_timestamp = air_quality_timestamp.strftime("%Y-%m-%dT%H:%M:%S") # format timestamp for WebSocket
        air_quality.timestamp = air_quality_timestamp
        air_quality.ID_air_quality = cursor.lastrowid
        cursor.close()
        cnx.close()

        # Notify WebSocket clients with the JSON data
        air_quality_dict = dict(air_quality)
        air_quality_dict["timestamp"] = formatted_timestamp
        air_quality_dict["type"] = "airQuality" # to identify payload in frontend
        air_quality_json = json.dumps(air_quality_dict)
        await notify_clients(air_quality_json)

        return air_quality
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Broadcast live air_quality via WebSocket
@app.post("/liveair_qualities/", response_model=Air_Quality)
async def broadcast_weight(air_quality: Air_Quality):
    air_quality_dict = dict(air_quality)
    # weight_dict["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    air_quality_dict["type"] = "liveGasValue" # to identify payload in frontend
    weight_json = json.dumps(air_quality_dict)
    await notify_clients(weight_json)
    return air_quality

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
@app.post("/feedings/", response_model=Feeding)
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

# Fetch all weights
@app.get("/weights/", response_model=list[Weight])
@app.get("/weights/{count}", response_model=list[Weight])
def get_all_weights(count: Optional[int] = None):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor(dictionary=True)

        if count is None:
            query = "SELECT * FROM weight"
        else:
            query = f"SELECT * FROM weight ORDER BY ID_weight DESC LIMIT {count}"

        cursor.execute(query)
        weights = cursor.fetchall()
        cursor.close()
        cnx.close()
        return weights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Insert a new weight
@app.post("/weights/", response_model=Weight)
def create_weight(weight: Weight):
    try:
        cnx = get_mysql_connection()
        cursor = cnx.cursor()
        query = "INSERT INTO weight (weight, cat_ID) VALUES (%s, %s)"
        cursor.execute(query, (weight.weight, weight.cat_ID))
        cnx.commit()
        weight.ID_weight = cursor.lastrowid
        cursor.close()
        cnx.close()
        return weight
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Broadcast live weight via WebSocket
@app.post("/liveWeights/", response_model=Weight)
async def broadcast_weight(weight: Weight):
    weight_dict = dict(weight)
    # weight_dict["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    weight_dict["type"] = "liveWeight" # to identify payload in frontend
    weight_json = json.dumps(weight_dict)
    await notify_clients(weight_json)
    return weight

# Reroute to the docs
@app.get("/")
async def docs_redirect():
    return RedirectResponse(url='/docs')