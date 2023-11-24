from flask import Flask, request, jsonify
# from flask_socketio import emit
import json
import math
import numpy as np
from pymongo import InsertOne, UpdateOne
from app import app 
from model.Trade_model import my_trades,Trade_model,my_history
import pandas as pd 
# from model.schema import Trade
from pymongo.errors import BulkWriteError
from pydantic import BaseModel
from typing import List


trading = Trade_model()
# socketio = SocketIO(app, cors_allowed_origins="*")
class Trade(BaseModel):
    # account_id: ObjectId  # Reference to Account document ID
    login:int
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

my_data = None
trades_to_save = None
users_to_save = None
recent_data= None
previous_trades_length = 0
client_connected = False


# @socketio.on('connect', namespace='/receive_data')
# def handle_connect():
#     global client_connected

#     # Check if a client has already connected
#     if not client_connected:
#         print('WebSocket client connected')
#         client_connected = True  # Set the flag to True
#     else:
#         print('WebSocket client reconnected')


# @socketio.on('disconnect', namespace='/receive_data')
# def handle_disconnect():
#     global client_connected
#     print('WebSocket client disconnected')
#     client_connected = False


# def send_trades():
#     global trades_to_save
#     if trades_to_save:
#         socketio.emit('new_trades', trades_to_save)
#         print("New trades emitted")


# def emit_data():
#     if my_data:
#         socketio.emit('my_data', my_data, namespace='/receive_data')
#         print('Data emitted successfully:')

def get_data():
    if recent_data:
     current_profit_values = [entry['currentProfit'] for entry in recent_data]
     print("get data running",current_profit_values) 
    return current_profit_values

@app.route('/datafromdb', methods=['GET'])
def store_data():
    trade = trading.get_recent_data_from_db(current_trades_length)
    if recent_data:
        # for trade in recent_data:
            # if trade.get("isTradeClosed") == "true":
            #     my_trades.insert_one(trade)
            #     print("trade closed is inserted succesfully")
            
        trades_to_insert = [trade for trade in recent_data if trade.get("isTradeClosed") == "true"]
        if trades_to_insert:
            my_trades.insert_many(trades_to_insert)
            print("trade closed is inserted succesfully")
    return jsonify(trade) 


@app.route('/calculate', methods=['GET'])
def calculation():
    # if my_data.get('trades'):
    #     data= [entry['currentProfit'] for entry in my_data.get('trades')]
    if recent_data:
        
     data = [entry['currentProfit'] for entry in recent_data]
     print("get data running",data)
    # calculations = my_data.get("calculations")
    print("calculation running",data)
    try:
        a = np.array(data)
        # print(type(a))
        mask_profit= a[a>0]
        mean_profit_avg_win =round(mask_profit.mean(), 4)
        mask_loss = a[a<0]
        mean_loss_avg_loss = round(mask_loss.mean(), 4)
        std_dev_winning_trades= round(np.std(mask_profit), 4)
        std_dev_losing_trades= round(np.std(mask_loss), 4)
        sum_of_profit= np.sum(mask_profit)
        sum_of_loss= abs(np.sum(mask_loss))
        profit_factor= round(sum_of_profit / sum_of_loss, 4)
        win_rate = len(mask_profit) / len(a)
        loss_rate = len(mask_loss) / len(a)
        expectancy = round((win_rate*mean_profit_avg_win) - (loss_rate*mean_loss_avg_loss), 4)
        grossP_L= round(sum_of_profit - sum_of_loss, 4)
        closedP_L = round(sum_of_profit + sum_of_loss, 4)   
        response = {
            # "calculations": calculations,
            "Expectancy": expectancy,
            "Profit Factor":profit_factor,
            "Average win": mean_profit_avg_win,
            "Average Loss": mean_loss_avg_loss,
            "Std. Dev. Winning Trades": std_dev_winning_trades,
            "Std. Dev. Losing Trades": std_dev_losing_trades,
            "Win Rates %": f"{win_rate * 100}%",
            "Loss Rates %": f"{loss_rate * 100}%",
            "Gross P/L": grossP_L,
            "Closed P/L": closedP_L
        }
        return jsonify(response)
        
        
    except Exception as e:
        error_response = {'error': 'Internal server error', 'message': str(e)}
        return jsonify(error_response), 500

@app.route('/receive_data', methods=['POST'])
def receive_data():
    global my_data
    global trades_to_save
    global previous_trades_length
    global recent_data
    global current_trades_length
    try:
        data = request.data.decode("utf-8")
        # print(data,'------data')
    
        new_data = json.loads(data)
        my_data = new_data
        print("recieved data running")
        # login =  new_data['account']
        # login_value = login[0]['Login']
        # print(login_value,'<--------login')
        trades_to_save = new_data['trades']
        current_trades_length = len(trades_to_save)
        
        if 'trades' in new_data:
             trade_schema = TradeList(**new_data)
             trades_to_save = trade_schema.trades
        # # print(pd.DataFrame(new_data['account']))
        print('trades --->>',trades_to_save)
        # Your existing code for checking trade length difference
        if current_trades_length != previous_trades_length:
            bulk_operations = []
            trades_to_remove = []

            # to Update trades in my_trades if they are present in trades_to_save using this
            for trade in trades_to_save:
                # Use the symbol to check if the trade already exists in the database
                existing_trade = my_trades.find_one({"symbol": trade.symbol})
                # print(existing_trade, 'existing trades')

                if existing_trade:
                    # Update to the trade
                    update_data = {
                        "$set": trade.dict(exclude={"symbol"})  # expecting symbol
                    }
                    bulk_operations.append(UpdateOne({"_id": existing_trade["_id"]}, update_data))
                else:
                    # Insert new trade
                    bulk_operations.append(InsertOne(trade.dict()))

            # to Move trades from my_trades to my_history if they are not present in trades_to_save using this
            trades_to_move_cursor = my_trades.find({"symbol": {"$nin": [trade.symbol for trade in trades_to_save]}})
            trades_to_move = list(trades_to_move_cursor)  #to Convert the cursor to a list
            print('trades to move --->>', trades_to_move)

            for trade_to_move in trades_to_move:
                # trade_to_move['login'] = login_value
                my_history.insert_one(trade_to_move)
                trades_to_remove.append(trade_to_move["_id"])
                print('trades moved to history table')

            # Remove trades from my_trades that were moved to my_history or updated
            if trades_to_remove:
                my_trades.delete_many({"_id": {"$in": trades_to_remove}})
                print('trades removed from my_trades')

            try:
                my_trades.bulk_write(bulk_operations, ordered=False)
                print("Trades inserted/updated successfully")
            except BulkWriteError as bwe:
                # Handle errors if needed
                print("Error:", bwe.details)
        #    my_trades.insert_many([trade.dict() for trade in trades_to_save])
            # Get the symbols of trades_to_save
        #     symbols_to_save = set(trade.symbol for trade in trades_to_save)
        #     print(symbols_to_save,'symbols to save')
        #     # Get the existing symbols in the database
        #     existing_symbols = set(doc['symbol'] for doc in my_trades.find({}, {'symbol': 1}))
        #     print(existing_symbols,'existing symbols')

        #     # Find the symbols that are already in the database and need to be updated
        #     symbols_to_update = existing_symbols.intersection(symbols_to_save)
        #     print(symbols_to_update,'symbols to update')

        #     # Update existing records
        #     for trade in trades_to_save:
        #         if trade.symbol in symbols_to_update:
        #             # Update the existing record based on the symbol
        #             my_trades.update_one({'symbol': trade.symbol}, {'$set': trade.dict()})
            
        #     # Find the symbols that are not in the database and need to be inserted
        #     symbols_to_insert = symbols_to_save - existing_symbols
        #     print(symbols_to_insert,'symbols to insert')

        # # Insert new records
        # new_trades = [trade.dict() for trade in trades_to_save if trade.symbol in symbols_to_insert]
        # if new_trades:
        #     my_trades.insert_many(new_trades)
        # print(new_trades,'new trades')

        # print("Trades updated:", len(symbols_to_update))
        # print("Trades inserted:", len(symbols_to_insert))
        previous_trades_length = current_trades_length
        # recent_data = trading.get_recent_data_from_db(current_trades_length)
        # print("recent data inside ---->",recent_data)
        # emit_data()
        response_data = {
            "message": "Data received",
            "data": "data is here"
        }
        return jsonify(response_data)
    except json.JSONDecodeError as e:
        print("JSON decoding error:", e)
        return "Invalid JSON data"
    except Exception as e:
        print("Error:", e)
        return "Error processing data" 



