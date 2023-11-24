from db import db
# from schema import Trade


my_trades= db["trades"]
my_history = db["history"]

from typing import List
from pydantic import BaseModel

class Trade(BaseModel):
    symbol: str
    volume: float
    openPrice: float
    takeProfit: float
    stopLoss: float
    currentPrice: float
    type: str
    ticket: int
    tradeTime: str
    closingTime: str
    isTradeClosed: bool
    currentProfit: float
    currentTime: str

class TradeList(BaseModel):
    trades: List[Trade]

class Trade_model:
    def trading_data():
        my_trades.find()
        return 
    def get_recent_data_from_db(self,limit):
        try:
            recent_data = my_trades.find().sort([('_id', -1)]).limit(limit)
            
            recent_data_list = list(recent_data)
            print("current trades are extracted successfully")
            if recent_data_list:
                # Iterate through the list and convert ObjectId to a string using json_util
                for record in recent_data_list:
                    record['_id'] = str(record['_id'])
                
                return recent_data_list
            else:
                return [{'message': 'No recent data available'}]
        except Exception as e:
            print("Error:", e)
            return [{'error': 'Internal server error'}]
