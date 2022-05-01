from flask import Flask
from flask_restful import Resource, Api, reqparse
import json

app = Flask(__name__)
api = Api(app)

class Tvl(Resource):
    def get(self):
        with open("files/tvls_evolution.json") as file:
            return json.load(file)

class Transactions(Resource):
    def get(self):
        with open("files/tvls_evolution.json") as file:
            return json.load(file)

api.add_resource(Tvl, "/tvl")
api.add_resource(Transactions, "/tx")

if __name__ =="__main__":
    app.run()