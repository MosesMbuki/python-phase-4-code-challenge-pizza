#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET request to /restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
    return make_response(jsonify(restaurants), 200)

@app.route('/restaurants/<int:id>', methods=['GET', 'DELETE'])
def restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    if request.method == 'GET':
        restaurant_dict = restaurant.to_dict()
        restaurant_dict['restaurant_pizzas'] = [
            rp.to_dict() for rp in restaurant.restaurant_pizzas
        ]
        return make_response(jsonify(restaurant_dict), 200)
    
    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
    return make_response(jsonify(pizzas), 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    try:
        new_rp = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_rp)
        db.session.commit()
        return make_response(jsonify(new_rp.to_dict()), 201)
    except ValueError as e:
        return make_response(jsonify({"errors": [str(e)]}), 400)
    except Exception as e:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)



if __name__ == "__main__":
    app.run(port=5555, debug=True)