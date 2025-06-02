import os

# Service URLs
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:8001')
RESTAURANT_SERVICE_URL = os.environ.get('RESTAURANT_SERVICE_URL', 'http://localhost:8002')

# Docker fallback URLs
USER_SERVICE_DOCKER_URL = 'http://user-service:8000'
RESTAURANT_SERVICE_DOCKER_URL = 'http://restaurant-service:8000'

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/food_delivery')
DB_SCHEMA = os.environ.get('DB_SCHEMA', 'delivery_service')

# Port configuration
PORT = int(os.environ.get('PORT', 8003))
