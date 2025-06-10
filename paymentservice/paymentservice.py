import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB setup (use environment variable for URI, or hardcode the URI for testing)
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")  # Default to local MongoDB if not set
client = MongoClient(mongo_uri)
db = client["PaymentService"]
payments = db["payments"]

@app.route('/pay', methods=['POST'])
def pay():
    try:
        # Getting the data from the request
        data = request.get_json()
        
        if not data or "order_id" not in data or "customer_id" not in data or "amount" not in data or "method" not in data:
            return jsonify({"error": "Missing required fields"}), 400

        order_id = data['order_id']
        customer_id = data['customer_id']
        amount = data['amount']
        method = data['method']
        payment_details = data.get('payment_details', {})

        # Default values for transaction status
        status = "failed"
        transaction_id = None

        # Handling different payment methods
        if method == "cod":
            status = "pending"
            transaction_id = "COD-" + order_id
            message = "Payment pending (Cash on Delivery)"

        elif method == "card":
            status = "completed"
            transaction_id = "CARD-" + order_id
            message = "Payment completed (Card)"

        elif method == "bank":
            status = "failed"
            transaction_id = None
            message = "Payment failed (Bank Transfer)"
        
        else:
            return jsonify({"error": "Invalid payment method"}), 400

        # Save payment details to MongoDB
        payments.insert_one({
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "method": method,
            "status": status,
            "transaction_id": transaction_id,
            "timestamp": datetime.utcnow()
        })

        # Returning a response to the client
        return jsonify({
            "status": status,
            "transaction_id": transaction_id,
            "message": message
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run Flask on port 5001 (accessible for testing)
    app.run(debug=True, host='0.0.0.0', port=5001)
