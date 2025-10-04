# Compliance Flow Project Structure

## Complete Project Layout

```
compliance-flow/
├── infrastructure/                 # Master Infrastructure as Code
│   ├── main.tf                    # Main Terraform configuration
│   ├── variables.tf               # Variable definitions
│   ├── outputs.tf                 # Output definitions
│   ├── terraform.tf               # Provider and backend configuration
│   ├── environments/              # Environment-specific configurations
│   │   ├── dev.tfvars             # Development environment
│   │   ├── staging.tfvars         # Staging environment
│   │   └── prod.tfvars            # Production environment
│   ├── modules/                   # Terraform modules
│   │   ├── networking/            # VNet, subnets, NSGs, private DNS
│   │   ├── database/              # PostgreSQL Flexible Server
│   │   ├── redis/                 # Azure Cache for Redis
│   │   ├── kafka/                 # Confluent Cloud Kafka
│   │   ├── container_registry/    # Azure Container Registry
│   │   ├── container_apps/        # Azure Container Apps Environment
│   │   ├── storage/               # Azure Storage Account
│   │   ├── key_vault/             # Azure Key Vault
│   │   ├── monitoring/            # Log Analytics + Application Insights
│   │   └── api_management/        # Azure API Management (prod only)
│   └── nginx/                     # API Gateway configuration
│       ├── nginx.conf
│       └── conf.d/
├── services/                      # Microservices
│   ├── user-service/              # Identity & Access Management
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic.ini
│   │   ├── app/
│   │   │   ├── main.py            # FastAPI application
│   │   │   ├── core/              # Core configuration
│   │   │   │   ├── config.py      # Settings
│   │   │   │   ├── database.py    # Database connection
│   │   │   │   ├── security.py    # Authentication
│   │   │   │   └── logging.py     # Logging setup
│   │   │   ├── models/            # SQLAlchemy models
│   │   │   │   ├── user.py
│   │   │   │   ├── business_unit.py
│   │   │   │   └── sso_config.py
│   │   │   ├── schemas/           # Pydantic schemas
│   │   │   │   ├── user.py
│   │   │   │   ├── auth.py
│   │   │   │   └── business_unit.py
│   │   │   ├── api/               # API routes
│   │   │   │   └── routes/
│   │   │   │       ├── auth.py
│   │   │   │       ├── users.py
│   │   │   │       └── business_units.py
│   │   │   ├── services/          # Business logic
│   │   │   │   ├── auth_service.py
│   │   │   │   ├── user_service.py
│   │   │   │   └── sso_service.py
│   │   │   ├── middleware/        # Custom middleware
│   │   │   └── utils/             # Utilities
│   │   ├── migrations/            # Alembic migrations
│   │   └── tests/                 # Unit and integration tests
│   ├── declaration-service/       # Declaration Management
│   │   ├── [Similar structure to user-service]
│   ├── form-service/              # Form Management
│   │   ├── [Similar structure to user-service]
│   ├── rule-engine-service/       # Decision Automation
│   │   ├── [Similar structure to user-service]
│   ├── review-service/            # Review Workflow
│   │   ├── [Similar structure to user-service]
│   ├── case-service/              # Investigation Management
│   │   ├── [Similar structure to user-service]
│   ├── notification-service/      # Communication
│   │   ├── [Similar structure to user-service]
│   └── analytics-service/         # Reporting & Analytics
│       ├── [Similar structure to user-service]
├── shared/                        # Shared libraries and schemas
│   ├── events/                    # Event schemas
│   │   ├── user_events.py
│   │   ├── declaration_events.py
│   │   ├── review_events.py
│   │   └── case_events.py
│   ├── database/                  # Shared database utilities
│   │   ├── base.py
│   │   ├── session.py
│   │   └── mixins.py
│   ├── auth/                      # Shared auth utilities
│   │   ├── jwt.py
│   │   ├── middleware.py
│   │   └── dependencies.py
│   ├── messaging/                 # Kafka utilities
│   │   ├── producer.py
│   │   ├── consumer.py
│   │   └── schemas.py
│   └── utils/                     # Common utilities
│       ├── logging.py
│       ├── config.py
│       └── exceptions.py
├── frontend/                      # React Frontend Application
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/            # Reusable components
│   │   │   ├── forms/
│   │   │   ├── layout/
│   │   │   ├── common/
│   │   │   └── declarations/
│   │   ├── pages/                 # Page components
│   │   │   ├── auth/
│   │   │   ├── declarations/
│   │   │   ├── reviews/
│   │   │   ├── cases/
│   │   │   └── analytics/
│   │   ├── services/              # API clients
│   │   │   ├── auth.ts
│   │   │   ├── declarations.ts
│   │   │   ├── reviews.ts
│   │   │   └── cases.ts
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── types/                 # TypeScript type definitions
│   │   ├── utils/                 # Utility functions
│   │   └── styles/                # Global styles
│   ├── public/                    # Static assets
│   └── tests/                     # Frontend tests
├── docs/                          # Technical documentation
│   ├── PRD_ComplianceFlow.md      # Main PRD
│   ├── PRD_UserService.md         # Service-specific PRDs
│   ├── [...other service PRDs]
│   ├── Tech_Stack_Definition.md   # Technology stack
│   ├── API_Documentation.md       # API documentation
│   ├── Deployment_Guide.md        # Deployment instructions
│   └── Architecture_Diagrams/     # System architecture diagrams
├── scripts/                       # Development and deployment scripts
│   ├── setup-dev.sh               # Development environment setup
│   ├── deploy.sh                  # Deployment script
│   ├── init-databases.sh          # Database initialization
│   ├── run-migrations.sh          # Database migration script
│   ├── build-images.sh            # Container image build script
│   └── test-all.sh                # Run all tests
├── .github/                       # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml                 # Continuous integration
│       ├── cd.yml                 # Continuous deployment
│       ├── security-scan.yml      # Security scanning
│       └── infrastructure.yml     # Infrastructure deployment
├── .env.example                   # Environment variables template
├── docker-compose.yml             # Local development environment
├── docker-compose.override.yml    # Local overrides
├── .gitignore                     # Git ignore rules
├── README.md                      # Project overview
└── PROJECT_STRUCTURE.md          # This file
```

## Infrastructure Overview

### Master Infrastructure (Terraform)

The infrastructure is designed as a complete Azure environment with:

- **Networking**: VNet with dedicated subnets for each service tier
- **Database**: PostgreSQL Flexible Server with private endpoints
- **Caching**: Azure Cache for Redis
- **Messaging**: Confluent Cloud Kafka
- **Compute**: Azure Container Apps for microservices
- **Storage**: Azure Blob Storage for file attachments
- **Security**: Azure Key Vault for secrets management
- **Monitoring**: Azure Monitor + Application Insights
- **API Gateway**: NGINX (dev) / Azure API Management (prod)

### Key Features

1. **Multi-Environment Support**: Separate configurations for dev/staging/prod
2. **Network Security**: Private endpoints and network security groups
3. **Secrets Management**: All secrets stored in Azure Key Vault
4. **Auto-Scaling**: Container Apps with automatic scaling
5. **Monitoring**: Comprehensive logging and metrics
6. **Backup & DR**: Automated backups with geo-redundancy (prod)

## Service Structure

Each microservice follows the same structure:

- **FastAPI** application with async support
- **SQLAlchemy** for database ORM
- **Alembic** for database migrations
- **Pydantic** for data validation
- **Pytest** for testing
- **Docker** containerization

## Development Workflow

1. **Local Development**: Use docker-compose for full local stack
2. **Testing**: Each service has comprehensive test suite
3. **CI/CD**: GitHub Actions for automated testing and deployment
4. **Infrastructure**: Terraform for infrastructure management
5. **Monitoring**: Structured logging and metrics collection

## Getting Started

1. **Setup Infrastructure**:
   ```bash
   cd infrastructure/
   terraform init
   terraform apply -var-file="environments/dev.tfvars"
   ```

2. **Start Local Development**:
   ```bash
   docker-compose up -d
   ```

3. **Access Services**:
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8080
   - Individual services: http://localhost:8001-8008

## Security Considerations

- All services use JWT authentication
- Network traffic is isolated using private endpoints
- Secrets are managed through Azure Key Vault
- Database connections use SSL/TLS
- Container images run as non-root users
- Network security groups restrict traffic flow

## Monitoring & Observability

- Structured logging with correlation IDs
- Application metrics via Azure Monitor
- Health check endpoints for all services
- Distributed tracing support
- Real-time dashboards and alerting












