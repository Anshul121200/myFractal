from app import app
from model.User_model import User_model
from flask import jsonify, request
# import 
import datetime
import re 

obj1= User_model()



@app.route("/createUser", methods=["POST"])
def new_user():
    user_data = request.get_json()
    response, status_code = obj1.create_user(user_data)

    return jsonify(response), status_code

    
# @app.route("/update_user/<user_id>", methods=["PUT"])
# def update_user(user_id):
#     data = request.get_json()
#     user_id= request.view_args.get('user_id')
#     response = obj1.update_user_data(user_id,data)

#     return jsonify(response)

# @app.route('/usersignup', methods=["POST"])
# def user_sign_up():
#     data =request.get_json()
#     response, status_code = obj1.create_or_update_user(data)
#     return jsonify(response), status_code

@app.route('/createnewaccount', methods=["POST"])
def create_new_account():
    data =request.get_json()
    print('request--->',data)
    response, status_code = obj1.create_new_user(data)
    return jsonify(response), status_code

@app.route('/signin', methods=["POST"])
def sign_in():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    response, status_code = obj1.sign_in_user(email, password)
    return jsonify(response), status_code

# @app.route('/update_accounts', methods=["PUT"])    # if using this route uncomment user_id

@app.route('/update_accounts/<string:user_id>', methods=["PUT"])
def update_user(user_id):
    # user_id = request.args.get('user_id')  # Specify the key for extracting the user_id
    response, status_code = obj1.create_new_account_for_user(user_id)
    return jsonify(response), status_code

@app.route('/logout', methods=['POST'])
def logout():
    email = request.form.get('email')  # assuming email is sent in the request data

    if not email:
        return {"success": False, "message": "Email not provided"}, 400

    # auth = YourAuthClass()  # Create an instance of your authentication class
    result = obj1.sign_out_user(email)

    return result

@app.route('/user/account_ids', methods=["GET"])
def accounts_of_user():
    user_id = request.args.get('user_id')
    # user_id = request.args.get('user_id')  # Specify the key for extracting the user_id
    response, status_code = obj1.find_users_account(user_id)
    return jsonify(response), status_code