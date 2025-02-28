from flask import jsonify, request
from app import app, supabase

@app.route('/')
def home():
    return jsonify({"message": "Bloom Backend работает!"})

# Получить заказ по ID
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    response = supabase.table("orders").select("*").eq("id", order_id).execute()
    if response.data:
        return jsonify(response.data[0])
    return jsonify({"error": "Order not found"}), 404

# Создать новый заказ
@app.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    response = supabase.table("orders").insert(data).execute()
    
    if response.data:
        return jsonify({"message": "Order created!", "order": response.data}), 201
    return jsonify({"error": "Failed to create order"}), 400
