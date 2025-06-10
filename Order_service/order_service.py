from flask import Flask, jsonify, request
from pymongo import MongoClient
from datetime import datetime
import requests
import logging
from flask_cors import CORS

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# MongoDB setup
MONGO_URI = "mongodb+srv://p229221:22pseproject@projectcluster.amjkwy6.mongodb.net/?retryWrites=true&w=majority&appName=ProjectCluster"
client = MongoClient(MONGO_URI)
db = client["OrderService"]
orders_collection = db["orders"]

# Save order in MongoDB
def save_order(customerid, customername, products, total_cost, payment_status):
    order = {
        "customer_id": customerid,
        "customer_name": customername,
        "products": products,
        "total_cost": total_cost,
        "payment_status": payment_status,
        "timestamp": datetime.utcnow()
    }
    result = orders_collection.insert_one(order)
    return str(result.inserted_id)

# Inventory check
def product_available(product_id, quantity):
    url = f"http://product-service:8000/inventory/{product_id}"
    params = {"quantity": quantity}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Checked inventory for product {product_id}: available={data['available']}")
        return data["available"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to check inventory for product {product_id}: {str(e)}")
        return False

def process_payment(id, name, cost, method="cod", payment_details=None):
    url = "http://localhost:5001/pay"# Change if Payment Service runs elsewhere
    payload = {
        "order_id": "order" + str(datetime.utcnow().timestamp()),  # or your actual order id
        "customer_id": id,
        "amount": cost,
        "method": method
    }
    if payment_details:
        payload["payment_details"] = payment_details

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "failed", "message": response.text}
    except Exception as e:
        return {"status": "failed", "message": str(e)}

# Real shipping call to Abdullah's PHP service
def shipping_service(order_id, customer_id, products, shipping_address):
    try:
        # This is Abdullah's shipping microservice
        url = "http://shippingservice:5001/ship"  # Docker internal DNS
        payload = {
            "order_id": order_id,
            "customer_id": customer_id,
            "products": products,
            "shipping_address": shipping_address
        }
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Shipping successful for order {order_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Shipping failed: {str(e)}")
        return {"status": "failed", "error": str(e)}

@app.route('/products', methods=['POST'])
def order_check_and_pay():
    data = request.get_json()

    # Input validation
    if not data or "customerid" not in data or "customername" not in data or "product" not in data or "shipping_address" not in data:
        return jsonify({"error": "Missing fields: customerid, customername, product, shipping_address"}), 400

    customer_id = data["customerid"]
    customer_name = data["customername"]
    products = data["product"]
    shipping_address = data["shipping_address"]

    if not products or not isinstance(products, list):
        return jsonify({"error": "Product list is missing or invalid"}), 400

    total_cost = 0
    product_list = []

    for product in products:
        product_id, name, quantity, price = product
        if not product_available(product_id, quantity):
            return jsonify({
                "status": "failed",
                "message": f"Product {product_id} not available in requested quantity."
            }), 400
        total_cost += quantity * price
        product_list.append({
            "id": product_id,
            "name": name,
            "quantity": quantity,
            "price": price
        })

    # Step 1: Process payment
    payment_response = process_payment(customer_id, customer_name, total_cost)

    # Step 2: Save Order
    order_id = save_order(customer_id, customer_name, product_list, total_cost, payment_response)

    # Step 3: Ship the order using Abdullah's service
    shipping_response = shipping_service(order_id, customer_id, product_list, shipping_address)

    # Final response
    return jsonify({
        "payment": payment_response,
        "order_id": order_id,
        "shipping": shipping_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)