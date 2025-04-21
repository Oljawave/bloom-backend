from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import json
from app import app, supabase
import os
from dotenv import load_dotenv

load_dotenv()
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        response = supabase.table("orders").insert(data).execute()

        if response.data:

            order_id = response.data[0]["id"]
            
            send_telegram_notification(order_id)

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
                "phone": formatted_phone,
                "selected_flowers": order.get("selected_flowers", [])
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

            status_response = supabase.table("order_statuses").select("name_ru").eq("id", order["status_id"]).execute()
            status_name_ru = status_response.data[0]["name_ru"] if status_response.data else "Неизвестно"

            formatted_dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m") for date in order["selected_dates"]]

            phone_clean = re.sub(r"\D", "", order["phone"])
            if len(phone_clean) == 11:
                formatted_phone = f"+{phone_clean[0]} ({phone_clean[1:4]}) {phone_clean[4:7]}-{phone_clean[7:9]}-{phone_clean[9:11]}"
            else:
                formatted_phone = order["phone"]

            created_at_dt = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
            created_date = created_at_dt.strftime("%d.%m.%Y")
            created_time = created_at_dt.strftime("%H:%M:%S")

            orders.append({
                "order_id": order["id"],
                "user_id": order["user_id"],
                "status_id": order["status_id"],
                "status_name_ru": status_name_ru,
                "dates": formatted_dates,
                "comment": order["comment"],
                "price_range": order["price_range"],
                "city": order["city"],
                "street_building": f'{order["street"]} {order["building"]}',
                "apartment": order.get("apartment", ""),
                "floor": order.get("floor", ""),
                "entrance": order.get("entrance", ""),
                "phone": formatted_phone,
                "created_date": created_date,
                "created_time": created_time,
                "selected_flowers": order.get("selected_flowers", [])
            })

        return jsonify({"orders": orders}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

@app.route('/orders/by-id/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    try:
        response = supabase.table("orders").select("*").eq("id", order_id).execute()

        if not response.data:
            return jsonify({"message": "Заказ не найден"}), 404

        order = response.data[0]

        status_response = supabase.table("order_statuses").select("name_ru").eq("id", order["status_id"]).execute()

        if not status_response.data:
            return jsonify({"message": "Статус не найден"}), 404

        status_name_ru = status_response.data[0]["name_ru"]

        formatted_dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m") for date in order["selected_dates"]]

        short_address = f'г. {order["city"]}, ул. {order["street"]} {order["building"]}'
        if order.get("apartment"):
            short_address += f', кв. {order["apartment"]}'

        phone_clean = re.sub(r"\D", "", order["phone"])
        if len(phone_clean) == 11:
            formatted_phone = f"+{phone_clean[0]} ({phone_clean[1:4]}) {phone_clean[4:7]}-{phone_clean[7:9]}-{phone_clean[9:11]}"
        else:
            formatted_phone = order["phone"]

        created_at_dt = datetime.strptime(order["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
        created_date = created_at_dt.strftime("%d.%m.%Y")
        created_time = created_at_dt.strftime("%H:%M:%S")

        order_details = {
            "order_id": order["id"],
            "user_id": order["user_id"],
            "status_id": order["status_id"],
            "status_name_ru": status_name_ru, 
            "dates": formatted_dates,
            "comment": order["comment"],
            "price_range": order["price_range"],
            "city": order["city"],
            "street_building": f'{order["street"]} {order["building"]}',
            "apartment": order.get("apartment", ""),
            "floor": order.get("floor", ""),
            "entrance": order.get("entrance", ""),
            "phone": formatted_phone,
            "created_date": created_date,
            "created_time": created_time,
            "selected_flowers": order.get("selected_flowers", [])
        }

        return jsonify({"order": order_details}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    

@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.json
        new_status_id = data.get("status_id")

        if new_status_id is None:
            return jsonify({"error": "status_id не указан"}), 400

        response = supabase.table("orders").update({"status_id": new_status_id}).eq("id", order_id).execute()

        if response.data:
            return jsonify({"message": "Статус заказа обновлен", "order": response.data[0]}), 200
        else:
            return jsonify({"error": "Не удалось обновить заказ"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


import requests

cached_token = {
    "token": None,
    "expires_at": None
}

BLOOOOM_API_URL = os.getenv("BLOOOOM_API_URL")
BLOOOOM_USERNAME = os.getenv("BLOOOOM_USERNAME")
BLOOOOM_PASSWORD = os.getenv("BLOOOOM_PASSWORD")


def get_bloooom_token():
    try:
        if cached_token["token"]:
            return cached_token["token"]

        response = requests.post(f"{BLOOOOM_API_URL}/v1/employee/login", json={
            "username": BLOOOOM_USERNAME,
            "password": BLOOOOM_PASSWORD
        })
        print("Login response:", response.status_code, response.text)

        if response.status_code == 200:
            token = response.json().get("accessToken")
            cached_token["token"] = token
            return token
        else:
            raise Exception("Authentication failed")

    except Exception as e:
        print("Error during authentication:", e)
        return None



@app.route('/flowers', methods=['GET'])
def get_flowers():
    try:
        token = get_bloooom_token()
        if not token:
            return jsonify({"error": "Не удалось получить токен"}), 401

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BLOOOOM_API_URL}/v1/bouquet/branch/3"
        print("Fetching bouquets from:", url)
        response = requests.get(url, headers=headers)
        print("Bouquet response:", response.status_code, response.text)

        if response.status_code != 200:
            return jsonify({"error": "Ошибка при получении букетов"}), 500

        bouquets = response.json()
        result = []

        for flower in bouquets:
            result.append({
                "id": flower["id"],
                "name": flower["name"],
                "price": flower["price"],
                "image": flower.get("bouquetPhotos", [{}])[0].get("url", "https://via.placeholder.com/150")
            })

        return jsonify(result), 200

    except Exception as e:
        print("Exception in /flowers:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/flowers/<int:bouquet_id>', methods=['GET'])
def get_bouquet_by_id(bouquet_id):
    try:
        token = get_bloooom_token()
        if not token:
            return jsonify({"error": "Не удалось получить токен"}), 401

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BLOOOOM_API_URL}/v1/bouquet/{bouquet_id}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Букет не найден"}), response.status_code

        bouquet = response.json()

        image_url = bouquet.get("bouquetPhotos", [{}])[0].get("url", "https://via.placeholder.com/150")

        price = None
        if bouquet.get("branchBouquetInfo"):
            price = bouquet["branchBouquetInfo"][0].get("price")

        result = {
            "id": bouquet["id"],
            "name": bouquet["name"],
            "author": bouquet.get("author"),
            "style": bouquet.get("bouquetStyle"),
            "image": image_url,
            "price": price,
            "flowers": bouquet.get("flowerVarietyInfo", []),
            "additional_elements": bouquet.get("additionalElements", []),
        }

        return jsonify(result), 200

    except Exception as e:
        print("Exception in /flowers/<id>:", str(e))
        return jsonify({"error": str(e)}), 500
    

import requests
import os

def send_telegram_notification(order_id):
    try:
        TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
        TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
        ORDER_URL = os.getenv("ORDER_URL")

        message = f"""
<b>📦 Поступил новый заказ!</b>

🔹 <b>Заказ №{order_id}</b> успешно создан! 

🛍️ <b>Детали заказа:</b>
<a href="{ORDER_URL}">Перейти к заказу</a>

💬 <i>Пожалуйста, перейдите по ссылке, чтобы просмотреть все подробности и обработать заказ.</i>

🙏 <i>Спасибо за вашу работу и сотрудничество с нами!</i>

<em>С уважением, команда Blooooom</em>
        """

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }

        response = requests.post(url, data=payload)

        if response.status_code == 200:
            print(f"Уведомление успешно отправлено в Telegram для заказа {order_id}")
        else:
            print(f"Ошибка при отправке уведомления в Telegram: {response.text}")

    except Exception as e:
        print(f"Ошибка при отправке уведомления в Telegram: {str(e)}")




@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response
