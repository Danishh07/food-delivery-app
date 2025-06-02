# Heroku Deployment Guide

This guide explains how to deploy the Food Delivery App microservices to Heroku.

## Prerequisites

1. Heroku CLI installed
2. Git repository
3. Heroku account

## Deployment Steps

### 1. Create Heroku Apps

```bash
# Create apps for each service
heroku create food-delivery-user-service
heroku create food-delivery-restaurant-service  
heroku create food-delivery-agent-service

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev -a food-delivery-user-service
heroku addons:create heroku-postgresql:hobby-dev -a food-delivery-restaurant-service
heroku addons:create heroku-postgresql:hobby-dev -a food-delivery-agent-service
```

### 2. Set Environment Variables

```bash
# Get database URLs
heroku config:get DATABASE_URL -a food-delivery-user-service
heroku config:get DATABASE_URL -a food-delivery-restaurant-service
heroku config:get DATABASE_URL -a food-delivery-agent-service

# Set service URLs for inter-service communication
heroku config:set USER_SERVICE_URL=https://food-delivery-user-service.herokuapp.com -a food-delivery-restaurant-service
heroku config:set RESTAURANT_SERVICE_URL=https://food-delivery-restaurant-service.herokuapp.com -a food-delivery-user-service
heroku config:set DELIVERY_SERVICE_URL=https://food-delivery-agent-service.herokuapp.com -a food-delivery-restaurant-service
```

### 3. Create Procfiles

Each service needs a Procfile in its directory:

**user-service/Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**restaurant-service/Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**delivery-agent-service/Procfile:**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Deploy Services

```bash
# Deploy User Service
git subtree push --prefix=user-service heroku-user master

# Deploy Restaurant Service  
git subtree push --prefix=restaurant-service heroku-restaurant master

# Deploy Delivery Agent Service
git subtree push --prefix=delivery-agent-service heroku-delivery master
```

### 5. Initialize Database

Run the database initialization script on each service:

```bash
heroku run python -c "
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
" -a food-delivery-user-service
```

## Live Endpoints

After deployment, your services will be available at:

- User Service: https://food-delivery-user-service.herokuapp.com
- Restaurant Service: https://food-delivery-restaurant-service.herokuapp.com  
- Delivery Agent Service: https://food-delivery-agent-service.herokuapp.com

## Alternative: Railway Deployment

Railway is another good option for deployment:

1. Connect your GitHub repository to Railway
2. Create separate projects for each service
3. Set the root directory for each service
4. Add PostgreSQL database
5. Set environment variables

## Alternative: Render Deployment (Recommended for Free Tier)

Render offers free tier deployment that's suitable for this application:

### 1. Create Render Account and Set Up Services

1. Sign up at [Render](https://render.com/)
2. Click "New +" and select "Web Service" for each microservice
3. Connect your GitHub repository
4. Configure each service:
   - **Name**: `food-delivery-user-service`, `food-delivery-restaurant-service`, `food-delivery-agent-service`
   - **Root Directory**: Select the appropriate directory (e.g., `user-service`)
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### 2. Create PostgreSQL Databases

1. Click "New +" and select "PostgreSQL"
2. Configure each database:
   - **Name**: `food-delivery-user-db`, `food-delivery-restaurant-db`, `food-delivery-agent-db`
   - **Plan**: Free
3. Save the database connection strings for the next step

### 3. Set Environment Variables

Set these environment variables for each service:

**User Service**:
```
DATABASE_URL=[User Service PostgreSQL Connection String]
RESTAURANT_SERVICE_URL=https://food-delivery-restaurant-service.onrender.com
DELIVERY_SERVICE_URL=https://food-delivery-agent-service.onrender.com
PORT=10000
```

**Restaurant Service**:
```
DATABASE_URL=[Restaurant Service PostgreSQL Connection String]
USER_SERVICE_URL=https://food-delivery-user-service.onrender.com
DELIVERY_SERVICE_URL=https://food-delivery-agent-service.onrender.com
PORT=10000
```

**Delivery Agent Service**:
```
DATABASE_URL=[Delivery Agent Service PostgreSQL Connection String]
USER_SERVICE_URL=https://food-delivery-user-service.onrender.com
RESTAURANT_SERVICE_URL=https://food-delivery-restaurant-service.onrender.com
PORT=10000
```

### 4. Initialize Databases

After deployment, connect to your PostgreSQL databases and run:

```sql
CREATE TABLE IF NOT EXISTS users (
    -- User table schema
);

-- Run similar commands for other tables
```

Or use the Render shell to run Python initialization:

```
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
```

### 5. Important Notes for Free Tier

- Free services spin down after 15 minutes of inactivity
- Each service will spin up when requested (may take 30-60 seconds on first request)
- 750 free hours per month across all services
- No credit card required
