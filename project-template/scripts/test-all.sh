#!/bin/bash
# Run tests for all microservices

set -e

echo "🧪 Running tests for all Compliance Flow services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TOTAL_SERVICES=0
PASSED_SERVICES=0
FAILED_SERVICES=()

# Function to run tests for a service
run_service_tests() {
    local service_name=$1
    local service_path="services/$service_name"
    
    if [ ! -d "$service_path" ]; then
        echo -e "${YELLOW}⚠️  Skipping $service_name (directory not found)${NC}"
        return
    fi
    
    TOTAL_SERVICES=$((TOTAL_SERVICES + 1))
    
    echo -e "\n${YELLOW}🔍 Testing $service_name...${NC}"
    
    cd "$service_path"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        echo -e "${YELLOW}⚠️  No requirements.txt found for $service_name${NC}"
        cd - > /dev/null
        return
    fi
    
    # Run tests
    if python -m pytest tests/ -v --tb=short --disable-warnings; then
        echo -e "${GREEN}✅ $service_name tests passed${NC}"
        PASSED_SERVICES=$((PASSED_SERVICES + 1))
    else
        echo -e "${RED}❌ $service_name tests failed${NC}"
        FAILED_SERVICES+=("$service_name")
    fi
    
    cd - > /dev/null
}

# List of services to test
services=(
    "user-service"
    "declaration-service"
    "form-service"
    "rule-engine-service"
    "review-service"
    "case-service"
    "notification-service"
    "analytics-service"
)

# Run tests for each service
for service in "${services[@]}"; do
    run_service_tests "$service"
done

# Summary
echo -e "\n${YELLOW}📊 Test Summary:${NC}"
echo -e "Total services: $TOTAL_SERVICES"
echo -e "${GREEN}Passed: $PASSED_SERVICES${NC}"
echo -e "${RED}Failed: ${#FAILED_SERVICES[@]}${NC}"

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo -e "\n${RED}❌ Failed services:${NC}"
    for service in "${FAILED_SERVICES[@]}"; do
        echo -e "  - $service"
    done
    exit 1
else
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
fi



