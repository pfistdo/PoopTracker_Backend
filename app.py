import json
import socket
from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
api = Api(app)
# Enable CORS for all routes
CORS(app)

# Determine the environment (local or pythonanywhere)
if "PC22" in socket.gethostname():
    environment = "local"
else:
    environment = "pythonanywhere"

# Load the configuration from the JSON file
if environment == "local":
    config_file_path = "config.json"
else:
    config_file_path = "/home/pfistdo/mysite/config.json"
with open(config_file_path) as config_file:
    config = json.load(config_file)

# Get the database configuration
db_config = config[environment]
user = db_config["user"]
password = db_config["password"]
host = db_config["host"]
database = db_config["database"]

socketio = SocketIO(app, cors_allowed_origins='*')

#This methode sends the data via WebSocket to the connected frontend
def sendData(value):
    socketio.emit('sensor_data', {'data': value})

## ####################################################
## Resources
## ####################################################
class Poop(Resource):
    # Get a single poop
    def get(self, poop_id):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            query = ("SELECT * FROM poop WHERE ID_poop = %s")
            cursor.execute(query, (poop_id,))
            result = cursor.fetchone()
            result["timestamp"] = result["timestamp"].__str__() # Convert the datetime object to a string
        except mysql.connector.Error as err:
            return error_response(str(err), 500)
        finally:
            close_db_connection(connection, cursor)
        return result or {}, 200

    # Insert a new poop
    def post(self):
        connection = get_db_connection()
        cursor = connection.cursor()

        parser = reqparse.RequestParser()
        parser.add_argument('weight')
        parser.add_argument('air_quality')
        parser.add_argument('food_ID')
        data = parser.parse_args()

        try:
            query = "INSERT INTO poop (weight, air_quality, food_ID) VALUE (%s, %s, %s);"
            cursor.execute(query, (data['weight'], data['air_quality'], data['food_ID'],))
            connection.commit()
        except mysql.connector.Error as err:
            return error_response(str(err), 500)
        finally:
            close_db_connection(connection, cursor)
        # sendData(data['weight'])
        return "Poop data inserted successfully", 201

class PoopList(Resource):
    # Get all poops
    def get(self):
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            query = ("SELECT * FROM poop;")
            cursor.execute(query)
            result = cursor.fetchall()
            for row in result:
                row["timestamp"] = row["timestamp"].__str__() # Convert the datetime object to a string
        except mysql.connector.Error as err:
            return error_response(str(err), 500)
        finally:
            close_db_connection(connection, cursor)
        return result or {}, 200

## ####################################################
## Endpoints
## ####################################################
api.add_resource(Poop, '/poop/<poop_id>', '/poop', '/poop/')
api.add_resource(PoopList, '/poops', '/poops/')

## ####################################################
## Helpers
## ####################################################
def get_db_connection():
    return mysql.connector.connect(user=user, password=password,
                                        host=host,
                                        database=database)

def close_db_connection(connection, cursor):
    cursor.close()
    connection.close()

def error_response(message, status_code):
    return {'error': message}, status_code

## ####################################################
## Main
## ####################################################
if __name__ == '__main__':
    socketio.run(app, port=5000)