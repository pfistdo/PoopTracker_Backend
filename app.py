from flask import Flask
from flask_restful import Api, Resource
import mysql.connector

app = Flask(__name__)
api = Api(app)
# DB connection
cnx = mysql.connector.connect(user='root', password='admin',
                                    host='127.0.0.1',
                                    database='poop_tracker')

## ####################################################
## Resources
## ####################################################
class Poop(Resource):
    def get(self, poop_id):
        try:
            cursor = cnx.cursor(dictionary=True)
            query = ("SELECT * FROM poop WHERE ID_poop = %s")
            cursor.execute(query, (poop_id,))
            result = cursor.fetchone()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        finally:
            cursor.close()
            cnx.close()
        return result
    
class PoopList(Resource):
    def get(self):
        try:
            cursor = cnx.cursor(dictionary=True)
            query = ("SELECT * FROM poop;")
            cursor.execute(query)
            result = cursor.fetchall()
            print(result)
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        finally:
            cursor.close()
            cnx.close()
        return result

## ####################################################
## Endpoints
## ####################################################
api.add_resource(Poop, '/poop/<poop_id>')
api.add_resource(PoopList, '/poop', '/poop/')


if __name__ == '__main__':


    app.run(debug=True)