# Compliance Flow Project Template

This template provides everything needed to build the Compliance Flow platform - a complete **production-ready** microservices architecture with comprehensive infrastructure, CI/CD pipelines, monitoring, security, and testing frameworks.

## 🎯 **What's Included**

### ✅ **Complete CI/CD Pipeline**
- GitHub Actions workflows for build, test, and deployment
- Automated security scanning (SAST, container scanning, dependency checks)
- Multi-environment deployment support (dev/staging/prod)
- Contract testing with Pact Broker

### ✅ **Enterprise Monitoring & Observability**
- Azure Application Insights with distributed tracing
- Comprehensive logging with correlation IDs
- Custom metrics and dashboards
- Real-time alerting (email, SMS, Teams)
- Health checks and readiness probes

### ✅ **Production Security**
- Web Application Firewall (WAF) with OWASP rules
- Azure Security Center integration
- Network security groups and private endpoints
- Secrets management with Azure Key Vault
- Rate limiting and DDoS protection

### ✅ **Comprehensive Testing Strategy**
- Unit tests with 80%+ coverage requirement
- Integration tests for API endpoints
- Contract testing with Pact
- Smoke tests for deployment validation
- Performance testing framework

### ✅ **Infrastructure as Code**
- Complete Terraform modules for Azure
- Multi-environment configurations
- Auto-scaling Container Apps
- Database backup and disaster recovery

## 🚀 Quick Setup

### Initialize Project
```bash
# Copy this template
cp -r project-template/ my-compliance-flow/
cd my-compliance-flow/

# Initialize git
git init
git add .
git commit -m "Initial project setup"

# Set up GitHub secrets (see Security Setup section)
```

### Start Development Environment
```bash
# Start all services with monitoring
docker-compose up -d

# Check status
docker-compose ps

# View logs with correlation tracking
docker-compose logs -f user-service

# Run tests
./scripts/test-all.sh
```

### Deploy Infrastructure
```bash
cd infrastructure/

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="environments/dev.tfvars"

# Deploy to Azure
terraform apply -var-file="environments/dev.tfvars"
```

## 📁 Project Structure

```
├── .github/workflows/      # CI/CD pipelines
│   ├── ci.yml             # Continuous integration
│   ├── cd.yml             # Continuous deployment
│   └── security-scan.yml  # Security scanning
├── infrastructure/         # Complete Terraform infrastructure
│   ├── modules/           # Reusable Terraform modules
│   │   ├── monitoring/    # Azure Monitor + App Insights
│   │   ├── security/      # WAF, Security Center, policies
│   │   ├── pact-broker/   # Contract testing infrastructure
│   │   └── networking/    # VNet, subnets, NSGs
│   └── environments/      # Environment-specific configs
├── services/              # 8 microservices with monitoring
│   └── user-service/      # Example service with full setup
│       ├── app/           # FastAPI application
│       ├── tests/         # Comprehensive test suite
│       │   ├── unit/      # Unit tests
│       │   ├── integration/ # API integration tests
│       │   └── contract/  # Pact contract tests
│       └── Dockerfile     # Production-ready container
├── tests/smoke/           # End-to-end smoke tests
├── shared/               # Common libraries and schemas
├── frontend/             # React application
├── docs/                 # PRD documents and API specs
├── scripts/              # Development and deployment scripts
├── .cursorrules          # AI development guidelines
└── docker-compose.yml    # Local development environment
```

## 🔐 Security Setup

### Required GitHub Secrets
Set up these secrets in your GitHub repository:

```bash
# Azure Authentication
AZURE_CREDENTIALS          # Service principal JSON
AZURE_CLIENT_ID            # Service principal client ID
AZURE_CLIENT_SECRET        # Service principal secret
AZURE_SUBSCRIPTION_ID      # Azure subscription ID
AZURE_TENANT_ID            # Azure tenant ID

# Infrastructure
TF_STATE_RESOURCE_GROUP     # Terraform state storage RG
TF_STATE_STORAGE_ACCOUNT    # Terraform state storage account
RESOURCE_GROUP_NAME         # Target resource group
CONTAINER_REGISTRY_NAME     # Azure Container Registry
CONTAINER_APPS_ENVIRONMENT_NAME # Container Apps environment

# Monitoring & Notifications
TEAMS_WEBHOOK_URL           # Microsoft Teams notifications
PACT_BROKER_URL            # Pact broker URL
PACT_BROKER_TOKEN          # Pact broker authentication

# URLs (set after deployment)
API_GATEWAY_URL            # API Gateway endpoint
FRONTEND_URL               # Frontend application URL
```

### Azure Service Principal Setup
```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "compliance-flow-github" \
  --role "Contributor" \
  --scopes "/subscriptions/{subscription-id}" \
  --sdk-auth

# Add additional permissions for security features
az role assignment create \
  --assignee {service-principal-id} \
  --role "Security Admin" \
  --scope "/subscriptions/{subscription-id}"
```

## 🤖 AI Development with Cursor

This project includes comprehensive `.cursorrules` for consistent AI-assisted development:

### Key Features
- **Service-specific patterns** for each microservice
- **Naming conventions** for consistency
- **Kafka event schemas** with standardized topics
- **Database migration patterns**
- **API design guidelines**
- **Security best practices**
- **Testing patterns** for unit, integration, and contract tests
- **Monitoring integration** with Application Insights

### Using Cursor Rules
```bash
# The .cursorrules file provides guidance for:
- Naming conventions (services, events, APIs)
- Code structure and patterns
- Database design with multi-tenancy
- Event-driven architecture
- Comprehensive testing approaches
- Security implementations
- Monitoring and observability
- Contract testing with Pact
```

## 🏗️ Service Development

### Developing Individual Services
Each service can be developed independently:

```bash
cd services/user-service/

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8001

# Run tests
pytest

# Database migrations
alembic upgrade head
```

### Service Structure
Every service follows the same pattern:
```
service-name/
├── Dockerfile                 # Container configuration
├── requirements.txt          # Python dependencies
├── alembic.ini              # Database migration config
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/                # Configuration and setup
│   ├── models/              # Database models
│   ├── schemas/             # API schemas
│   ├── api/routes/          # API endpoints
│   └── services/            # Business logic
├── migrations/              # Database migrations
└── tests/                   # Unit and integration tests
```

## 🔄 Event-Driven Architecture

### Kafka Topic Naming
Following `.cursorrules` conventions:
```
{service}.{entity}.{action}
Examples:
- user.user.created
- declaration.declaration.submitted
- review.review.completed
```

### Event Schema
All events follow this structure:
```json
{
  "event_id": "uuid",
  "event_type": "service.entity.action",
  "tenant_id": "uuid",
  "timestamp": "ISO8601",
  "version": "1.0",
  "data": {...}
}
```

## 🗄️ Database Management

### Per-Service Databases
Each service has its own database:
- `user_service`
- `declaration_service`
- `form_service`
- `rule_engine_service`
- `review_service`
- `case_service`
- `notification_service`
- `analytics_service`

### Migrations
```bash
# Create new migration
cd services/user-service/
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🔧 Configuration

### Environment Variables
Each service uses these patterns:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379

# Kafka
KAFKA_BOOTSTRAP_SERVERS=host:9092

# Service URLs
USER_SERVICE_URL=http://user-service:8000
```

### Local Development
```bash
# Environment file
cp .env.example .env

# Edit configuration
vim .env

# Restart services
docker-compose restart
```

## 🧪 Comprehensive Testing Strategy

### Test Types & Coverage
- **Unit Tests**: 80%+ coverage requirement, business logic validation
- **Integration Tests**: API endpoint testing with database
- **Contract Tests**: Service-to-service communication with Pact
- **Smoke Tests**: Post-deployment validation
- **Security Tests**: Automated vulnerability scanning

### Running Tests
```bash
# Run all test suites
./scripts/test-all.sh

# Run specific test types
cd services/user-service/

# Unit tests with coverage
pytest tests/unit/ -v --cov=app --cov-report=html

# Integration tests  
pytest tests/integration/ -v

# Contract tests (requires Pact Broker)
pytest tests/contract/ -v

# Run smoke tests after deployment
python tests/smoke/smoke_tests.py
```

### Contract Testing with Pact
```bash
# Consumer tests (generate contracts)
pytest tests/contract/test_user_consumer.py

# Provider verification (verify contracts)
pact-verifier --provider user-service \
              --pact-broker-base-url $PACT_BROKER_URL

# Publish contracts to broker
pact-broker publish pacts/ \
           --consumer-app-version 1.0.0 \
           --broker-base-url $PACT_BROKER_URL
```

### Test Configuration
```python
# conftest.py - Comprehensive test fixtures
@pytest.fixture
async def test_session():
    """Database session for testing."""
    
@pytest.fixture
def auth_headers():
    """Authentication headers for API tests."""
    
@pytest.fixture
def mock_kafka_producer():
    """Mocked Kafka producer for unit tests."""
```

## 📊 Enterprise Monitoring & Observability

### Azure Application Insights Integration
- **Distributed Tracing**: Track requests across microservices
- **Custom Metrics**: Business and technical metrics collection
- **Real-time Dashboards**: Pre-built monitoring workbooks
- **Smart Alerts**: Anomaly detection and threshold alerts

### Health & Readiness Checks
All services expose comprehensive health endpoints:
```bash
# Basic health check
GET /health

# Readiness check (database connectivity)
GET /health/ready  

# Liveness check (service responsiveness)
GET /health/live

# Metrics endpoint (Prometheus-compatible)
GET /metrics

# API documentation
GET /docs
```

### Structured Logging with Correlation
```python
# Automatic correlation ID tracking
logger.info(
    "User authentication successful",
    extra={
        "custom_dimensions": {
            "user_id": user.id,
            "tenant_id": user.tenant_id,
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
    }
)
```

### Monitoring Dashboard Access
- **Application Insights**: Azure Portal → Monitor → Application Insights
- **Log Analytics**: Query logs with KQL (Kusto Query Language)
- **Workbooks**: Pre-built dashboards for system overview
- **Alerts**: Configured for error rates, response times, availability

### Key Metrics Tracked
- Request volume and response times
- Error rates and exception details
- Database connection health
- Memory and CPU usage
- Business metrics (user registrations, declarations submitted)
- Security events (failed logins, suspicious requests)

## 🚢 CI/CD Deployment Pipeline

### Automated Deployment Flow
1. **Code Push** → Triggers GitHub Actions
2. **CI Pipeline**: Lint, test, security scan
3. **Build & Push**: Container images to registry
4. **Deploy Infrastructure**: Terraform updates
5. **Deploy Services**: Container Apps deployment
6. **Smoke Tests**: Validate deployment
7. **Notifications**: Teams alerts on status

### Environment Promotion
```bash
# Automatic deployment to dev on main branch push
git push origin main

# Manual deployment to staging
gh workflow run cd.yml -f environment=staging

# Manual deployment to production  
gh workflow run cd.yml -f environment=prod -f services=user-service,declaration-service
```

### Infrastructure Deployment
```bash
# Deploy complete infrastructure
cd infrastructure/

# Development environment
terraform apply -var-file="environments/dev.tfvars"

# Production with security features
terraform apply -var-file="environments/prod.tfvars" \
  -var="enable_ddos_protection=true" \
  -var="enable_backup=true" \
  -var="security_center_tier=Standard"
```

### Container Deployment
```bash
# Build and push all services
./scripts/build-images.sh --environment prod

# Deploy specific service
az containerapp update \
  --name user-service \
  --resource-group compliance-flow-prod \
  --image myregistry.azurecr.io/user-service:latest
```

### Rollback Strategy
```bash
# Quick rollback to previous version
az containerapp revision list --name user-service
az containerapp traffic set --name user-service \
  --revision-weight previous-revision=100 current-revision=0
```

## 🔐 Enterprise Security Features

### Web Application Firewall (WAF)
- **OWASP Rule Sets**: Protection against common attacks
- **Geo-blocking**: Block traffic from specific countries
- **Rate Limiting**: Prevent DDoS and abuse
- **Custom Rules**: Business-specific security policies

### Azure Security Center Integration
- **Continuous Assessment**: Security posture monitoring
- **Threat Detection**: Advanced threat protection
- **Compliance Monitoring**: SOC2, ISO27001, GDPR compliance
- **Security Alerts**: Real-time security incident notifications

### Network Security
- **Private Endpoints**: Database and storage isolation
- **Network Security Groups**: Layer 4 traffic filtering
- **DDoS Protection**: Standard/Premium tier options
- **TLS Everywhere**: End-to-end encryption

### Identity & Access Management
- **JWT Tokens**: RS256 signing with Azure AD integration
- **Role-based Access Control**: Granular permission system
- **Multi-tenant Isolation**: Complete tenant data separation
- **SSO Integration**: Azure Active Directory support

### Secrets & Key Management
- **Azure Key Vault**: Centralized secrets management
- **Managed Identities**: No credentials in code
- **Certificate Management**: Automated SSL/TLS certificates
- **Key Rotation**: Automated security key rotation

### Security Monitoring & Compliance
```bash
# View security alerts
az security alert list

# Check compliance status
az security assessment list

# Security scan results
az security sub-assessment list
```

### Data Protection
- **Encryption at Rest**: Customer-managed keys (CMK)
- **Encryption in Transit**: TLS 1.2+ minimum
- **Database Security**: Private endpoints, SSL required
- **Backup Encryption**: Geo-redundant encrypted backups

## 📚 Documentation

### Available Docs
- `docs/PRD_ComplianceFlow.md` - Main platform requirements
- `docs/PRD_{Service}.md` - Service-specific requirements
- `docs/Tech_Stack_Definition.md` - Technology choices
- `PROJECT_STRUCTURE.md` - Complete file organization

### API Documentation
- Swagger UI: `http://localhost:8001-8008/docs`
- ReDoc: `http://localhost:8001-8008/redoc`

## 🛠️ Development Guidelines

### Code Quality
- Black for code formatting
- Flake8 for linting
- MyPy for type checking
- 80%+ test coverage

### Git Workflow
- Feature branches
- Conventional commits
- Pull request reviews
- Automated CI/CD

### Cursor AI Usage
1. **Read `.cursorrules`** before starting development
2. **Follow naming conventions** for consistency
3. **Use provided patterns** for common tasks
4. **Update rules** when adding new patterns

## 🆘 Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check logs
docker-compose logs service-name

# Restart single service
docker-compose restart service-name
```

**Database connection issues:**
```bash
# Check PostgreSQL
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U dev -d user_service
```

**Kafka connection issues:**
```bash
# Check Kafka
docker-compose logs kafka

# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Useful Commands
```bash
# Reset everything
docker-compose down -v
docker-compose up -d

# View service URLs
docker-compose ps

# Execute commands in containers
docker-compose exec user-service bash
```

## 📈 Next Steps

1. **Review `.cursorrules`** - Understand AI development patterns
2. **Start with User Service** - Core authentication service
3. **Set up CI/CD** - Configure GitHub Actions
4. **Deploy to Azure** - Use Terraform for infrastructure
5. **Add monitoring** - Configure alerts and dashboards

---

**This template provides everything needed for enterprise-grade microservices development with AI assistance! 🚀**