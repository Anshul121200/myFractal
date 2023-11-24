from app import app
from db import db
import bcrypt
import jwt
import datetime
import re 
from bson import ObjectId
import random
import string
from flask import jsonify, request
from pydantic import BaseModel,ValidationError
# from schema import NewUser
import sys
# print(sys.path,'------')
from typing import List


my_Users= db['users']

class NewUser(BaseModel):
    # account_id: List[str] = []
    account_ids: List[str]
    first_name: str
    last_name: str
    email: str
    timezone: str
    is_Agreed_To_Terms: bool = None
    is_news_letter_subscribed: bool = None
    password: str
    confirm_password: str
    token: str



SECRET_KEY = "your_secret_key" 
user_schema = {
    "$jsonSchema":{
        "bsonType":"object",
        "required":["full_name","email","timezone","username","password","is_news_letter_subscribed","status"],
        "properties":{
            "first_name":{
                "bsonType":"string",
                "description":"must be a string first name"
            },
            "last_name":{
                "bsonType":"string",
                "description":"must be a string last name"
            },
            "email":{
                "bsonType":"email",
                "description":"enter your name"
            } 
        }
    }
}

# schema = {
#     "full_name": {
#         "type": "string",
#         "required": True,
#     },
#     "email": {
#         "type": "string",
#         "required": True,
#         "unique": True,
#     },
#     "username": {
#         "type": "string",
#         "optional": True,
#         "unique": True,
#     },
#     "password": {
#         "type": "string",
#         "optional": True,
#     },
#     "timezone": {
#         "type": "string",
#         "optional": True,
#     },
#     "is_news_letter_subscribed": {
#         "type": "boolean",
#         "default": False,
#     },
#     "status": {
#         "type": "string",
#     },
#     "role": {
#         "type": "string",
#         "required": True,
#         "enum": ["admin", "superAdmin", "vendor"],
#         "default": "vendor",
#     }
# }

class User_model:
    def create_new_user(self, user_data):
        try:
            # Extract data from user_data
            user_data.setdefault('account_ids', [])
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')
            email = user_data.get('email')
            timezone = user_data.get('timezone')
            is_Agreed_To_Terms = user_data.get('is_Agreed_To_Terms')
            is_news_letter_subscribed = user_data.get('is_news_letter_subscribed')
            password = user_data.get('password')
            confirm_password = user_data.get('confirm_password')

            while True:
                random_digits = ''.join(random.choices(string.digits, k=8))
                account_id = f"FA{random_digits}"
                user_data["account_ids"].append(account_id)
                # Check if the generated account ID already exists
                existing_account = my_Users.find_one({"account_id": account_id})
                if not existing_account:
                    break
            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return {"success": False, "message": "Invalid email address"}, 400

            # Check if email already existsc
            existing_email_user = my_Users.find_one({"email": email})
            if existing_email_user:
                return {"success": False, "message": "Email address already exists"}, 400

            # Password validation
            if (
                len(password) < 8 or
                not re.search(r'[a-z]', password) or
                not re.search(r'[A-Z]', password) or
                not re.search(r'[0-9]', password) or
                not re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
            ):
                return {"success": False, "message": "Password must meet specified criteria"}, 400

            # Check password and confirm_password match
            if password != confirm_password:
                return {"success": False, "message": "Password and confirm password do not match"}, 400

            # Hash the password before storing it
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            jwt_secret = SECRET_KEY

            # Create a payload for JWT
            payload = {
                'email': email,
                'password': password,
            }

            # Encode JWT token
            token = jwt.encode(payload, jwt_secret, algorithm='HS256')

            # Prepare new_user data
            new_user = {
                'account_ids':  [str(account_id)],
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'timezone': timezone,
                'is_Agreed_To_Terms': is_Agreed_To_Terms,
                'is_news_letter_subscribed': is_news_letter_subscribed,
                'password': hashed_password.decode('utf-8'),
                'confirm_password':password, 
                'token': token
            }
            
            try:
                user = NewUser(**new_user)
                # print(user,'<-----user')
                user_dict = user.dict()
                # user_id = my_Users.insert_one(user_dict).inserted_id   #uncomment this line to store user
                print(user_dict,'user_dict')
            except ValidationError as e:
                return {"success":False,'message': e.errors()}, 400
            print(new_user,'new--user')
            # user_id = my_Users.insert_one(new_user).inserted_id

            # Return success response
            return {'success': True, 'message': 'User created successfully', 'token': str(token), 'data': {"account_id": str(account_id)}}, 200

        except Exception as e:
            # Log the unexpected error for debugging
            print(f"Unexpected error in create_new_user: {e}")
            # Return a generic error response for unexpected errors
            return {'success': False, 'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500

    def sign_in_user(self, email, password):
        try:
            # Check if the email exists in the database
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return {"success":False,"message": "Invalid email address"}, 400
           
            user = my_Users.find_one({"email": email})
            if not user:
                return {"success": False, "message": "Email Doesn't Exists"}, 404
            
            user['_id'] = str(user['_id'])
            # Get the hashed password from the database
            hashed_password = user.get("password")

            # Verify the provided password against the hashed password
            if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return {"success": False, "message": "Invalid password"}, 401

            # Verify the user's token
            token = user.get("token")
            # print(token)
            if not token:
                return {"success": False, "message": "User token not found"}, 401

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                # print(payload,'<-----sign in payload')
                if payload["email"] != email:
                    return {"success": False, "message": "Token email does not match user's email"}, 401
            except jwt.ExpiredSignatureError:
                return {"success": False, "message": "Token has expired"}, 401
            except jwt.InvalidTokenError:
                return {"success": False, "message": "Invalid token"}, 401

            # You can perform additional actions for the successful login here
            
            return {"success": True, "message": "User logged in successfully", "data":{"token": token, "user":user }}, 200
        except Exception as e:
            # Handle unexpected errors here
            return {"success": False, "message": "An unexpected error occurred"}, 500

    #logout function
    def sign_out_user(self, email):
        try:
            # Find the user by email
            user = my_Users.find_one({"email": email})

            # Check if the user exists
            if not user:
                return {"success": False, "message": "User not found"}, 404

            # Invalidate the user's token (optional: generate a new one)
            # For simplicity, let's assume you always generate a new token on logout
            # new_token = generate_new_token()  # Implement a function to generate a new token

            # Update the user's token in the database
            # my_Users.update_one({"email": email}, {"$set": {"token": new_token}})

            return {"success": True, "message": "User logged out successfully"}, 200

        except Exception as e:
            # Handle unexpected errors here
            return {"success": False, "message": "An unexpected error occurred"}, 500

    # @classmethod
    def create_new_account_for_user(self,user_id):
        try:
            # Assuming you have a function to generate a unique account ID
            # account_id = generate_unique_account_id()
            while True:
                random_digits = ''.join(random.choices(string.digits, k=8))
                account_id = f"FA{random_digits}"
                # user_data["account_ids"].append(account_id)
                # Check if the generated account ID already exists
                existing_account = my_Users.find_one({"account_id": account_id})
                if existing_account:
                    return {"success": False, "message": "Generated account ID already exists"}, 400

                if not existing_account:
                    break
            # Check if the generated account ID already exists
            # existing_account = my_Users.find_one({"account_id": account_id})
            
            # Update the user in the database
            update_result = my_Users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"account_ids": account_id}}
            )
            print(update_result)
            if update_result.modified_count == 0:
                return {"success": False, "message": "User not found or account ID not added"}, 404

            # Return success response
            return {"success": True, "message": "New account created and added to user", "account_id": account_id}, 200

        except Exception as e:
            # Log the unexpected error for debugging
            print(f"Unexpected error in create_new_account_for_user: {e}")
            # Return a generic error response for unexpected errors
            return {'success': False, 'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500



    def find_users_account(self ,user_id):
        try:
            user = getattr(request, 'user', None)
            
            print(user,'user')
            if not user:
                return {"success": False, "message": "User not authenticated"}, 401
            
            # Assuming you have a MongoDB collection named 'my_users'
            # Replace 'my_users' with your actual collection name
            account_ids = my_Users.find_one({'_id':ObjectId(user_id)}, {'_id': 0, 'account_ids': 1})

            if not account_ids:
                return {"success": False, "message": f"User with ID {user_id} not found"}, 404

            
            return {"success": True, "message": "account ids fetched successfully", "accounts":account_ids}, 200

        except Exception as e:
            print(f"Unexpected error in finding users account ids: {e}")
            return {'success': False, 'error': 'Internal server error', 'message': f'An unexpected error occurred: {e}'}, 500       
    #     # Check if a user with the provided email or username already exists
    #     existing_user = my_Users.find_one({"$or": [{"email": user_data["email"]}, {"username": user_data.get("username") } ] })

    #     if existing_user:
    #         return {"message": "User with the same email or username already exists"}, 409  # Return a 409 Conflict status

    #     # Validate and preprocess user data
    #     if not re.match(r"[^@]+@[^@]+\.[^@]+", user_data["email"]):  # Validate email using a regular expression
    #         return {"message": "Invalid email address"}, 400  # Return a 400 Bad Request status

    #     if "password" in user_data:
    #         user_data["password"] = self.hash_password(user_data["password"])

    #     # Insert user data into the database
    #     my_Users.insert_one(user_data)

    #     # Generate a token and save it in the database
    #     token = jwt.encode({'email': user_data["email"], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
    #     my_Users.update_one({'email': user_data["email"]}, {'$set': {'token': token}})

    #     return {"message": "User created successfully", "token": token}, 201  # Return a 201 Created status

    # def hash_password(self, password):
    #     salt = bcrypt.gensalt()
    #     hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    #     return hashed_password
