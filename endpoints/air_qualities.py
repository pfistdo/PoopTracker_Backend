from datetime import datetime
import json

from typing import Optional
from fastapi import APIRouter, HTTPException

from database.db_connector import get_mysql_connection
from websocket_manager import notify_clients
from models.air_quality import Air_Quality

router = APIRouter()

# Fetch all air qualities
@router.get("/air_qualities/", response_model=list[Air_Quality])
@router.get("/air_qualities/{count}", response_model=list[Air_Quality])
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
@router.post("/air_qualities/", response_model=Air_Quality)
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
@router.post("/liveair_qualities/", response_model=Air_Quality)
async def broadcast_weight(air_quality: Air_Quality):
    air_quality_dict = dict(air_quality)
    air_quality_dict["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    air_quality_dict["type"] = "liveGasValue" # to identify payload in frontend
    weight_json = json.dumps(air_quality_dict)
    await notify_clients(weight_json)
    return air_quality