# from schema import BodySchema 
from pydantic import ValidationError,BaseModel, Field
from db import db
from typing import Dict, List
from bson import ObjectId,json_util
from flask import jsonify,request
import pandas as pd

my_ai_data = db['ai_data']
my_accounts= db['metatrader-accounts']

class TDescription(BaseModel):
    Trade_Frequency: str
    Profit_Discrepancy: str
    Win_Rates: str
    Average_Profits: str
    Risk_Reward_Ratios_RRR: str
    Conclusion: str

class LongShortComparison(BaseModel):
    description: TDescription
    suggestion: str

class ResultsByDaysDescription(BaseModel):
    Monday: str
    Tuesday: str
    Wednesday: str
    Thursday: str
    Friday: str
    # Additional_Field_1: str
   

class ResultsByDays(BaseModel):
    description: ResultsByDaysDescription
    suggestion: str

class TradingDaysAnalysisDescription(BaseModel):
    Number_of_Days: str
    Avg_no_of_trades: str
    Positive_Days: str
    Avg_Positive_Day: str
    Negative_Days: str
    Avg_Negative_Day: str
    # Additional_Field_1: str

class TradingDaysAnalysis(BaseModel):
    description: TradingDaysAnalysisDescription
    suggestion: str

# class ResultsByInstrumentDescription(BaseModel):
#     description: str
#     # Additional_Field_1: str

class ResultsByInstrument(BaseModel):
    # description: ResultsByInstrumentDescription
    description: Dict[str, str]
    suggestion: str

class ResultsByPositionSizeDescription(BaseModel):
    Position_Size: str
    No_of_Trades: str
    Results: str
    High_Volume_Trades: str
    Profitable_Trades: str
    Losses: str
    Diversification: str
    # Additional_Field_1: str

class ResultsByPositionSize(BaseModel):
    description: ResultsByPositionSizeDescription
    suggestion: str

class ResultsByTradeDurationDescription(BaseModel):
    Duration: str
    No_of_Trades: str
    Results: str
    High_Frequency_Trading: str
    Profitable_Durations: str
    Losses_in_Longer_Durations: str
    One_Profitable_Trade: str
    # Additional_Field_1: str

class ResultsByTradeDuration(BaseModel):
    description: ResultsByTradeDurationDescription
    suggestion: str

class ResultsByOpenHourDescription(BaseModel):
    Hour: str
    No_of_Trades: str
    Results: str
    Peak_Trading_Hour: str
    Profitable_Hours: str
    Losses_During_Evening_Hours: str
    Mixed_Results: str
    # Additional_Field_1: str

class ResultsByOpenHour(BaseModel):
    description: ResultsByOpenHourDescription
    suggestion: str

class BodySchema(BaseModel):
    account_id: str
    long_short_comparison: LongShortComparison
    results_by_days: ResultsByDays
    trading_days_analysis: TradingDaysAnalysis
    results_by_instrument: ResultsByInstrument
    results_by_position_size: ResultsByPositionSize
    results_by_trade_duration: ResultsByTradeDuration
    results_by_open_hour: ResultsByOpenHour
    
class ai_model:
    @staticmethod
    def account_exists(account_id):
        try:
            # Check if the account_id exists in the 'accounts' collection
            if my_accounts.find_one({"account_id": account_id}):
                return {"status": True, "message": "Account found"}, 200
            else:
                return {"status": False, "message": "Account not found"}, 404
        except Exception as e:
            # Handle MongoDB errors
            print(f"Unexpected Error: {repr(e)}")
            return {"status": False, "message": "Internal server error","error":repr(e)}, 500

    @classmethod
    def store_data(cls, data):
        try:
            # account_exists, account_status = cls.account_exists(data["account_id"])
            
            # if not account_exists:
            #     return account_status
            user = getattr(request, 'user', None)
            
            # print(user,'user')
            if not user:
                return {"success": False, "message": "User not authenticated"}, 401
            account_id = data['account_id']

            # Check if the account_id exists in the 'accounts' collection
            if not my_accounts.find_one({"account_id": account_id}):
                return {"success": False, "message": "Account not found"}, 404
            
            print(data, '-- raw data --')   
            # Validate and parse incoming JSON data using Pydantic model
            body_schema = BodySchema(**data)

            # Save validated data to the database
            # Example: Save to MongoDB
            # my_ai_data.insert_one(body_schema.dict())
            print(body_schema,'body of parsed data')
            return {"success":True ,"message": "Data saved successfully"}, 200
        except ValidationError as e:
            # Log the validation error
            print(f"Validation Error: {repr(e)}")
            return {"success":False ,"error": "Validation error", "message": e.errors()}, 400  # Return validation errors with a 400 status code
        except Exception as e:
            # Log other unexpected errors
            print(f"Unexpected Error: {repr(e)}")
            return {"success":False ,"error": "Unexpected error", "message": str(e)}, 500  # Return unexpected errors with a 500 status code
    
    @classmethod
    def get_account_data(cls, account_id):
            try: 
                user = getattr(request, 'user', None)
            
                # print(user,'user')
                if not user:
                    return {"success": False, "message": "User not authenticated"}, 401
                if not isinstance(account_id, str):
                    return jsonify({"error": "Invalid account_id format"}), 400
                
                # Find all records for the given account_id
                # Convert the cursor to a list of dictionaries
                results_cursor = my_ai_data.find({"account_id": account_id})
                result_list = []
                
                for result in results_cursor:
                    # print(pd.DataFrame(result))
                    result['_id']= str(result['_id'])
                    result_list.append(result)
                    
                # Check if any results were found
                if result_list:
                    return result_list

                
                # result = my_ai_data.find_one({"account_id": account_id})
                # # print(result,'------result')
                # if result:
                #     result_dict = {key: result[key] for key in result if key != '_id'}
                #     return result_dict
                else:
                    return {"error": "Data not found for the given account_id"}, 404

            except Exception as e:
                return jsonify({"error": str(e)}), 500
            
            
            
