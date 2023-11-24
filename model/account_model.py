from enum import Enum
from db import db
from pydantic import Field, ValidationError, BaseModel
from bson import ObjectId ,json_util
import MetaTrader5 as mt5
import pandas as pd
from flask import request
from datetime import datetime

# mt5.initialize()
# mt5.login(login = 730357, server = "FXChoice-MetaTrader 5 Pro", password="yt0Uw7ddus3F")


my_account = db['metatrader-accounts']
my_history = db['history']


        


class BrokerEnum(str, Enum):
    mt4 = 'mt4'
    mt5 = 'mt5'

class Account(BaseModel):
    account_id: str  # Reference to User document ID
    login: int = Field(..., description="Login is required")
    broker: BrokerEnum = Field(..., description="Broker must be either 'mt4' or 'mt5'")
    password: str = Field(..., description="Password is required")
    server: str = Field(..., description="Server is required")
    
    
    #todo without mt5 login and saving account 
def mt5_login(login, server, password):
    # establish MetaTrader 5 connection to a specified trading account
    if not mt5.initialize(login=login, server=server, password=password):
        # error_code = mt5.last_error()
        error_message = f"Failed to log in. Error code: {mt5.last_error()}"
        # shut down connection to the MetaTrader 5 terminal
        mt5.shutdown()
        print(mt5.shutdown(),'<====shutdown')
        return error_message, 500  # 500 represents an internal server error
    else:
        return "Logged in successfully", 200

class Account_Model:
    def create_new_account(self, userdata):
        try:
            # Validate the incoming data against the Account model
            account_data = Account(**userdata)

            # Check if the account number already exists
            existing_login = my_account.find_one({"login": account_data.login})
            if existing_login:
                return {"success": False, "message": "Account number already exists"},404
            
            user = getattr(request, 'user', None)
            if not user:
                return {"success": False, "message": "User not authenticated"}, 401

            # Insert the validated data into the MongoDB collection
            # mt5.initialize()
            isLoggingIn= mt5_login(login = account_data.login, server = account_data.server, password=account_data.password)
            print(isLoggingIn[1],'isLoggedIn')
            # print(mt5.login(login = account_data.login, server = account_data.server, password=account_data.password),'login')
            if isLoggingIn[1] == 200:
                print('is logged in')
                # result = my_account.insert_one(account_data.dict())
                return {"success": True, "message": isLoggingIn[0]},401
            elif isLoggingIn[1] == 500:
                return {"success": False, "message": isLoggingIn[0]},500    
            else: 
                return {"success": False, "message": "Account not Exist"},401
            
            # if result.inserted_id:
            #     return {"success": True, "message": "Account created successfully"},200
            # else:
            #     return {"success": False, "message": "Failed to create account"
            
        except ValidationError as e:
            # Handle validation errors (invalid data)
            error_messages = []
            for error in e.errors():
                error_messages.append(f"{error['loc'][-1]}: {error['msg']}")
            return {"success": False, "message": error_messages, "error": "Validation error"},500
  
    # def get_trades_based_on_accounts():
    def get_trades(self,account_id, start_date, end_date):
        try:
            # user = getattr(request, 'user', None)
            
            # # print(user,'user')
            # if not user:
            #     return {"success": False, "message": "User not authenticated"}, 401
            
            # Find the corresponding account using the provided account_id
            account = my_account.find_one({"account_id": account_id})
            # print(account,'account')
            if account:
                # Extract the login from the account
                login = account.get("login")
                
                # Find trades in my_history collection based on login
                if start_date and end_date:
                    query = {
                        "$and": [
                            {"login": login},
                            {"closingTime": {"$gte": start_date, "$lte": end_date}}
                        ]
                    }
                else:
                    query = {"login": login}

                trades = list(my_history.find(query))                # print(trades, 'trades')
                if trades:
                    # Return the trades as JSON
                    # return json_util.dumps({"trades": trades}), 200
                    for trade in trades:
                        trade['_id'] = str(trade['_id'])
                    return {"trades":trades}, 200
                else:
                    # No trades found for the account
                    return {"success": False, "message": "No history trades for this account"}, 404
            else:
                # Account not found
                return {"success": False, "message": "Invalid account Id"}, 404

        except Exception as e:
            # Handle unexpected exceptions
            print(f"An unexpected error occurred: {str(e)}")
            return {"success": False, "message": "Internal Server Error"}, 500
       
    def get_trades_journal(self, account_id, start_date, end_date):
        try:
            user = getattr(request, 'user', None)

            print(user, 'user')
            if not user:
                return {"success": False, "message": "User not authenticated"}, 401

            # Find the corresponding account using the provided account_id
            account = my_account.find_one({"account_id": account_id})
            if account:
                # Extract the login from the account
                login = account.get("login")

                # Find trades in my_history collection based on login
                if start_date and end_date:
                    query = {
                        "$and": [
                            {"login": login},
                            {"closingTime": {"$gte": start_date, "$lte": end_date}}
                        ]
                    }
                else:
                    query = {"login": login}

                trades = list(my_history.find(query))

                if trades:
                    # Prepare a summary dictionary for each date
                    date_summary = {}
                    
                    for trade in trades:
                        trade['_id'] = str(trade['_id'])
                        # Extract the date from the currentTime field
                        # trade_date = datetime.strptime(trade['currentTime'], '%Y.%m.%d %H:%M').date()
                        trade_date_str = trade['currentTime']
                        trade_date_key = trade_date_str.split()[0]
                        # Update the date summary
                        if trade_date_key in date_summary:
                            date_summary[trade_date_key]['numOfTrades'] += 1
                            date_summary[trade_date_key]['result'] += trade['currentProfit']
                        else:
                            date_summary[trade_date_key] = {
                                'numOfTrades': 1,
                                'result': trade['currentProfit']
                            }
                    
                    return {"dateSummary": date_summary}, 200
                else:
                    # No trades found for the account
                    return {"success": False, "message": "No history trades for this account"}, 404
            else:
                # Account not found
                return {"success": False, "message": "Invalid account Id"}, 404

        except Exception as e:
            # Handle unexpected exceptions
            print(f"An unexpected error occurred: {str(e)}")
            return {"success": False, "message": "Internal Server Error"}, 500
        
    def get_trades_summary(self, account_id, start_date, end_date):
        try:
            user = getattr(request, 'user', None)

            # print(user, 'user')
            if not user:
                return {"success": False, "message": "User not authenticated"}, 401

            # Find the corresponding account using the provided account_id
            account = my_account.find_one({"account_id": account_id})
            if account:
                # Extract the login from the account
                login = account.get("login")

                # Find trades in my_history collection based on login and date range
                query = {
                    "$and": [
                        {"login": login},
                        {"closingTime": {"$gte": start_date, "$lte": end_date}}
                    ]
                }
                trades = list(my_history.find(query))

                if trades:
                    # Prepare a summary dictionary for each date
                    date_summary = {}

                    for trade in trades:
                        trade['_id'] = str(trade['_id'])
                        # Extract the date from the currentTime field
                        trade_date_str = trade['currentTime']
                        trade_date_key = trade_date_str.split()[0]  # Extracting '2023.11.10' from '2023.11.10 08:08'

                        # Update the date summary
                        if trade_date_key in date_summary:
                            date_summary[trade_date_key]['numOfTrades'] += 1
                            date_summary[trade_date_key]['result'] += trade['currentProfit']
                        else:
                            date_summary[trade_date_key] = {
                                'numOfTrades': 1,
                                'result': trade['currentProfit']
                            }

                    # Convert date_summary to the desired format
                    result_summary = []
                    for date_key, values in date_summary.items():
                        date_obj = datetime.strptime(date_key, '%Y.%m.%d')
                        formatted_date = date_obj.strftime('%Y.%m.%d')
                        result_summary.append({
                            'date': formatted_date,
                            'number_of_trades': values['numOfTrades'],
                            'total_profit': values['result']
                        })

                    return {"dateSummary": result_summary}, 200
                else:
                    # No trades found for the account
                    return {"success": False, "message": "No history trades for this account"}, 404
            else:
                # Account not found
                return {"success": False, "message": "Invalid account Id"}, 404

        except Exception as e:
            # Handle unexpected exceptions
            print(f"An unexpected error occurred: {str(e)}")
            return {"success": False, "message": "Internal Server Error"}, 500