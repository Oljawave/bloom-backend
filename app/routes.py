from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
from app import app, supabase


CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        response = supabase.table("orders").insert(data).execute()

        if response.data:
            return Response(
                json.dumps({"message": "Order created!", "order": response.data}, ensure_ascii=False),
                status=201,
                mimetype="application/json"
            )
        return jsonify({"error": "Failed to create order"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response
