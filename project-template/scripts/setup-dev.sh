#!/bin/bash
# Compliance Flow Development Environment Setup

set -e

echo "🚀 Setting up Compliance Flow development environment..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ Created .env file. Please review and update values as needed."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/kafka

# Pull latest images
echo "🐳 Pulling Docker images..."
docker-compose pull

# Build custom images
echo "🔨 Building service images..."
docker-compose build

# Start infrastructure services first
echo "🏗️ Starting infrastructure services..."
docker-compose up -d postgres redis zookeeper kafka

# Wait for services to be ready
echo "⏳ Waiting for infrastructure services to be ready..."
sleep 30

# Check if services are healthy
echo "🔍 Checking service health..."
docker-compose ps

# Initialize databases
echo "🗄️ Initializing databases..."
docker-compose exec -T postgres psql -U dev -d compliance_flow -c "SELECT 1;" || {
    echo "❌ PostgreSQL is not ready. Please check logs: docker-compose logs postgres"
    exit 1
}

# Start all microservices
echo "🚀 Starting microservices..."
docker-compose up -d

# Wait for all services to start
echo "⏳ Waiting for all services to start..."
sleep 20

# Check service health
echo "🏥 Checking service health..."
services=("user-service" "declaration-service" "form-service" "rule-engine-service" "review-service" "case-service" "notification-service" "analytics-service")

for service in "${services[@]}"; do
    port=$((8000 + ${#services[@]}))
    if [ "$service" = "user-service" ]; then port=8001; fi
    if [ "$service" = "declaration-service" ]; then port=8002; fi
    if [ "$service" = "form-service" ]; then port=8003; fi
    if [ "$service" = "rule-engine-service" ]; then port=8004; fi
    if [ "$service" = "review-service" ]; then port=8005; fi
    if [ "$service" = "case-service" ]; then port=8006; fi
    if [ "$service" = "notification-service" ]; then port=8007; fi
    if [ "$service" = "analytics-service" ]; then port=8008; fi
    
    echo "  Checking $service on port $port..."
    if curl -s "http://localhost:$port/health" > /dev/null; then
        echo "  ✅ $service is healthy"
    else
        echo "  ⚠️ $service may not be ready yet"
    fi
done

# Check frontend
echo "🌐 Checking frontend..."
if curl -s "http://localhost:3000" > /dev/null; then
    echo "✅ Frontend is healthy"
else
    echo "⚠️ Frontend may not be ready yet"
fi

# Check API Gateway
echo "🌉 Checking API Gateway..."
if curl -s "http://localhost:8080" > /dev/null; then
    echo "✅ API Gateway is healthy"
else
    echo "⚠️ API Gateway may not be ready yet"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "🔗 Access Points:"
echo "  Frontend:      http://localhost:3000"
echo "  API Gateway:   http://localhost:8080"
echo "  User Service:  http://localhost:8001/docs"
echo "  Declaration:   http://localhost:8002/docs"
echo "  Form Service:  http://localhost:8003/docs"
echo "  Rule Engine:   http://localhost:8004/docs"
echo "  Review:        http://localhost:8005/docs"
echo "  Case Service:  http://localhost:8006/docs"
echo "  Notification:  http://localhost:8007/docs"
echo "  Analytics:     http://localhost:8008/docs"
echo ""
echo "📚 Useful Commands:"
echo "  View logs:     docker-compose logs -f [service-name]"
echo "  Restart:       docker-compose restart [service-name]"
echo "  Stop all:      docker-compose down"
echo "  Reset data:    docker-compose down -v"
echo ""
echo "Happy coding! 🚀"


