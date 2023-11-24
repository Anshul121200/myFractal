from flask import Flask , request, jsonify
# from pymongo import MongoClient
from flask_cors import CORS
# from flask_socketio import SocketIO, emit
import json
import jwt


app = Flask(__name__)

CORS(app, origins="*")
# allowed_origins = ["http://localhost:3000"]
# CORS(app, origins=allowed_origins)
# socketio = SocketIO(app, cors_allowed_origins="*")

app.config["FLASK_ENV"] = "development"
# secret_key= app.config['SECRET_KEY']= 'MY_NAME_IS_YOU'
SECRET_KEY = "your_secret_key"

app.debug = True

# mongo_uri = "mongodb://localhost:27017"
# database_name = "fractalalpha"

# Load configuration from a separate file
app.config.from_pyfile('config.py')

my_data = None

@app.route("/")
def firstone():
    if my_data is not None:
      return my_data
  
def authenticate_request():
    # print("Authenticating request...")  # Add this line
    token = request.headers.get('Authorization')
        # Skip token check for the route that creates a new user
    print(request.endpoint,'<----endpoint')
    if request.endpoint == 'create_new_account':
        return
    elif request.endpoint =='sign_in':
        return
    elif request.endpoint =='get_trades_history':
        return
    
    if not token:
        return jsonify({"message": "Token is missing"}), 401
    # print(jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256']), 'tokennnn')
    
    try:
        #  ``print("Before decoding...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256']) 
        request.user = payload
        # print("After decoding:", payload)
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

@app.before_request
def before_request():
    return authenticate_request()
# @app.route("/receive_data", methods=['POST'])
# def data_recieved():
#     global my_data
#     data = request.data.decode("utf-8")
#     new_data = json.loads(data)
# #         my_data = new_data
#     response_data = {
#             "message": "Data received",
#             "data": new_data
#         }
#     my_data= response_data
#     return response_data

from controller import *
from data import *

if __name__ == '__main__':
    app.run()
# if __name__ == '__main__':
#     socketio.run(app, host='127.0.0.1', port=8000)