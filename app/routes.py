from flask import jsonify, request
from app import app, supabase
import json

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json


        if isinstance(data.get("selected_dates"), list):
            data["selected_dates"] = json.dumps(data["selected_dates"])

        response = supabase.table("orders").insert(data).execute()

        if response.data:
            return jsonify({"message": "Order created!", "order": response.data}), 201
        return jsonify({"error": "Failed to create order"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
