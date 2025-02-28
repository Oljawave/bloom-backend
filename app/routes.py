from flask import jsonify, request, Response
import json
from app import app, supabase

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
