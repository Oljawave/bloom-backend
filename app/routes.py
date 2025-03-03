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
    
    
@app.route('/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    try:
        response = supabase.table("orders").select("*").eq("user_id", user_id).execute()

        if not response.data:
            return jsonify({"message": "Заказы не найдены"}), 404

        orders = [
            {
                "order_id": order["id"],
                "dates": order["selected_dates"],
                "price_range": order["price_range"],
                "address": f'{order["city"]}, {order["street"]}, {order["building"]}, '
                           f'кв. {order["apartment"]}, подъезд {order["entrance"]}, этаж {order["floor"]}',
                "phone": order["phone"]
            }
            for order in response.data
        ]

        return jsonify({"orders": orders}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response
