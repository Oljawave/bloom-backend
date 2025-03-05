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
    

from datetime import datetime
import re

@app.route('/orders/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    try:
        response = supabase.table("orders").select("*").eq("user_id", user_id).execute()

        if not response.data:
            return jsonify({"message": "Заказы не найдены"}), 404

        orders = []
        for order in response.data:
            formatted_dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m") for date in order["selected_dates"]]

            short_address = f'г. {order["city"]}, ул. {order["street"]} {order["building"]}'
            if order.get("apartment"):  
                short_address += f', кв. {order["apartment"]}'  

            phone_clean = re.sub(r"\D", "", order["phone"]) 
            if len(phone_clean) == 11:
                formatted_phone = f"+{phone_clean[0]} ({phone_clean[1:4]}) {phone_clean[4:7]}-{phone_clean[7:9]}-{phone_clean[9:11]}"
            else:
                formatted_phone = order["phone"]  

            orders.append({
                "order_id": order["id"],
                "dates": formatted_dates,
                "price_range": order["price_range"],
                "address": short_address,
                "phone": formatted_phone
            })

        return jsonify({"orders": orders}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/orders', methods=['GET'])
def get_all_orders():
    try:
        response = supabase.table("orders").select("*").execute()

        if not response.data:
            return jsonify({"message": "Заказы не найдены"}), 404

        orders = []
        for order in response.data:
            formatted_dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m") for date in order["selected_dates"]]

            phone_clean = re.sub(r"\D", "", order["phone"]) 
            if len(phone_clean) == 11:
                formatted_phone = f"+{phone_clean[0]} ({phone_clean[1:4]}) {phone_clean[4:7]}-{phone_clean[7:9]}-{phone_clean[9:11]}"
            else:
                formatted_phone = order["phone"]  

            orders.append({
                "order_id": order["id"],
                "dates": formatted_dates,
                "price_range": order["price_range"],
                "city": order["city"],
                "street_building": f'{order["street"]} {order["building"]}',
                "apartment": order.get("apartment", ""),
                "floor": order.get("floor", ""),
                "entrance": order.get("entrance", ""),
                "phone": formatted_phone
            })

        return jsonify({"orders": orders}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response
