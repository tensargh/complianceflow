# AI-Assisted Development Workflow
## A Complete SDLC Framework Using Cursor AI and MCPs

**Version:** 1.0  
**Last Updated:** October 4, 2025

---

## Executive Summary

This document outlines a comprehensive AI-assisted development workflow designed to demonstrate best practices for integrating AI tools (primarily Cursor AI and Model Context Protocol integrations) throughout the entire Software Development Lifecycle (SDLC). This workflow serves both as a practical implementation guide and as a proof-of-concept for AI development consulting services.

### Key Objectives
1. **Demonstrate AI Integration** - Show how AI can enhance productivity at every stage of development
2. **Create Reusable Templates** - Build microservice and frontend templates that follow this workflow
3. **Establish Best Practices** - Document patterns that teams can adopt
4. **Enable Autonomous Operations** - Progress toward AI agents handling routine development tasks

---

## Context: How We Got Here

### The PRD Foundation (Pre-Epic Work)

**Before breaking down epics into stories**, significant requirements work was completed using AI assistance:

#### Greenfield Project Approach
ComplianceFlow is a **new project built from scratch**. The Product Owner used AI to:

1. **Brainstorm and Refine Product Vision** (2-3 hours with AI vs. 1-2 weeks traditional)
   - Discussed business needs conversationally with AI
   - AI helped identify edge cases and requirements gaps
   - Refined scope through iterative conversation

2. **Create Main PRD** (`PRD_ComplianceFlow.md`)
   - 450+ lines of comprehensive requirements
   - 8 microservices identified
   - Event-driven architecture defined
   - Data models and service boundaries documented
   - **Time:** ~3-4 hours with AI vs. 2-3 weeks traditional

3. **Create Individual Service PRDs** (8 documents)
   - Detailed API specifications
   - Entity definitions with field types
   - Event schemas
   - Security and performance requirements
   - **Time per PRD:** 30-45 minutes with AI vs. 1-2 days traditional each

**Total PRD Creation Time:**
- **With AI:** ~6-8 hours for complete requirements suite
- **Traditional:** 3-4 weeks of full-time work
- **Time Saved:** ~75-80%

#### Alternative: Adding to Existing Platform

If this were an **existing platform** rather than greenfield:
- Start with existing documentation and architectural patterns
- Review existing service templates and coding standards
- Build new PRDs based on established patterns
- Reference existing event schemas and API conventions
- Ensure consistency with current tech stack

**Key Point:** Whether greenfield or brownfield, AI accelerates the requirements phase dramatically. For existing platforms, AI helps maintain consistency with established patterns even faster.

---

## Workflow Stages

### Stage 0: Requirements Foundation (Pre-Epic)
**Role:** Product Owner + Stakeholders  
**Tools:** Cursor AI  
**Time Savings:** 75-80% reduction in PRD creation time

This stage is often invisible but crucial. Before epics and stories, you need comprehensive requirements documentation.

**See `Context: How We Got Here` section above for details.**

---

### Stage 1: Product Management & Requirements
**Role:** Product Owner / Product Manager  
**Tools:** Cursor AI, Jira/ADO MCP  
**Time Savings:** 40-60% reduction in story preparation time

#### The Interactive Process

**Critical Mindset:** AI is your **co-pilot, not autopilot**. The Product Owner drives the process, validates outputs, and ensures business value. AI removes toil, not thinking.

**Starting Point:** Comprehensive PRDs already exist (created with AI assistance in Stage 0)

#### Detailed Workflow

##### 1. Epic & Story Planning Session

**Before AI:**
- Manually write epic descriptions
- Spend hours formatting user stories
- Struggle to maintain consistency
- Miss acceptance criteria
- Repeat work across similar stories

**With AI (Interactive Process):**

1. **Start the Conversation** (5-10 minutes)
   ```
   You: "Let's plan the Infrastructure Setup epic for our microservices platform.
   We need Terraform modules for Azure (PostgreSQL, Redis, Event Hubs, Key Vault),
   Docker Compose for local dev, and CI/CD pipelines."
   
   AI: *Generates initial epic breakdown with 8-10 stories*
   ```

2. **Review & Refine** (10-15 minutes)
   ```
   You: "Good start. Break the PostgreSQL story down more - we need 8 separate databases
   for our services. Also add a story for monitoring infrastructure."
   
   AI: *Updates story list, adds PostgreSQL details, creates monitoring story*
   ```

3. **Add Acceptance Criteria** (15-20 minutes)
   ```
   You: "For the Terraform Backend story, ensure we cover state locking,
   versioning, and RBAC permissions."
   
   AI: *Generates Gherkin scenarios for each requirement*
   ```

4. **Validate & Create** (5-10 minutes)
   - Review all stories one final time
   - AI creates them in Jira via MCP
   - You verify they're linked correctly

**Total Time:** 35-55 minutes for 11 detailed stories  
**Traditional Time:** 2-4 hours  
**Time Saved:** ~60%

##### 2. What AI Handles (The Toil)

✅ **Formatting** - Converts your thoughts into proper Gherkin syntax  
✅ **Boilerplate** - Adds Definition of Done, technical notes, dependencies  
✅ **Consistency** - Ensures all stories follow same template  
✅ **Linking** - Creates proper parent-child relationships in Jira  
✅ **Completeness** - Suggests acceptance criteria you might miss  

##### 3. What YOU Handle (The Thinking)

🧠 **Business Value** - What problem does this solve?  
🧠 **Priority** - What order should these be implemented?  
🧠 **Scope** - Is this story too big? Too small?  
🧠 **Validation** - Do these acceptance criteria actually test the requirement?  
🧠 **Dependencies** - What blockers exist? What sequence makes sense?  

##### 4. Iterative Refinement Example

**Initial Epic Breakdown:**
```
Epic: ECS-7 Infrastructure Setup
- Story 1: Setup Terraform
- Story 2: Create networking
- Story 3: Setup databases
```

**After PO Review:**
```
You: "Story 3 is too broad. We have 8 different databases, each needs
proper isolation, backup config, and connection strings in Key Vault."

AI: *Expands into detailed story with 4 scenarios covering server setup,
individual databases, backups, and performance configuration*
```

**After Second Review:**
```
You: "Good, but add a specific list of all 8 database names following
our naming convention."

AI: *Adds technical notes section listing all databases with proper naming*
```

This is **interactive refinement** - AI does heavy lifting, you steer direction.

##### 5. Documentation Generation

**Process:**
1. **Epic Description** (AI-generated, PO-reviewed)
   - Purpose and scope
   - Key deliverables
   - Success criteria
   - Dependencies

2. **User Stories** (AI-generated from conversations)
   - Gherkin acceptance criteria
   - Technical implementation notes
   - Definition of Done checklist
   - Story point estimates

3. **Implementation Sequence Document** (AI-generated from dependencies)
   - Dependency graph
   - Critical path analysis
   - Parallelization opportunities
   - Risk mitigation

**The PO's Role:**
- Provide high-level requirements and context
- Validate AI output for business accuracy
- Refine stories based on team capacity
- Ensure stories deliver actual value

##### 6. Real Example: ECS-7 Breakdown

**PO Input (5 minutes):**
"We need infrastructure for 8 microservices: User, Declaration, Form, Rule Engine, Review, Case, Notification, Analytics. Use Terraform for Azure. Include PostgreSQL, Redis, Kafka/Event Hubs, Key Vault, monitoring. Also need Docker Compose for local dev and CI/CD pipelines."

**AI Output (30 seconds):**
- 11 detailed stories
- 65 story points estimated
- Full Gherkin acceptance criteria
- Technical implementation notes
- Dependency mapping
- Risk items identified

**PO Refinement (20 minutes):**
- Adjusted story sequences
- Added specific Azure SKU requirements
- Clarified monitoring alert thresholds
- Validated deferred tasks (path filters)
- Approved for sprint planning

**Total: 25 minutes for sprint-ready backlog**

##### 7. Key Benefits for Product Owners

**Speed:**
- 40-60% faster story creation
- Consistent quality across all stories
- Reduced sprint planning meeting time

**Quality:**
- Comprehensive acceptance criteria
- Fewer missing requirements discovered later
- Better technical-business alignment

**Consistency:**
- All stories follow same template
- Dependencies clearly documented
- Risks captured systematically

**Collaboration:**
- Stories include enough technical detail for dev team
- Clear success criteria reduce ambiguity
- Documentation serves as team contract

##### 8. Anti-Patterns to Avoid

❌ **Blindly Accepting AI Output** - Always validate business value  
❌ **Skipping Reviews** - AI might miss domain-specific nuances  
❌ **Over-Automating** - Keep human judgment in prioritization  
❌ **Ignoring Team Feedback** - AI doesn't know your team's capacity  
❌ **Creating Stories in Isolation** - Involve tech lead in epic planning  

##### 9. Best Practices

✅ **Iterate Conversationally** - Treat AI like a junior PM who needs guidance  
✅ **Review Everything** - Especially acceptance criteria for accuracy  
✅ **Maintain Context** - Reference PRDs and prior decisions  
✅ **Document Rationale** - Capture WHY decisions were made  
✅ **Validate with Team** - Use sprint planning to get feedback  

**AI Value Add:**
- 40-60% faster story writing with consistent format
- Comprehensive Gherkin acceptance criteria generated automatically
- Automated linking between requirements and work items
- Quality checks on acceptance criteria completeness
- Boilerplate documentation handled automatically
- More time for strategy and stakeholder communication

---

### Stage 2: Technical Leadership & Architecture
**Role:** Tech Lead / Senior Developer / Architect  
**Tools:** Cursor AI, ADO/Jira MCP, Mermaid/PlantUML

#### Process
1. **Story Refinement**
   - Pull stories from ADO/Jira using MCP
   - Break down complex stories into technical tasks
   - Identify dependencies and technical risks
   - Estimate effort and complexity

2. **Technical Documentation**
   - **Architecture Diagrams** - System, component, and sequence diagrams
   - **API Specifications** - OpenAPI/Swagger documentation
   - **Data Models** - Database schemas and relationships
   - **Technical Design Documents (TDDs)**
   - **Integration Guides** - Service interaction patterns

3. **Test Planning**
   - Define test strategy (unit, integration, e2e)
   - Create test scenarios from acceptance criteria
   - Identify test data requirements
   - Define performance and security test requirements

4. **Task Creation**
   - Break stories into granular tasks
   - Create tasks in ADO/Jira with:
     - Clear descriptions
     - Links to documentation
     - Test requirements
     - Definition of Done

**AI Value Add:**
- Automated diagram generation from descriptions
- OpenAPI spec generation from requirements
- Test case generation from acceptance criteria
- Consistency checking across documentation

---

### Stage 3: Development
**Role:** Software Developer  
**Tools:** Cursor AI, Git, ADO/Jira MCP

#### Process
1. **Task Selection**
   - Pull assigned task from ADO/Jira using MCP
   - Review linked documentation and requirements
   - Clarify questions with tech lead if needed

2. **Branch Creation**
   - Create feature branch following naming convention:
     - `feature/{work-item-id}-{brief-description}`
     - Example: `feature/ADO-1234-add-user-authentication`
   - Link branch to work item automatically

3. **Implementation (One Task at a Time)**
   - Use Cursor AI to:
     - Generate initial code structure
     - Implement business logic
     - Follow established patterns from templates
     - Apply coding standards automatically
   
4. **Test Development**
   - Write unit tests alongside implementation
   - Generate test cases using AI
   - Ensure code coverage targets are met
   - Run tests locally before commit

5. **Documentation Updates**
   - Update inline code documentation
   - Add/update README sections
   - Update API documentation if applicable
   - Document any technical decisions

6. **Pull Request Creation**
   - Create PR with:
     - Descriptive title linked to work item
     - Summary of changes
     - Testing performed
     - Screenshots/videos for UI changes
   - Link PR to work item in ADO/Jira
   - Request reviewers

**AI Value Add:**
- Faster code generation following best practices
- Automated test generation
- Consistent code style
- Context-aware suggestions

---

### Stage 4: Code Review
**Role:** Senior Developer / Peer Developer  
**Tools:** Cursor AI, Git, ADO/Jira MCP

#### Process
1. **Pull Request Assignment**
   - Receive PR notification via ADO/Jira
   - Pull PR context using MCP
   - Load related work items and requirements

2. **AI-Assisted Review**
   - Use Cursor to:
     - Understand code changes in context
     - Check against architectural patterns
     - Verify test coverage
     - Identify potential issues
   - Review:
     - Code quality and maintainability
     - Security vulnerabilities
     - Performance implications
     - Adherence to standards

3. **Feedback & Iteration**
   - Provide constructive feedback
   - Suggest improvements using AI
   - Request changes or approve
   - Verify fixes before final approval

4. **Merge & Cleanup**
   - Merge approved PRs
   - Delete feature branches
   - Update work item status
   - Trigger CI/CD pipeline

**AI Value Add:**
- Faster code comprehension
- Pattern matching against best practices
- Security vulnerability detection
- Suggested improvements

---

### Stage 5: Automated Testing & Deployment
**Role:** DevOps / CI/CD Pipeline  
**Tools:** GitHub Actions / Azure Pipelines / Jenkins

#### Process
1. **Continuous Integration**
   - Automated build on PR creation
   - Run all automated tests:
     - Unit tests
     - Integration tests
     - End-to-end tests
     - Security scans
     - Code quality checks

2. **Deployment Pipeline**
   - Deploy to test environment
   - Run smoke tests
   - Performance testing
   - Deploy to staging
   - Production deployment (with approval)

3. **Feedback Loop**
   - Update work items with deployment status
   - Log metrics and monitoring data
   - Alert on failures or performance issues

---

### Stage 6: AI Agent Automation (Future State)
**Role:** Autonomous AI Agent  
**Tools:** Cursor AI, Custom Agents, ADO/Jira MCP

#### Process
1. **Story/Bug Intake**
   - Agent monitors work queue for eligible items
   - Identifies well-defined stories or triaged bugs
   - Pulls all context (requirements, docs, related code)

2. **Automated Analysis**
   - Reviews existing codebase
   - Analyzes documentation and patterns
   - Identifies affected components
   - Plans implementation approach

3. **Implementation**
   - Creates feature branch
   - Implements changes following patterns
   - Writes comprehensive tests
   - Updates documentation

4. **Submission**
   - Creates PR with detailed description
   - Flags for human review
   - Responds to review feedback
   - Iterates based on comments

5. **Quality Gates**
   - Human approval required for merge
   - Tech lead review for complex changes
   - Security review for sensitive changes

**AI Value Add:**
- Handle routine bug fixes autonomously
- Implement straightforward features
- Free human developers for complex work
- 24/7 development capacity

---

## MCP Integrations

### GitHub MCP
- **Availability:** ✅ Official MCP available from Anthropic
- **Repository:** `modelcontextprotocol/servers` (GitHub server)
- **Capabilities:**
  - Create/read/update issues and PRs
  - Repository management
  - File operations
  - Search code and issues
  - Manage branches and commits
  - Review PR comments

### Jira MCP
- **Availability:** ✅ Community MCPs available
- **Note:** Several community-developed MCPs exist; quality varies
- **Capabilities:**
  - Issue management (create, read, update)
  - Sprint management
  - Board views
  - Project queries
  - JQL (Jira Query Language) support

### Azure DevOps (ADO) MCP
- **Availability:** ⚠️ Limited community support
- **Note:** Less mature MCP ecosystem compared to GitHub/Jira
- **Alternative:** May require custom MCP development or REST API integration
- **Capabilities (if using REST API):**
  - Create/read/update work items
  - Query backlogs and boards
  - Manage pull requests
  - Access repositories
  - Pipeline integration

### Recommended Additional MCPs
- **Slack MCP** - Team notifications and collaboration (official)
- **Google Drive MCP** - Document management (official)
- **PostgreSQL/SQLite MCPs** - Database operations (official)
- **Filesystem MCP** - Local file operations (official)

---

## Quality Gates & Standards

### Definition of Ready (DoR) - Stories
- [ ] Clear business value statement
- [ ] Acceptance criteria defined
- [ ] Dependencies identified
- [ ] Estimated by team
- [ ] Architectural approach reviewed (if needed)

### Definition of Done (DoD) - Tasks
- [ ] Code implemented and follows standards
- [ ] Unit tests written (minimum 80% coverage)
- [ ] Integration tests for API endpoints
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] CI/CD pipeline passes
- [ ] Deployed to test environment
- [ ] Acceptance criteria verified

### Code Quality Standards
- Automated linting and formatting
- Static code analysis
- Security vulnerability scanning
- Performance profiling for critical paths
- Accessibility compliance (for frontend)

---

## Template Projects

### Microservice Template
**Technology Stack:** (Customize as needed)
- Runtime: Node.js/TypeScript or .NET or Go
- API: REST with OpenAPI specification
- Database: PostgreSQL/MongoDB
- Testing: Jest/xUnit
- CI/CD: GitHub Actions / Azure Pipelines

**Included:**
- Project structure following best practices
- Authentication/authorization boilerplate
- Database migrations setup
- Logging and monitoring
- Health check endpoints
- API documentation generation
- Docker configuration
- Test examples (unit, integration, e2e)

### Frontend Template
**Technology Stack:** (Customize as needed)
- Framework: React/Next.js or Vue or Angular
- State Management: Redux/Zustand/Pinia
- UI Components: Material-UI/Shadcn/Ant Design
- Testing: Jest + React Testing Library / Vitest
- Build: Vite/Webpack
- CI/CD: GitHub Actions / Azure Pipelines

**Included:**
- Component library setup
- Routing configuration
- API client setup
- Authentication flow
- State management patterns
- Testing utilities
- Storybook for component development
- Accessibility features

### Full-Stack Template
- Combined microservice + frontend
- Shared types/interfaces
- End-to-end testing setup
- Development environment (Docker Compose)
- Documentation site

---

## Metrics & Success Criteria

### Development Velocity
- Story completion rate
- Lead time (story → production)
- Cycle time (development → deployed)
- Deployment frequency

### Quality Metrics
- Code coverage percentage
- Bug escape rate
- PR review time
- Production incident rate
- Mean time to recovery (MTTR)

### AI Effectiveness Metrics
- Time saved per developer
- Code quality improvements
- Documentation completeness
- Reduction in review cycles
- Developer satisfaction scores

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [ ] Set up template repositories
- [ ] Configure ADO/Jira integration
- [ ] Document workflow standards
- [ ] Train team on Cursor + MCPs
- [ ] Establish coding standards

### Phase 2: Workflow Implementation (Weeks 5-8)
- [ ] Implement Stage 1-3 of workflow
- [ ] Create first features using new process
- [ ] Gather feedback and iterate
- [ ] Build documentation examples
- [ ] Measure initial metrics

### Phase 3: Advanced Features (Weeks 9-12)
- [ ] Implement Stage 4-5
- [ ] Automate more quality gates
- [ ] Build comprehensive test suites
- [ ] Create training materials
- [ ] Document lessons learned

### Phase 4: Agent Development (Weeks 13+)
- [ ] Design agent architecture
- [ ] Implement basic automation
- [ ] Test on simple bugs/tasks
- [ ] Gradually expand capabilities
- [ ] Monitor and optimize

---

## Suggested Improvements & Considerations

### 1. Knowledge Management
**Current Gap:** Documentation may become scattered  
**Suggestion:** 
- Implement a wiki or documentation portal (e.g., Docusaurus, GitBook)
- Use AI to auto-generate and update documentation
- Create a searchable knowledge base of patterns and solutions
- Maintain an ADR (Architecture Decision Record) repository

### 2. Feedback Loops
**Current Gap:** Limited mechanism for continuous improvement  
**Suggestion:**
- Regular retrospectives with AI-assisted analysis
- Automated collection of developer pain points
- Metrics dashboard for workflow effectiveness
- A/B testing different AI approaches

### 3. Security & Compliance
**Current Gap:** Not explicitly addressed in workflow  
**Suggestion:**
- Security review stage for sensitive changes
- Automated compliance checking (e.g., GDPR, SOC2)
- Secret scanning and dependency auditing
- Regular security training with AI tutoring

### 4. Cross-Team Collaboration
**Current Gap:** Focus is single-team  
**Suggestion:**
- Shared component libraries
- API contracts and versioning strategy
- Cross-team dependency management
- Standardized communication protocols

### 5. Onboarding & Training
**Current Gap:** How do new team members learn this workflow?  
**Suggestion:**
- Interactive onboarding guides built with AI
- Pair programming sessions (human + AI)
- Video tutorials demonstrating workflow
- AI-powered mentoring for junior developers

### 6. Rollback & Incident Management
**Current Gap:** What happens when things go wrong?  
**Suggestion:**
- Automated rollback procedures
- AI-assisted incident analysis
- Post-mortem automation
- Learning from production issues

### 7. Technical Debt Management
**Current Gap:** Not addressed in workflow  
**Suggestion:**
- Regular tech debt assessment with AI
- Automated refactoring suggestions
- Scheduled refactoring sprints
- Debt tracking in backlog with priority scoring

### 8. Performance Optimization
**Current Gap:** Limited focus on performance  
**Suggestion:**
- Automated performance testing in CI/CD
- AI-suggested optimizations
- Regular performance reviews
- Monitoring and alerting integration

### 9. Accessibility & Inclusion
**Current Gap:** Not explicitly mentioned  
**Suggestion:**
- Automated accessibility testing
- AI-powered accessibility suggestions
- WCAG compliance checking
- Inclusive design reviews

### 10. Cost Management
**Current Gap:** AI services and infrastructure costs  
**Suggestion:**
- Monitor AI API usage and costs
- Optimize prompts and context usage
- Evaluate cost/benefit of AI features
- Budget allocation for AI services

---

## Risk Mitigation

### Over-Reliance on AI
**Risk:** Developers may not learn fundamentals  
**Mitigation:**
- Require understanding of AI-generated code
- Regular code reviews emphasizing learning
- Training on core concepts
- Pair programming to transfer knowledge

### AI Hallucinations & Errors
**Risk:** AI may generate incorrect or insecure code  
**Mitigation:**
- Multiple layers of review
- Comprehensive automated testing
- Security scanning tools
- Never auto-merge AI agent PRs without review

### Tool Lock-in
**Risk:** Heavy dependency on specific AI tools  
**Mitigation:**
- Use standard languages and frameworks
- Document patterns independently of tools
- Maintain ability to work without AI
- Regular evaluation of tool alternatives

### Data Privacy & IP
**Risk:** Sensitive code sent to AI services  
**Mitigation:**
- Use enterprise AI services with data privacy
- Review terms of service carefully
- Implement code scanning for secrets
- Consider self-hosted AI models for sensitive code

### Change Management
**Risk:** Team resistance to new workflow  
**Mitigation:**
- Gradual rollout with pilot teams
- Demonstrate value early and often
- Gather and act on feedback
- Provide adequate training and support

---

## Consulting Service Deliverables

When using this as proof-of-concept for consulting services, you can offer:

### 1. Assessment & Strategy
- Current workflow analysis
- AI readiness assessment
- Custom workflow design
- Tool evaluation and selection
- ROI projections

### 2. Implementation Services
- Template repository setup
- MCP integration configuration
- CI/CD pipeline creation
- Documentation framework
- Team training programs

### 3. Ongoing Support
- Workflow optimization
- Metrics analysis and reporting
- Agent development and tuning
- Best practice updates
- Community of practice facilitation

### 4. Demonstration Materials
- Live working system (this ComplianceFlow project)
- Video demonstrations of each workflow stage
- Case studies with metrics
- Before/after comparisons
- Sample repositories and templates

---

## Next Steps

1. **Validate with ComplianceFlow Project**
   - Implement this workflow on current project
   - Document all processes and decisions
   - Measure effectiveness
   - Iterate based on learnings

2. **Create Template Repositories**
   - Build microservice template
   - Build frontend template
   - Document setup processes
   - Include example features

3. **Build MCP Integrations**
   - Set up ADO or Jira instance
   - Configure MCP connections
   - Test workflow automation
   - Document integration guides

4. **Develop Training Materials**
   - Create video tutorials
   - Write step-by-step guides
   - Build interactive demos
   - Prepare presentation decks

5. **Measure & Document Results**
   - Collect metrics on effectiveness
   - Gather testimonials from team members
   - Create case study documents
   - Build demo repository

---

## Conclusion

This AI-assisted development workflow represents a comprehensive approach to integrating AI throughout the entire SDLC. By implementing this with real projects like ComplianceFlow, you'll create:

1. **Proof of Value** - Demonstrable improvements in velocity and quality
2. **Reusable Assets** - Templates and patterns others can adopt
3. **Thought Leadership** - Documented best practices for AI development
4. **Consulting Foundation** - Tangible results to attract clients

The workflow balances automation with human oversight, ensuring quality while maximizing the benefits of AI assistance. As you implement and refine this approach, you'll develop deep expertise in AI-assisted development that positions you as a leader in this rapidly evolving space.

---

## Appendix A: Tool Recommendations & Free Tier Analysis

### Recommended Stack (All with Free Tiers)

#### Project Management
**Option 1: Jira (RECOMMENDED for widespread adoption)**
- ✅ **Free Tier:** Up to 10 users
- ✅ **Features:** Scrum/Kanban boards, backlogs, agile reporting, workflows, roadmaps
- ✅ **Storage:** 2 GB
- ✅ **Automation:** 100 rule runs/month
- ✅ **MCP Support:** Good community MCPs available
- ⚠️ **Limitation:** 100 email notifications/day, no advanced permissions
- 💰 **Cost Beyond Free:** ~$7.75/user/month (Standard)
- 🎯 **Why Choose:** Most widely adopted, great for demos to enterprise clients

**Option 2: Azure DevOps**
- ✅ **Free Tier:** Up to 5 users (full access)
- ✅ **Features:** Azure Boards, Repos, Pipelines, Test Plans, Artifacts
- ✅ **Pipeline Minutes:** 1,800/month
- ✅ **Repos:** Unlimited private Git repos
- ⚠️ **MCP Support:** Limited, may need custom development
- ⚠️ **Limitation:** Only 5 free users
- 💰 **Cost Beyond Free:** ~$6/user/month (Basic)
- 🎯 **Why Choose:** If already in Microsoft ecosystem

#### Source Code Management
**GitHub (STRONGLY RECOMMENDED)**
- ✅ **Free Tier:** Unlimited public/private repos
- ✅ **Collaborators:** Unlimited
- ✅ **Actions Minutes:** 2,000/month for private repos
- ✅ **Actions Minutes:** UNLIMITED for public repos
- ✅ **Storage:** 500 MB packages storage
- ✅ **MCP Support:** Excellent - official MCP from Anthropic
- ⚠️ **Limitation:** Some advanced features (code owners, SAML) require paid plans
- 💰 **Cost Beyond Free:** $4/user/month (Team)
- 🎯 **Why Choose:** Industry standard, best MCP support, generous free tier

#### CI/CD
**GitHub Actions (RECOMMENDED)**
- ✅ **Free Tier:** 2,000 minutes/month (private repos)
- ✅ **Public Repos:** UNLIMITED minutes
- ✅ **Multi-platform:** Linux, Windows, macOS runners
- ✅ **Integration:** Native GitHub integration
- 💡 **Pro Tip:** Use public repos for your demo projects = unlimited CI/CD
- 💰 **Cost Beyond Free:** $0.008/minute
- 🎯 **Why Choose:** Seamless with GitHub, great free tier

### Essential Tools (All Free for Basic Use)
- **Cursor AI** - Primary development IDE with AI (free tier available)
- **Docker** - Containerization (free)
- **Postman/Insomnia** - API testing (free tiers available)

### Recommended Additional Tools (Free Tiers)
- **Mermaid** - Diagram generation (free, open source)
- **Swagger UI** - API documentation (free, open source)
- **Dependabot** - Security scanning (free on GitHub)
- **Storybook** - UI component development (free, open source)
- **Playwright** - E2E testing (free, open source)

### Cost Optimization Tips
1. **Use Public Repos** for demo projects = unlimited GitHub Actions minutes
2. **Keep Team ≤ 10** users to stay on Jira free tier
3. **Self-hosted Runners** - If you exceed Actions minutes, use your own servers (free)
4. **Batch CI/CD** - Optimize workflows to use fewer minutes

---

## Appendix B: Sample Naming Conventions

### Branch Naming
- Feature: `feature/{ticket-id}-{description}`
- Bugfix: `bugfix/{ticket-id}-{description}`
- Hotfix: `hotfix/{ticket-id}-{description}`
- Release: `release/v{version}`

### Commit Messages
Format: `{type}({scope}): {subject}`

Types: feat, fix, docs, style, refactor, test, chore

Example: `feat(auth): add OAuth2 authentication support`

### PR Titles
Format: `[{ticket-id}] {description}`

Example: `[ADO-1234] Add user authentication with OAuth2`

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Oct 4, 2025 | AI Assistant | Initial workflow documentation |

---

**Questions or Feedback?**  
This is a living document. As you implement this workflow, capture learnings and update this guide. Consider creating a feedback mechanism for continuous improvement.

