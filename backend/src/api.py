import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES


@app.route('/drinks')
@requires_auth('get:drinks')
def get_drinks():
    try:
        drinks = list(map(Drink.short, Drink.query.all()))
    except:
        abort(400)
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    try:
        drinks = list(map(Drink.long, Drink.query.all()))
    except:
        abort(400)
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks():
    try:
        body = request.get_json()
        drink = Drink(title=body["title"], recipe=json.dumps(body["recipe"]))
        drink.insert()
    except:
        abort(400)
    return jsonify({
        "success": True,
        "drinks": drink.long()
    })


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id):
    # print(Drink.query.all())
    try:
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.title = body["title"]
        drink.recipe = json.dumps(body["recipe"])
        drink.update()
    except:
        if drink is None:
            abort(404)
        abort(400)
    return jsonify({
        "success": True,
        "drinks": drink.long()
    })


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        drink.delete()
    except:
        if drink is None:
            abort(404)
        abort(400)
    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request",
    }), 400


@app.errorhandler(401)
def unauthorize_request(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized request",
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found",
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed",
    }), 405


@ app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
# Error handler


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
