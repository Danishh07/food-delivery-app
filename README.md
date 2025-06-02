# Food Delivery App Backend

A microservices-based food delivery application backend built with FastAPI, PostgreSQL, and Docker.

## Architecture

The application consists of 3 microservices:

1. **User Service** (Port 8001)
   - View available restaurants with menus
   - Place orders from restaurants
   - Rate completed orders and delivery agents
   - View order history

2. **Restaurant Service** (Port 8002)
   - Create and manage restaurants
   - Update menu items, pricing, and availability
   - Toggle restaurant online/offline status
   - Accept/reject incoming orders
   - Auto-assign available delivery agents to accepted orders

3. **Delivery Agent Service** (Port 8003)
   - Register delivery agents
   - Update agent availability status
   - Receive order assignments from restaurants
   - Update delivery status throughout the delivery process
   - View delivery statistics

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Swagger/OpenAPI (Auto-generated)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2

## Features Implemented

### Core Requirements ✅
- [x] User Service: Restaurant listing, order placement, rating system
- [x] Restaurant Service: Menu management, order processing, agent assignment
- [x] Delivery Agent Service: Status updates, order tracking
- [x] Microservices architecture with inter-service communication
- [x] PostgreSQL database with proper schema design
- [x] RESTful API endpoints for all operations

### Bonus Features ✅
- [x] Docker containerization for all services
- [x] Comprehensive API documentation
- [x] Database relationships and constraints
- [x] Error handling and validation
- [x] Postman collection for testing

## Quick Start

### Option 1: Using Docker (Recommended)

1. **Prerequisites:**
   - Docker Desktop installed and running
   - Git (to clone the repository)

2. **Setup:**
   ```bash
   # Clone the repository
   git clone <your-repo-url>
   cd food-delivery-app
   
   # Start all services
   docker-compose up --build
   ```

3. **Verify Services:**
   - User Service: http://localhost:8001/docs
   - Restaurant Service: http://localhost:8002/docs  
   - Delivery Agent Service: http://localhost:8003/docs

### Option 2: Manual Setup

1. **Prerequisites:**
   - Python 3.11+
   - PostgreSQL 15+
   
2. **Database Setup:**
   ```sql
   CREATE DATABASE food_delivery;
   -- Run the init.sql script to create tables and sample data
   ```

3. **Install Dependencies:**
   ```bash
   # For each service directory
   cd user-service && pip install -r requirements.txt
   cd ../restaurant-service && pip install -r requirements.txt  
   cd ../delivery-agent-service && pip install -r requirements.txt
   ```

4. **Set Environment Variables:**
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost:5432/food_delivery"
   ```

5. **Run Services:**
   ```bash
   # Terminal 1 - User Service
   cd user-service && uvicorn main:app --port 8001
   
   # Terminal 2 - Restaurant Service  
   cd restaurant-service && uvicorn main:app --port 8002
   
   # Terminal 3 - Delivery Agent Service
   cd delivery-agent-service && uvicorn main:app --port 8003
   ```

## API Endpoints

### User Service (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/restaurants` | Get all online restaurants with menus |
| POST | `/orders` | Place a new order |
| GET | `/orders/{order_id}` | Get order details |
| POST | `/orders/{order_id}/rate` | Rate an order |
| POST | `/agents/{agent_id}/rate` | Rate a delivery agent |

### Restaurant Service (Port 8002)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/restaurants` | Create a new restaurant |
| GET | `/restaurants/{restaurant_id}` | Get restaurant details |
| PUT | `/restaurants/{restaurant_id}/status` | Update online/offline status |
| POST | `/restaurants/{restaurant_id}/menu` | Add menu items |
| PUT | `/restaurants/{restaurant_id}/menu/{item_id}` | Update menu item |
| GET | `/restaurants/{restaurant_id}/menu` | Get restaurant menu |
| PUT | `/orders/{order_id}/accept` | Accept an order |
| PUT | `/orders/{order_id}/reject` | Reject an order |
| GET | `/orders/pending` | Get pending orders |

### Delivery Agent Service (Port 8003)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/agents` | Register delivery agent |
| GET | `/agents` | Get all agents |
| GET | `/agents/{agent_id}` | Get agent details |
| PUT | `/agents/{agent_id}/status` | Update availability |
| GET | `/agents/available` | Get available agents |
| PUT | `/orders/{order_id}/status` | Update delivery status |
| GET | `/orders/assigned/{agent_id}` | Get agent's assigned orders |
| GET | `/agents/{agent_id}/stats` | Get delivery statistics |

## Database Schema

The application uses a PostgreSQL database with the following main tables:

- **users**: Customer information
- **restaurants**: Restaurant details and status
- **menu_items**: Restaurant menu with pricing
- **delivery_agents**: Delivery agent profiles
- **orders**: Order information and status
- **order_items**: Items in each order
- **order_ratings**: Customer ratings for orders
- **agent_ratings**: Customer ratings for delivery agents

## Testing

### Using Postman
1. Import `postman_collection.json` into Postman
2. Set environment variables:
   - `user_service_url`: http://localhost:8001
   - `restaurant_service_url`: http://localhost:8002  
   - `delivery_service_url`: http://localhost:8003
3. Run the collection to test all endpoints

### Sample Workflow
1. **Setup**: Create restaurants and add menu items
2. **Order Flow**: 
   - User views restaurants → Places order → Restaurant accepts → Agent delivers
3. **Rating**: User rates the order and delivery agent

## Deployment

### Heroku Deployment
See `DEPLOYMENT.md` for detailed deployment instructions to Heroku, Railway, or Render.

### Production Considerations
- Use environment variables for database credentials
- Implement proper logging and monitoring  
- Add authentication and authorization
- Set up CI/CD pipeline
- Use a production WSGI server like Gunicorn

## Development

### Adding New Features
1. Define new API endpoints in the appropriate service
2. Add database models if needed
3. Update Pydantic schemas for validation
4. Add tests and documentation
5. Update the Postman collection

### Code Structure
```
service/
├── main.py          # FastAPI app and routes
├── models.py        # SQLAlchemy database models  
├── schemas.py       # Pydantic validation schemas
├── database.py      # Database connection setup
├── requirements.txt # Python dependencies
├── Dockerfile       # Container configuration
└── Procfile        # Heroku deployment config
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is created for educational purposes as part of a backend engineering assignment.
