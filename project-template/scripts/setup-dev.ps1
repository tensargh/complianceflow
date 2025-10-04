# Compliance Flow Development Environment Setup (PowerShell)

Write-Host "🚀 Setting up Compliance Flow development environment..." -ForegroundColor Green

# Check prerequisites
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is required but not installed. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is required but not installed. Please install Docker Desktop with Compose." -ForegroundColor Red
    exit 1
}

# Create environment file if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "env.example" ".env"
    Write-Host "✅ Created .env file. Please review and update values as needed." -ForegroundColor Green
}

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "data\postgres" | Out-Null
New-Item -ItemType Directory -Force -Path "data\redis" | Out-Null
New-Item -ItemType Directory -Force -Path "data\kafka" | Out-Null

# Pull latest images
Write-Host "🐳 Pulling Docker images..." -ForegroundColor Yellow
docker-compose pull

# Build custom images
Write-Host "🔨 Building service images..." -ForegroundColor Yellow
docker-compose build

# Start infrastructure services first
Write-Host "🏗️ Starting infrastructure services..." -ForegroundColor Yellow
docker-compose up -d postgres redis zookeeper kafka

# Wait for services to be ready
Write-Host "⏳ Waiting for infrastructure services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check if services are healthy
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow
docker-compose ps

# Start all microservices
Write-Host "🚀 Starting microservices..." -ForegroundColor Yellow
docker-compose up -d

# Wait for all services to start
Write-Host "⏳ Waiting for all services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Yellow
$services = @(
    @{name="user-service"; port=8001},
    @{name="declaration-service"; port=8002},
    @{name="form-service"; port=8003},
    @{name="rule-engine-service"; port=8004},
    @{name="review-service"; port=8005},
    @{name="case-service"; port=8006},
    @{name="notification-service"; port=8007},
    @{name="analytics-service"; port=8008}
)

foreach ($service in $services) {
    Write-Host "  Checking $($service.name) on port $($service.port)..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($service.port)/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $($service.name) is healthy" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  ⚠️ $($service.name) may not be ready yet" -ForegroundColor Yellow
    }
}

# Check frontend
Write-Host "🌐 Checking frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend is healthy" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Frontend may not be ready yet" -ForegroundColor Yellow
}

# Check API Gateway
Write-Host "🌉 Checking API Gateway..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ API Gateway is healthy" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ API Gateway may not be ready yet" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Access Points:" -ForegroundColor Cyan
Write-Host "  Frontend:      http://localhost:3000" -ForegroundColor White
Write-Host "  API Gateway:   http://localhost:8080" -ForegroundColor White
Write-Host "  User Service:  http://localhost:8001/docs" -ForegroundColor White
Write-Host "  Declaration:   http://localhost:8002/docs" -ForegroundColor White
Write-Host "  Form Service:  http://localhost:8003/docs" -ForegroundColor White
Write-Host "  Rule Engine:   http://localhost:8004/docs" -ForegroundColor White
Write-Host "  Review:        http://localhost:8005/docs" -ForegroundColor White
Write-Host "  Case Service:  http://localhost:8006/docs" -ForegroundColor White
Write-Host "  Notification:  http://localhost:8007/docs" -ForegroundColor White
Write-Host "  Analytics:     http://localhost:8008/docs" -ForegroundColor White
Write-Host ""
Write-Host "📚 Useful Commands:" -ForegroundColor Cyan
Write-Host "  View logs:     docker-compose logs -f [service-name]" -ForegroundColor White
Write-Host "  Restart:       docker-compose restart [service-name]" -ForegroundColor White
Write-Host "  Stop all:      docker-compose down" -ForegroundColor White
Write-Host "  Reset data:    docker-compose down -v" -ForegroundColor White
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green


