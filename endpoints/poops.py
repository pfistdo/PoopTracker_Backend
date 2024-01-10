from datetime import datetime, timedelta
import json

from typing import Optional
from fastapi import APIRouter, HTTPException

from database.db_connector import get_mysql_connection
from websocket_manager import manager
from models.poop import Poop

router = APIRouter()

# Fetch all poops
@router.get("/poops/", response_model=list[Poop])
@router.get("/poops/{count}", response_model=list[Poop])
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
@router.post("/poops/", response_model=Poop)
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
        await manager.broadcast(poop_json) # send payload via WebSocket

        return poop
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))