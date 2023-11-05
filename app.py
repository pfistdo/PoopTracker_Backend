from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

POOP = {
    '1': {'500g': '15c'},
    '2': {'350g': '18c'},
}

## ####################################################
## Helper functions
## ####################################################
class Poop(Resource):
    def get(self, poop_id):
        return POOP[poop_id]

## ####################################################
## Endpoints
## ####################################################
api.add_resource(Poop, '/poop/<poop_id>')


if __name__ == '__main__':
    app.run(debug=True)