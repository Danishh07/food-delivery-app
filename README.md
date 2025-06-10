# Food Delivery App Microservices

A distributed food delivery system built with FastAPI and PostgreSQL, following a microservice architecture.

## Project Overview

This project implements a food delivery system with three microservices:
- **User Service**: Manages user accounts and orders
- **Restaurant Service**: Manages restaurants, menus, and order acceptance
- **Delivery Agent Service**: Manages delivery agents and order delivery status

## Live Demo

Access the deployed microservices:
- User Service: [https://food-delivery-user-service-5ceu.onrender.com](https://food-delivery-user-service-5ceu.onrender.com)
- Restaurant Service: [https://food-delivery-restaurant-service-64xo.onrender.com](https://food-delivery-restaurant-service-64xo.onrender.com)
- Delivery Agent Service: [https://food-delivery-agent-service.onrender.com](https://food-delivery-agent-service.onrender.com)

API documentation (Swagger UI) is available at each service's `/docs` endpoint.

## Technologies Used

- **FastAPI**: High-performance web framework for building APIs
- **PostgreSQL**: Relational database for persistent storage
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation and settings management
- **Uvicorn/Gunicorn**: ASGI servers for production deployment
- **Docker**: Containerization for local development

## Architecture

This application follows a microservice architecture with:

1. **Independent Services**: Each service has its own database schema and API
2. **RESTful Communication**: Services communicate through HTTP requests
3. **Event-based Updates**: Order status changes trigger updates across services
4. **Shared Database**: In production, services use separate schemas on a single PostgreSQL instance

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   User Service  │◄───►│Restaurant Service│◄───►│ Delivery Service│
│   (Port 8000)   │     │   (Port 8001)   │     │   (Port 8002)   │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         └─────────────►│                 │◄─────────────┘
                        │   PostgreSQL    │
                        │    Database     │
                        │                 │
                        └─────────────────┘
```

## Features

### User Service
- User registration and profile management
- Place food orders from available restaurants
- Track order status from placement to delivery
- View order history

### Restaurant Service
- Restaurant profile and menu management
- Receive and accept/reject incoming orders
- Update order preparation status
- Manage menu items and availability

### Delivery Agent Service
- Agent profile management and availability status
- Order assignment to available delivery agents
- Real-time order status updates
- Delivery route optimization

## API Endpoints

Each service exposes RESTful API endpoints. Explore the complete API documentation by visiting the Swagger UI at `/docs` for each service.

## Project Structure

```
food-delivery-app/
├── user-service/           # User account and order management
│   ├── main.py             # FastAPI application
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   └── database.py         # Database connection
│   
├── restaurant-service/     # Restaurant and menu management
│   ├── main.py             # FastAPI application
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   └── database.py         # Database connection
│   
└── delivery-agent-service/ # Delivery agent and delivery management
    ├── main.py             # FastAPI application
    ├── models.py           # Database models
    ├── schemas.py          # Pydantic schemas
    └── database.py         # Database connection
```

## Local Development

### Prerequisites
- Python 3.9+
- PostgreSQL
- Docker and Docker Compose (optional)

### Setup
1. Clone the repository
   ```bash
   git clone https://github.com/Danishh07/food-delivery-app.git
   cd food-delivery-app
   ```

2. Set up a PostgreSQL database

3. Install dependencies for each service
   ```bash
   cd user-service
   pip install -r requirements.txt
   # Repeat for other services
   ```

4. Run each service locally
   ```bash
   cd user-service
   uvicorn main:app --reload --port 8001
   # Run restaurant-service on 8002
   # Run delivery-agent-service on 8003
   ```

5. Alternatively, use Docker Compose
   ```bash
   docker-compose up
   ```

## Order Flow Example

1. User places order through User Service
2. Restaurant receives order through Restaurant Service
3. Restaurant confirms order
4. Delivery Agent is assigned through Delivery Agent Service
5. Delivery Agent picks up and delivers the order
6. Order status is updated throughout the process

## Links

- [User Service API](https://food-delivery-user-service-5ceu.onrender.com/docs)
- [Restaurant Service API](https://food-delivery-restaurant-service-64xo.onrender.com/docs)
- [Delivery Agent Service API](https://food-delivery-agent-service.onrender.com/docs)

## Author

- [Danish](https://github.com/Danishh07)
