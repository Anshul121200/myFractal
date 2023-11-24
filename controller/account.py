from app import app
from model.account_model import Account_Model
from flask import jsonify, request,Flask
from db import db 
from flask_cors import CORS


my_account= db['metatrader-accounts']

accounts= Account_Model()

@app.route("/create-account", methods=["POST"])
def create_MT5_account():
        user_data = request.get_json()
        response, status_code = accounts.create_new_account(user_data)
        # print(result)
        #  = result
        return jsonify(response), status_code


@app.route('/get_trades', methods=['GET'])
def get_trades_history():
    # Assuming accounts is an instance of the Account class
    # Get the account_id from the query parameters
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    response, status_code = accounts.get_trades(account_id, start_date, end_date)
    return jsonify(response), status_code


@app.route('/get_trades_journal', methods=['GET'])
def get_trades_journal():
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    # Call the new method for additional info
    response, status_code = accounts.get_trades_journal(account_id, start_date, end_date)
    return jsonify(response), status_code

@app.route('/trades_journal', methods=['GET'])
def get_trades_journal_summary():
    account_id = request.args.get('account_id')
    start_date = request.args.get('start_date')   # add % for spaces in the dates
    end_date = request.args.get('end_date')
    # Call the new method for additional info
    response, status_code = accounts.get_trades_summary(account_id, start_date, end_date)
    return jsonify(response), status_code