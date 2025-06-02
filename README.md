# Food Delivery App - Deployment Guide

This guide provides detailed instructions for deploying the Food Delivery App microservices using Render's free tier.

## Overview

The Food Delivery App consists of three microservices:
- **User Service**: Manages user accounts and orders
- **Restaurant Service**: Manages restaurants, menus, and order acceptance
- **Delivery Agent Service**: Manages delivery agents and order delivery status

## Prerequisites

1. A GitHub account
2. Your Food Delivery App code pushed to a GitHub repository
3. A Render account (sign up at [render.com](https://render.com))

## Deployment Options

### Option 1: Deploy using render.yaml (Blueprint)

The easiest way to deploy is using the Render Blueprint defined in `render.yaml`:

1. Push your code to GitHub (if you haven't already)
2. The `render.yaml` file is already configured with repository URL: `https://github.com/Danishh07/food-delivery-app`
3. Log in to your Render account
4. Go to the Dashboard and click "New" > "Blueprint"
5. Connect your GitHub repository
6. Render will automatically detect the `render.yaml` file and set up all services and databases

### Option 2: Manual Deployment

If you prefer to deploy each service manually:

#### 1. Create PostgreSQL Database

1. Log in to Render
2. Go to Dashboard > "New" > "PostgreSQL"
3. Set up a single database:
   - **Name**: `food-delivery-app-db`
   - **Database**: `food_delivery`
4. Choose the "Free" plan
5. Note the connection string for your database
   
> **Important**: Render's free tier only allows 1 active PostgreSQL database, so we'll use a single database with different schemas for each service.

#### 2. Deploy User Service

1. Go to Dashboard > "New" > "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `food-delivery-user-service`
   - **Root Directory**: `user-service` (the subdirectory containing the service)
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0:$PORT`
   - **Plan**: Free
4. Add environment variables:
   - `DATABASE_URL`: (Connection string from your database)
   - `DB_SCHEMA`: `user_service` (This will create a separate schema in the shared database)
   - `PORT`: `10000`
   - `RESTAURANT_SERVICE_URL`: `https://food-delivery-restaurant-service.onrender.com`
   - `DELIVERY_SERVICE_URL`: `https://food-delivery-agent-service.onrender.com`
5. Click "Create Web Service"

#### 3. Deploy Restaurant Service

1. Follow the same steps as above, but with these values:
   - **Name**: `food-delivery-restaurant-service`
   - **Root Directory**: `restaurant-service`   - Environment variables:
     - `DATABASE_URL`: (Same connection string as user service)
     - `DB_SCHEMA`: `restaurant_service` (Different schema for this service)
     - `PORT`: `10000`
     - `USER_SERVICE_URL`: `https://food-delivery-user-service.onrender.com`
     - `DELIVERY_SERVICE_URL`: `https://food-delivery-agent-service.onrender.com`

#### 4. Deploy Delivery Agent Service

1. Follow the same steps as above, but with these values:
   - **Name**: `food-delivery-agent-service`
   - **Root Directory**: `delivery-agent-service`   - Environment variables:
     - `DATABASE_URL`: (Same connection string as other services)
     - `DB_SCHEMA`: `delivery_service` (Different schema for this service)
     - `PORT`: `10000`
     - `USER_SERVICE_URL`: `https://food-delivery-user-service.onrender.com`
     - `RESTAURANT_SERVICE_URL`: `https://food-delivery-restaurant-service.onrender.com`

## Database Initialization

After deployment, you need to initialize your database schemas for each service:

1. For each service, go to its page in Render and open the "Shell" tab
2. For each service, run the following commands:
   ```bash
   python
   ```
   Then in the Python shell:
   ```python
   from database import engine
   from models import Base
   from sqlalchemy.schema import CreateSchema
   import sqlalchemy as sa
   
   # Create the schema first if it doesn't exist
   from config import DB_SCHEMA
   conn = engine.connect()
   if not conn.dialect.has_schema(conn, DB_SCHEMA):
       conn.execute(sa.schema.CreateSchema(DB_SCHEMA))
       conn.commit()
   
   # Create tables in the schema
   Base.metadata.create_all(bind=engine)
   exit()
   ```

## Adding Test Data

After initializing your database schemas, you can add some test data. For example, to add a test delivery agent:

1. Go to the delivery-agent-service page in Render and open the "Shell" tab
2. Run the following commands:
   ```bash
   python
   ```
   Then in the Python shell:
   ```python
   from database import SessionLocal
   from models import DeliveryAgent
   
   # Create a test agent
   db = SessionLocal()
   test_agent = DeliveryAgent(
       name="Test Agent",
       email="test.agent@example.com",
       phone="+1234567890",
       vehicle_type="car",
       is_available=True
   )
   
   db.add(test_agent)
   db.commit()
   print(f"Created agent with ID: {test_agent.id}")
   exit()
   ```

## Testing the Deployment

1. Once all services are deployed, verify they're running by visiting:
   - `https://food-delivery-user-service-5ceu.onrender.com`
   - `https://food-delivery-restaurant-service-64xo.onrender.com`
   - `https://food-delivery-agent-service.onrender.com`

2. Each should return a health check response like: `{"status": "Service is running"}`

3. Use the Swagger UI for each service to test endpoints:
   - `https://food-delivery-user-service-5ceu.onrender.com/docs`
   - `https://food-delivery-restaurant-service-64xo.onrender.com/docs`
   - `https://food-delivery-agent-service.onrender.com/docs`

## Important Notes for Free Tier

- Free services on Render will spin down after 15 minutes of inactivity
- Initial requests after inactivity may take 30-60 seconds to respond
- You get 750 free hours per month across all services
- No credit card is required for the free tier
- Database storage is limited to 1GB in the free tier
- Render allows only 1 PostgreSQL database in the free tier
  - Our solution uses a single database with multiple schemas (one for each service)
  - Each service will create and manage its own schema automatically

## Troubleshooting

- Check service logs in the Render dashboard for each service
- Verify environment variables are set correctly
- Ensure database initialization completed successfully
- If services can't communicate, verify the service URLs in environment variables
