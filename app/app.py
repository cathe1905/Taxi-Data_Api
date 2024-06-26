"""This module defines the endpoints for accessing taxi and trajectory data.
"""
import os
from flask import jsonify, Flask, request
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, jwt_required
from app.db.db import db
from app.controllers.taxi_controller import select_taxi, select_trajectories, select_last_trajectorie_by_taxi
from app.controllers.user_controller import generate_token, post_user, select_all_users, update_user, delete_user_selected
from app.controllers.data_xlsx_controller import retrieve_data_xlsx
from app.config import Config

load_dotenv()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.debug = True

db.init_app(app)

app.config.from_object(Config)

jwt = JWTManager(app)

@jwt.unauthorized_loader
def unauthorized_callback(error):
    """
    Custom response for requests missing a JWT token.
    Args:
        error (str): Error message from the JWT library.
    Returns:
        JSON response with a message indicating the absence of the token and a 401 status code.
    """
    return jsonify({'message': 'Please include an authentication token in the Authorization header of your request'}), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """
    Custom response for requests with an expired JWT token.
    Args:
        jwt_header (dict): JWT header data.
        jwt_payload (dict): JWT payload data.
    Returns:
        JSON response with a message indicating the token has expired and a 401 status code.
    """
    return jsonify({'message': 'Your authentication token has expired. Please generate a new token and include it in the Authorization header of your request.'}), 401

@app.route('/taxis')
@jwt_required()
def get_taxi():
    """Endpoint to retrieve taxi data.
    Returns:
        json: Taxi data.
    """
    arguments= request.args

    page= arguments.get("page", default=1, type=int)
    limit= arguments.get("limit", default=10, type=int)
    query= arguments.get("query", default="", type=str)
    
    return jsonify(select_taxi(page, limit, query))
  
@app.route('/trajectories/<int:taxi_id>')
@jwt_required()
def get_trajectories(taxi_id):
    """Endpoint to retrieve trajectory data for a specific taxi.
    Args:
        taxi_id (int): The ID of the taxi.
    Returns:
        json: Trajectory data for the specified taxi.
    """
    arguments= request.args
    date= arguments.get("date", default="", type=str)

    return jsonify(select_trajectories(taxi_id, date))

@app.route('/trajectories/latest')
@jwt_required()
def get_latest_trajectories():
    """Endpoint to retrieve the latest trajectories for all taxis.
    Returns:
        json: Latest trajectory data for all taxis.
    """ 
    arguments= request.args

    page= arguments.get("page", default=1, type=int)
    limit= arguments.get("limit", default=10, type=int)
    return jsonify(select_last_trajectorie_by_taxi(page, limit))

@app.route('/users', methods=['POST'])
def create_new_user():
    """Endpoint to add a new user into the data base.
    Returns:
        json: users data.
    """
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        return post_user(name, email, password)

    except Exception as error:
        return jsonify({'message': 'Internal server error'}), 500
    
@app.route('/users', methods=['GET'])
@jwt_required()
def get_all_user():
    """Endpoint to retrieve all users data.
    Returns:
        json: users data.
    """
    try:
        arguments= request.args

        page= arguments.get("page", default=1, type=int)
        limit= arguments.get("limit", default=10, type=int)

        return jsonify(select_all_users(page, limit))

    except Exception as error:
        return jsonify({'message': 'Internal server error'}), 500

@app.route('/users/<string:uid>', methods=['PATCH'])
@jwt_required()
def update_user_patch(uid):
    """Endpoint to retrieve an updated user.
    Returns:
        json: updated user.
    """
    try:
        data= request.json
        return update_user(uid, data)
        
    except:
        return jsonify({'message': 'Internal server error'}), 500
    
@app.route('/users/<string:uid>', methods=['DELETE'])
@jwt_required()
def delete_user(uid):
    """Endpoint to delete an user.
    Returns:
        json: deleted user.
    """
    try:
        return delete_user_selected(uid)

    except Exception as error:
        return jsonify({'message': 'Internal server error'}), 500
    
@app.route('/auth/login', methods=['POST'])
def authentication():
    """Endpoint to authenticate an user.
    Returns:
        json: token and information from user.
    """
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        return generate_token(email, password)

    except Exception as error:
        return jsonify({'message': 'Internal server error'}), 500
    
@app.route('/trajectories/export')
@jwt_required()
def export_data_taxis():
    """Endpoint to export taxi data.
    Returns:
        xlsx: Taxi data.
    """
    try:
        arguments= request.args

        taxi_id= arguments.get("taxi_id", type=str)
        date= arguments.get("date", type=str)
        email= arguments.get("email", type=str)
        
        return (retrieve_data_xlsx(taxi_id, date, email))
    
    except Exception as error:
        return jsonify({'message': 'Internal server error'}), 500
    
@app.errorhandler(400)
def page_limit_not_valid():
    """Error handler for invalid page or limit values.

    Returns:
        json: Error message.
    """
    return jsonify({"error": {"code": 400, "message": "Bad Request"}}), 400

@app.errorhandler(500)
def internal_server_error():
    """Error handler for internal server errors.

    Returns:
        json: Error message.
    """
    return jsonify({"error": {"code": 500, "message": "Internal Server Error"}}), 500


if __name__ == '__main__':
    app.run(debug=True)



