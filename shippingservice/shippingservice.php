<?php
require 'vendor/autoload.php';

use MongoDB\Client;
use MongoDB\BSON\UTCDateTime;

// MongoDB Atlas connection URI
$mongoUri = "mongodb+srv://p229221:22pseproject@projectcluster.amjkwy6.mongodb.net/";

// Initialize MongoDB Client
$client = new Client($mongoUri);
$database = $client->ShippingService;
$collection = $database->shipments;

// Save shipment to MongoDB
function save_shipment($order_id, $customer_id, $products, $shipping_address, $status) {
    global $collection;
    $shipment = [
        'order_id' => $order_id,
        'customer_id' => $customer_id,
        'products' => $products,
        'shipping_address' => $shipping_address,
        'status' => $status,
        'timestamp' => new UTCDateTime()
    ];

    $result = $collection->insertOne($shipment);
    return (string)$result->getInsertedId();
}

// Simulate shipment process
function process_shipment($order_id, $customer_id, $products, $shipping_address) {
    $shipment_status = "shipped";
    return save_shipment($order_id, $customer_id, $products, $shipping_address, $shipment_status);
}

// Send notification to Notification Service
function notify_user($order_id, $customer_id, $status, $shipping_address) {
    $notification_url = 'http://notification-service:3007/notify';

    $payload = [
        'userId' => $customer_id,
        'type' => 'shipping_updated',
        'orderId' => $order_id,
        'status' => $status
    ];

    $options = [
        'http' => [
            'header'  => "Content-type: application/json\r\n",
            'method'  => 'POST',
            'content' => json_encode($payload),
            'timeout' => 5
        ]
    ];

    $context  = stream_context_create($options);
    $result = @file_get_contents($notification_url, false, $context);

    if ($result === FALSE) {
        error_log("❌ Notification failed for order $order_id");
        return ["status" => "failed", "message" => "Notification failed"];
    }

    return json_decode($result, true);
}

// Main HTTP handler

// Set content type header once at the start before output
header('Content-Type: application/json');

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    // Health check endpoint
    echo json_encode(["status" => "shipping service is running"]);
    exit();
} elseif ($method === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);

    if (
        !isset($input['order_id']) ||
        !isset($input['customer_id']) ||
        !isset($input['products']) ||
        !isset($input['shipping_address'])
    ) {
        http_response_code(400);
        echo json_encode([
            "error" => "Invalid request format. Required: order_id, customer_id, products, shipping_address"
        ]);
        exit();
    }

    $order_id = $input['order_id'];
    $customer_id = $input['customer_id'];
    $products = $input['products'];
    $shipping_address = $input['shipping_address'];

    // Step 1: Process shipment
    $shipment_id = process_shipment($order_id, $customer_id, $products, $shipping_address);

    // Step 2: Notify user
    $notification_response = notify_user($order_id, $customer_id, "shipped", $shipping_address);

    echo json_encode([
        "status" => "success",
        "shipment_id" => $shipment_id,
        "order_id" => $order_id,
        "notified" => $notification_response
    ]);
} else {
    http_response_code(405);
    echo json_encode(["error" => "Invalid request method. Use POST or GET."]);
}
