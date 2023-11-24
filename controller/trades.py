from app import app
from db import db
from flask import Flask, jsonify, request
from datetime import datetime

my_history = db["history"]

@app.route("/controller")
def functionis():
    # we have to store trades when new added or removed and update when same ocurr
    
    return "hi from trades controller"

# Function to calculate duration in minutes
def calculate_duration_in_minutes(start_time, end_time):
    start_datetime = datetime.strptime(start_time, "%Y.%m.%d %H:%M")
    end_datetime = datetime.strptime(end_time, "%Y.%m.%d %H:%M")
    duration_in_minutes = (end_datetime - start_datetime).total_seconds() / 60
    return duration_in_minutes

# Function to perform trade analysis
def analyze_trades(trades):
    total_profit_loss = 0
    num_trades = len(trades)
    num_winning_trades = 0
    num_losing_trades = 0
    total_winning_profit = 0
    total_losing_loss = 0
    max_loss = float('-inf')
    num_days = 0

    for trade in trades:
        total_profit_loss += trade['currentProfit']

        if trade['currentProfit'] > 0:
            num_winning_trades += 1
            total_winning_profit += trade['currentProfit']
        else:
            num_losing_trades += 1
            total_losing_loss += trade['currentProfit']
            if trade['currentProfit'] < max_loss:
                max_loss = trade['currentProfit']

        if trade['isTradeClosed'].lower() == "true":
            num_days += 1

    win_rate = (num_winning_trades / num_trades) * 100 if num_trades > 0 else 0
    avg_profit = total_winning_profit / num_winning_trades if num_winning_trades > 0 else 0
    avg_loss = total_losing_loss / num_losing_trades if num_losing_trades > 0 else 0
    avg_no_of_trades_per_day = num_trades / num_days if num_days > 0 else 0
    avg_positive_day = total_winning_profit / num_days if num_days > 0 else 0
    avg_negative_day = total_losing_loss / num_days if num_days > 0 else 0

    return {
        "total_profit_loss": round(total_profit_loss, 2),
        "num_trades": num_trades,
        "num_winning_trades": num_winning_trades,
        "num_losing_trades": num_losing_trades,
        "win_rate": round(win_rate, 2),
        "avg_profit": round(avg_profit, 2),
        "avg_loss": round(avg_loss, 2),
        "max_loss": round(max_loss, 2),
        "num_days": num_days,
        "avg_no_of_trades_per_day": round(avg_no_of_trades_per_day, 2),
        "avg_positive_day": round(avg_positive_day, 2),
        "avg_negative_day": round(avg_negative_day, 2)
    }

# Route to handle trade analysis
@app.route('/analyze-trades', methods=['POST'])
def analyze_trades_route():
    try:
        request_data = request.json
        trades_data = request_data.get('trades')
        analysis_result = analyze_trades(trades_data)
        return jsonify(analysis_result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500