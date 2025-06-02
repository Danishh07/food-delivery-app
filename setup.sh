#!/bin/bash

echo "🚀 Setting up Food Delivery App Backend..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Build and start the services
echo "🔨 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service health..."

# Check User Service
if curl -f http://localhost:8001/ > /dev/null 2>&1; then
    echo "✅ User Service is running on http://localhost:8001"
else
    echo "❌ User Service failed to start"
fi

# Check Restaurant Service
if curl -f http://localhost:8002/ > /dev/null 2>&1; then
    echo "✅ Restaurant Service is running on http://localhost:8002"
else
    echo "❌ Restaurant Service failed to start"
fi

# Check Delivery Agent Service
if curl -f http://localhost:8003/ > /dev/null 2>&1; then
    echo "✅ Delivery Agent Service is running on http://localhost:8003"
else
    echo "❌ Delivery Agent Service failed to start"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📚 API Documentation:"
echo "  - User Service: http://localhost:8001/docs"
echo "  - Restaurant Service: http://localhost:8002/docs"
echo "  - Delivery Agent Service: http://localhost:8003/docs"
echo ""
echo "📮 To test the APIs, import the Postman collection from postman_collection.json"
echo ""
echo "🛑 To stop the services, run: docker-compose down"
