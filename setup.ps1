# Food Delivery App Setup Script for Windows

Write-Host "🚀 Setting up Food Delivery App Backend..." -ForegroundColor Green

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose is installed: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Build and start the services
Write-Host "🔨 Building and starting services..." -ForegroundColor Yellow
docker-compose up --build -d

Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check if services are running
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow

# Check User Service
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ User Service is running on http://localhost:8001" -ForegroundColor Green
} catch {
    Write-Host "❌ User Service failed to start" -ForegroundColor Red
}

# Check Restaurant Service
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Restaurant Service is running on http://localhost:8002" -ForegroundColor Green
} catch {
    Write-Host "❌ Restaurant Service failed to start" -ForegroundColor Red
}

# Check Delivery Agent Service
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8003/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Delivery Agent Service is running on http://localhost:8003" -ForegroundColor Green
} catch {
    Write-Host "❌ Delivery Agent Service failed to start" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 API Documentation:" -ForegroundColor Cyan
Write-Host "  - User Service: http://localhost:8001/docs" -ForegroundColor White
Write-Host "  - Restaurant Service: http://localhost:8002/docs" -ForegroundColor White
Write-Host "  - Delivery Agent Service: http://localhost:8003/docs" -ForegroundColor White
Write-Host ""
Write-Host "📮 To test the APIs, import the Postman collection from postman_collection.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛑 To stop the services, run: docker-compose down" -ForegroundColor Yellow
