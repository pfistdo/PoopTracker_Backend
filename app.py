from flask import Flask
from flask_restful import Api, Resource, reqparse
import mysql.connector

app = Flask(__name__)
api = Api(app)
# DB connection
user = 'root'
password = 'admin'
host = '127.0.0.1'
database = 'poop_tracker'

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
        finally:
            cursor.close()
            cnx.close()
        return result, 200
    
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
        return "Poop data inserted successfully", 201

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
        finally:
            cursor.close()
            cnx.close()
        return result, 200

## ####################################################
## Endpoints
## ####################################################
api.add_resource(Poop, '/poop/<poop_id>', '/poop', '/poop/')
api.add_resource(PoopList, '/poops', '/poops/')


if __name__ == '__main__':
    app.run(debug=True)