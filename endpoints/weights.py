from datetime import datetime
import json

from typing import Optional
from fastapi import APIRouter, HTTPException

from database.db_connector import get_mysql_connection
from websocket_manager import manager 
from models.weight import Weight

router = APIRouter()

# Fetch all weights
@router.get("/weights/", response_model=list[Weight])
@router.get("/weights/{count}", response_model=list[Weight])
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
@router.post("/weights/", response_model=Weight)
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
@router.post("/liveWeights/", response_model=Weight)
async def broadcast_weight(weight: Weight):
    weight_dict = dict(weight)
    weight_dict["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    weight_dict["type"] = "liveWeight" # to identify payload in frontend
    weight_json = json.dumps(weight_dict)
    await manager.broadcast(weight_json) # send payload via WebSocket
    
    return weight