const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const amqp = require('amqplib');
const mongoose = require('mongoose');
mongoose.set('strictQuery', true); // Suppress deprecation warning

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
  }
});

const PORT = process.env.PORT || 3007;
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://localhost';
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017/notifications';

app.use(express.json());

// MongoDB Schema for Notification Logs (optional, for persistence)
const notificationSchema = new mongoose.Schema({
  userId: String,
  type: String, // e.g., 'order_confirmation', 'shipping_update'
  message: String,
  createdAt: { type: Date, default: Date.now }
});
const Notification = mongoose.model('Notification', notificationSchema);

// Connect to MongoDB
mongoose.connect(MONGO_URL, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

// Connect to RabbitMQ and listen for events
async function connectRabbitMQ() {
  try {
    const connection = await amqp.connect(RABBITMQ_URL);
    const channel = await connection.createChannel();
    const queue = 'notification_queue';

    await channel.assertQueue(queue, { durable: true });
    console.log('Connected to RabbitMQ, listening on', queue);

    channel.consume(queue, async (msg) => {
      if (msg !== null) {
        const event = JSON.parse(msg.content.toString());
        await processNotification(event);
        io.emit("notification", event.message);
        channel.ack(msg);
      }
    });
  } catch (error) {
    console.error('RabbitMQ connection error:', error);
  }
}

// Process incoming events and send notifications
async function processNotification(event) {
  let message;
  switch (event.type) {
    case 'order_confirmed':
      message = `Order ${event.orderId} confirmed for user ${event.userId}`;
      break;
    case 'shipping_updated':
      message = `Order ${event.orderId} shipping status: ${event.status}`;
      break;
    default:
      console.log('Unknown event type:', event.type);
      return;
  }

  // Simulate sending notification (e.g., email or in-app)
  console.log(`Sending notification to user ${event.userId}: ${message}`);

  // Save notification to MongoDB (optional)
  const notification = new Notification({
    userId: event.userId,
    type: event.type,
    message
  });
  await notification.save();

  // Optionally, notify Front-End/User Service via REST API
  // Example: axios.post('http://user-service:3001/notifications', { userId, message });
}

// REST API to trigger notifications manually (for flexibility)
app.post('/notify', async (req, res) => {
  const { userId, type, orderId, status } = req.body;
  if (!userId || !type) {
    return res.status(400).json({ error: 'userId and type are required' });
  }

  const event = { userId, type, orderId, status };
  await processNotification(event);
  res.status(200).json({ message: 'Notification processed' });
});

// Health check endpoint
app.get('/health', (req, res) => res.status(200).json({ status: 'OK' }));

// Start the server
server.listen(PORT, () => {
  console.log(`Notification Service running on port ${PORT}`);
});
