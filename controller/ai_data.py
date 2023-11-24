from app import app
from model.ai_model import ai_model
from flask import jsonify , request


ai = ai_model()

@app.route('/api/save_ai_data', methods=['POST'])
def save_ai_data():
    try:
        data = request.get_json()
        result,status_code = ai.store_data(data)
        return jsonify(result),status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route('/api/get_data', methods=['GET'])
def get_data():
    try:
        user = getattr(request, 'user', None)
            
            # print(user,'user')
        if not user:
            return {"success": False, "message": "User not authenticated"}, 401
        
        account_id = request.args.get('account_id')
        result = ai.get_account_data(account_id)
        # print('result on api ----->', result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# @app.route('/api/send_Data')    