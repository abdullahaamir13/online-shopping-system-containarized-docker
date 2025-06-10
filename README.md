# Online Shopping System Documentation

## Overview
This project is an e-commerce order processing system developed as part of the Software Engineering course at FAST National University of Computer and Emerging Sciences, Peshawar Campus (Spring 2025), under Instructor Usama Musharaf. It is a microservices-based application simulating an online shopping platform with the following services:
- **Front-End / User Service**: User-friendly interface.
- **Auth Service**: Manages user authentication and profiles.
- **Product Service**: Handles product listings and inventory.
- **Order Service**: Manages orders and payments.
- **Payment Service**: Processes transactions.
- **Shipping Service**: Manages shipping and tracking.
- **Notification Service**: Sends user notifications.

Each service is containerized using Docker and communicates via REST APIs.

## Technology Stack
| Component    | Technology                  |
|--------------|-----------------------------|
| Frontend     | HTML, CSS, JavaScript / React |
| Backend      | Node.js (Express) / Python (Flask/FastAPI), PHP |
| Database     | MongoDB                     |
| Containerization | Docker                  |
| Communication| REST APIs                   |

## System Architecture
The system follows a dependency chain:
1. **Auth Service**: Authenticates users.
2. **Order Service**: Checks inventory with Product Service.
3. **Product Service**: Confirms product availability.
4. **Payment Service**: Processes payments.
5. **Shipping Service**: Initiates shipment.
6. **Notification Service**: Sends updates to users.

## Teams
- **Team A (Frontend-User Service)**: Lead - Moiz Ghazanfar; Members - Faryal, Laiba, Neelam, Subhan Shah Bukhari.
- **Team B (Auth Service)**: Leads - Saud Nasir & Abdullah; Members - Abdul Hadi, Talha Zia, Asim Shakeel, Atta ur Rehman.
- **Team C (Product Service)**: Leads - Muhammad Abdullah & Rohail Nawaz; Members - Sultan Mehmood Mughal, Hafiz Zarar, Abdullah Bilal, Faran Ahmad.
- **Team D (Order Service)**: Leads - Mustafa & Hamza; Members - Awais Bin Abdul Khaliq, Faris Ahmed, Munhib Baig, Usman, Rohail Iqbal.
- **Team E (Payment Service)**: Leads - Saim Haider & Zaighum Zarawar; Members - Usman, Muzammil Waheed, Muhammad Hamza, Hafiz Muhammad Abdullah.
- **Team F (Shipping Service)**: Lead - Muhammad Abdullah Aamir; Members - Bakht Nasir, Abdul Wakeel, Ahmed Ali, Abdullah Khan, Hafiz Abdur Rehman.
- **Team G (Notification Service)**: Lead - Hashim Abdullah; Members - Misbah Ur Rehman, Imran Ullah, Ubaid Malik, Hammad Hassan, Aqsam Qureshi.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed.
- Git installed.
- MongoDB Atlas (or local MongoDB instance) configured with connection strings.

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/abdullahaamir13/online-shopping-system-containarized-docker.git
   cd online-shopping-system-containarized-docker
   ```
2. **Configure Environment Variables**:
   - Create a `.env` file in the root directory with:
     ```
     MONGO_URI=mongodb+srv://yourusername:yourpassword@clusterurl/?retryWrites=true&w=majority
     ```
   - Update with your MongoDB Atlas connection string.
3. **Build and Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   - This starts all services (e.g., Order Service on port 5000, Product Service on 8000, etc.).

### Usage
- Access the frontend at `http://localhost:3000` (adjust port based on your `docker-compose.yml`).
- Log in/register using the Auth Service.
- Browse products, add to cart, and proceed to checkout.

### Troubleshooting
- **400 Error**: Check for missing required fields in API payloads.
- **Notification Issues**: Verify `notification-service` URL and port (default 3008).
- **Connection Errors**: Ensure MongoDB and RabbitMQ (for Notification Service) are running.

## Future Improvements
- Add email verification for Auth Service.
- Implement authentication for admin endpoints in Product Service.
- Enhance Notification Service with email/SMS channels and rate limiting.

## Contributors
See team details above.
