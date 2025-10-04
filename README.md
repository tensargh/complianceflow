# Compliance Flow Platform

A multi-tenant SaaS platform for compliance declaration management, built with microservices architecture on Azure.

**Repository:** https://github.com/tensargh/complianceflow/

## 🚀 Quick Start

### Prerequisites
- Azure CLI installed and authenticated
- Terraform >= 1.5
- Docker Desktop
- Node.js 18+ (for frontend development)
- Python 3.11+ (for service development)

### 1. Copy Template Project
```bash
cp -r project-template/ compliance-flow/
cd compliance-flow/
```

### 2. Deploy Infrastructure
```bash
cd infrastructure/
terraform init
terraform plan -var-file="environments/dev.tfvars"
terraform apply -var-file="environments/dev.tfvars"
```

### 3. Start Local Development
```bash
cd ../
docker-compose up -d
```

### 4. Access Applications
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **Service Docs**: http://localhost:8001-8008/docs

## 📋 What You Have

### Documents Created
- **Tech Stack Definition** (`docs/Tech_Stack_Definition.md`): Final technology choices (Python, FastAPI, PostgreSQL, Kafka, React)
- **Master PRD** (`docs/prds/PRD_ComplianceFlow.md`): Complete platform requirements
- **8 Service PRDs** (`docs/prds/`): Individual microservice specifications
- **AI Workflow Guide** (`docs/AI_Assisted_Development_Workflow.md`): Complete SDLC with AI integration
- **Tool Stack Guide** (`docs/Recommended_Tool_Stack.md`): Free tier tools and MCP setup
- **Project Template** (`project-template/`): Complete development structure with examples

### Infrastructure
- **Multi-environment Terraform**: Dev, staging, production
- **Azure Services**: Container Apps, PostgreSQL, Redis, Kafka, Key Vault
- **Network Security**: Private endpoints, NSGs, VNet isolation
- **Monitoring**: Azure Monitor, Application Insights, structured logging

### Microservices (8 Total)
1. **User Service**: Identity & SSO management
2. **Declaration Service**: Declaration lifecycle
3. **Form Service**: Dynamic form builder
4. **Rule Engine Service**: Automated decision making
5. **Review Service**: Human review workflow
6. **Case Service**: Investigation management
7. **Notification Service**: Email & communication
8. **Analytics Service**: Reporting & dashboards

## 🏗️ Architecture Overview

```
Frontend (React) → API Gateway (NGINX) → Microservices (FastAPI)
                                       ↓
Event Bus (Kafka) ← → PostgreSQL + Redis + Azure Blob Storage
```

### Key Patterns
- **Event-Driven**: Kafka for inter-service communication
- **Multi-Tenant**: Row-level security with tenant isolation
- **API-First**: OpenAPI specs for all services
- **Container-Native**: Azure Container Apps with auto-scaling

## 🛠️ Development Workflow

### Each Microservice
1. **Independent Development**: Each service can be developed separately
2. **Cursor AI Compatible**: `.cursorrules` for consistent development
3. **Database per Service**: Isolated data with migrations
4. **API Documentation**: Auto-generated OpenAPI docs

### Local Development
```bash
# Start specific service
docker-compose up user-service postgres redis kafka

# Run tests
docker-compose exec user-service pytest

# View logs
docker-compose logs -f user-service
```

### Service Development
```bash
cd services/user-service/
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📚 Key Files to Review

### Platform Level
- `docs/Tech_Stack_Definition.md` - Technology decisions and rationale
- `docs/prds/PRD_ComplianceFlow.md` - Complete platform requirements
- `docs/AI_Assisted_Development_Workflow.md` - AI-assisted SDLC guide
- `docs/Recommended_Tool_Stack.md` - Tool selection (Jira, GitHub, GitHub Actions)
- `project-template/README.md` - Template usage guide

### Service Level (in template)
- `project-template/PROJECT_STRUCTURE.md` - Complete file organization
- `project-template/.cursorrules` - AI development guidelines
- `project-template/docker-compose.yml` - Local development environment
- `project-template/shared/events/` - Event schemas and patterns

## 🔧 Customization

### Environment Configuration
- Edit `infrastructure/environments/{env}.tfvars`
- Adjust service configurations in `docker-compose.yml`
- Modify `.cursorrules` for team-specific patterns

### Adding New Services
1. Copy service template structure
2. Add to `docker-compose.yml`
3. Create Terraform module if needed
4. Update `.cursorrules` with service-specific patterns

## 📊 Monitoring & Operations

### Health Checks
- All services expose `/health` endpoints
- Container Apps health probes configured
- Application Insights integration

### Logging
- Structured JSON logging
- Correlation IDs for request tracing
- Centralized in Azure Monitor

### Scaling
- Auto-scaling based on CPU/memory
- Manual scaling via Terraform variables
- Database connection pooling

## 🔐 Security

### Authentication
- Azure AD SSO integration
- JWT tokens with refresh rotation
- Role-based access control

### Network Security
- Private endpoints for all services
- Network security groups
- VNet isolation between environments

### Secrets Management
- Azure Key Vault for all secrets
- Managed identities for Azure services
- No secrets in code or containers

## 🚢 Deployment

### Environments
- **Dev**: Single-zone, smaller instances
- **Staging**: Production-like with reduced scale
- **Production**: Multi-zone, high availability

### CI/CD
- GitHub Actions workflows included
- Automated testing and deployment
- Infrastructure as Code validation

## 📈 Next Steps

See `TASKLIST.md` for detailed implementation tasks.

**Quick Start Path:**
1. ✅ **Setup Tools** - Jira & GitHub configured (see `docs/MCP_Setup_Guide.md`)
2. ✅ **Setup MCP** - GitHub & Atlassian MCP configured in Cursor
3. **Review Docs** - Read AI workflow guide and tech stack definition
4. **Copy Template** - Use project-template as starting point
5. **Begin Development** - Start with User Service following patterns

**For Consulting Portfolio:**
- Document your implementation journey
- Capture metrics (velocity, quality, time savings)
- Create video demos of AI-assisted development
- Build reusable templates from your work

## 📂 Repository Structure (Monorepo)

This is a **monorepo** containing all microservices, frontend, and infrastructure.

```
complianceflow/                       # Single GitHub repository
├── .github/workflows/               # GitHub Actions CI/CD (per-service)
├── docs/                            # All documentation
│   ├── prds/                        # Product Requirements (Master + 8 services)
│   ├── Tech_Stack_Definition.md    # Technology choices & rationale
│   ├── AI_Assisted_Development_Workflow.md  # AI-assisted SDLC guide
│   └── Recommended_Tool_Stack.md   # Tools: Jira, GitHub, MCPs
├── infrastructure/                  # Terraform IaC (to be populated)
├── services/                        # All 8 microservices (to be built)
│   ├── user-service/
│   ├── declaration-service/
│   ├── form-service/
│   ├── rule-engine-service/
│   ├── review-service/
│   ├── case-service/
│   ├── notification-service/
│   └── analytics-service/
├── frontend/                        # React app (to be built)
├── shared/                          # Common libraries & events
│   ├── events/                      # Event schemas
│   ├── auth/                        # Auth utilities
│   ├── monitoring/                  # Observability
│   └── types/                       # Shared types
├── scripts/                         # Dev & deployment scripts
├── project-template/                # Reference examples (from planning)
├── docker-compose.yml              # Local dev infrastructure
├── env.example                     # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
└── TASKLIST.md                     # Implementation roadmap
```

**Why Monorepo?** Faster development, atomic commits, easier to demo, free unlimited CI/CD (public repos), simpler dependencies.

## 🆘 Support

### Key Documentation
- **Getting Started:** This README + `TASKLIST.md`
- **PRDs:** `/docs/prds/` (Master + 8 service PRDs)
- **Tech Stack:** `/docs/Tech_Stack_Definition.md`
- **AI Workflow:** `/docs/AI_Assisted_Development_Workflow.md`
- **Tool Setup:** `/docs/Recommended_Tool_Stack.md` + `/docs/MCP_Setup_Guide.md`
- **MCP Setup:** ✅ GitHub & Atlassian MCP configured (see `.cursor/README.md`)
- **Examples:** `/project-template/` (reference patterns)

---

**Ready to build enterprise-grade compliance software with AI assistance! 🤖**


