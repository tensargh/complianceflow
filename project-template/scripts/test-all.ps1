# Run tests for all microservices (PowerShell)

Write-Host "🧪 Running tests for all Compliance Flow services..." -ForegroundColor Green

# Track results
$TotalServices = 0
$PassedServices = 0
$FailedServices = @()

# Function to run tests for a service
function Test-Service {
    param($ServiceName)
    
    $ServicePath = "services\$ServiceName"
    
    if (-not (Test-Path $ServicePath)) {
        Write-Host "⚠️  Skipping $ServiceName (directory not found)" -ForegroundColor Yellow
        return
    }
    
    $script:TotalServices++
    
    Write-Host "`n🔍 Testing $ServiceName..." -ForegroundColor Yellow
    
    Push-Location $ServicePath
    
    # Check if requirements.txt exists
    if (-not (Test-Path "requirements.txt")) {
        Write-Host "⚠️  No requirements.txt found for $ServiceName" -ForegroundColor Yellow
        Pop-Location
        return
    }
    
    # Run tests
    try {
        python -m pytest tests/ -v --tb=short --disable-warnings
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $ServiceName tests passed" -ForegroundColor Green
            $script:PassedServices++
        } else {
            Write-Host "❌ $ServiceName tests failed" -ForegroundColor Red
            $script:FailedServices += $ServiceName
        }
    }
    catch {
        Write-Host "❌ $ServiceName tests failed with error: $_" -ForegroundColor Red
        $script:FailedServices += $ServiceName
    }
    
    Pop-Location
}

# List of services to test
$Services = @(
    "user-service",
    "declaration-service",
    "form-service",
    "rule-engine-service",
    "review-service",
    "case-service",
    "notification-service",
    "analytics-service"
)

# Run tests for each service
foreach ($Service in $Services) {
    Test-Service -ServiceName $Service
}

# Summary
Write-Host "`n📊 Test Summary:" -ForegroundColor Yellow
Write-Host "Total services: $TotalServices" -ForegroundColor White
Write-Host "Passed: $PassedServices" -ForegroundColor Green
Write-Host "Failed: $($FailedServices.Count)" -ForegroundColor Red

if ($FailedServices.Count -gt 0) {
    Write-Host "`n❌ Failed services:" -ForegroundColor Red
    foreach ($Service in $FailedServices) {
        Write-Host "  - $Service" -ForegroundColor Red
    }
    exit 1
} else {
    Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
}












