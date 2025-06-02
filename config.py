import os

# Service URLs
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:8001')
RESTAURANT_SERVICE_URL = os.environ.get('RESTAURANT_SERVICE_URL', 'http://localhost:8002')
DELIVERY_SERVICE_URL = os.environ.get('DELIVERY_SERVICE_URL', 'http://localhost:8003')

# Docker service URLs (fallbacks)
USER_SERVICE_DOCKER_URL = 'http://user-service:8000'
RESTAURANT_SERVICE_DOCKER_URL = 'http://restaurant-service:8000'
DELIVERY_SERVICE_DOCKER_URL = 'http://delivery-agent-service:8000'

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/food_delivery')
DB_SCHEMA = os.environ.get('DB_SCHEMA', 'public')