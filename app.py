from flask import Flask
from flask_restful import Api, Resource, reqparse
import mysql.connector
import json
import socket
import os

app = Flask(__name__)
api = Api(app)

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

## ####################################################
## Resources
## ####################################################
class Poop(Resource):
    # Get a single poop
    def get(self, poop_id):
        try:
            with mysql.connector.connect(user=user, password=password,
                                        host=host,
                                        database=database) as cnx:
                with cnx.cursor(dictionary=True) as cursor:
                    query = ("SELECT * FROM poop WHERE ID_poop = %s")
                    cursor.execute(query, (poop_id,))
                    result = cursor.fetchone()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return "An error occurred while processing the request", 500
        return result, 200  # The cursor will be automatically closed here

    # Insert a new poop
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('weight')
            data = parser.parse_args()
            with mysql.connector.connect(user=user, password=password,
                                        host=host,
                                        database=database) as cnx:
                with cnx.cursor() as cursor:
                    query = "INSERT INTO poop (weight) VALUE (%s);"
                    cursor.execute(query, (data['weight'],))
                    cnx.commit()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return "An error occurred while processing the request", 500
        return "Poop data inserted successfully", 201  # The cursor will be automatically closed here


class PoopList(Resource):
    # Get all poops
    def get(self):
        try:
            with mysql.connector.connect(user=user, password=password,
                                        host=host,
                                        database=database) as cnx:
                with cnx.cursor(dictionary=True) as cursor:
                    query = ("SELECT * FROM poop;")
                    cursor.execute(query)
                    result = cursor.fetchall()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
            return "An error occurred while processing the request", 500
        return result, 200

## ####################################################
## Endpoints
## ####################################################
api.add_resource(Poop, '/poop/<poop_id>', '/poop', '/poop/')
api.add_resource(PoopList, '/poops', '/poops/')


## ####################################################
## Main
## ####################################################
if __name__ == '__main__':
    app.run(debug=True)