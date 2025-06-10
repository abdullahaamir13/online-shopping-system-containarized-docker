const amqp = require('amqplib');
async function publishTestMessage() {
  try {
    const connection = await amqp.connect('amqp://localhost');
    const channel = await connection.createChannel();
    const queue = 'notification_queue';
    await channel.assertQueue(queue, { durable: true });
    const msg = JSON.stringify({
      type: 'shipping_updated',
      userId: 'user123',
      orderId: 'order456',
      status: 'shipped'
    });
    await channel.sendToQueue(queue, Buffer.from(msg));
    console.log('Sent shipping_updated event');
    await channel.close();
    await connection.close();
  } catch (error) {
    console.error('Error:', error);
  }
}
publishTestMessage();