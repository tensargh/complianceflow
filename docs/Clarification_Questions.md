# Clarification Questions Document
## Compliance Flow Application

### Document Information
- **Version**: 1.0
- **Date**: December 2024
- **Status**: Draft
- **Purpose**: Identify gaps and gather additional requirements

---

## 1. Business Context & Scope

### 1.1 Industry & Compliance Requirements
- **Q1**: What industry/regulatory framework is this application primarily designed for? (e.g., financial services, healthcare, manufacturing)
**Answer**: Financial services - for things such as declaration of personal trades, declarations of gift or entertainment hiven or received, attesting to holdings, etc  - however, i want this not to be limited to this domain. 
Primarily 
- **Q2**: Are there specific regulatory requirements that must be met? (e.g., SOX, GDPR, HIPAA, PCI-DSS)
**Answer**: No - this is not trying at this stage to match regulations - this is the wider case of making generic declarations - then we want to be able to use this core functionality for specific declaration types.
- **Q3**: What are the typical activity types that users will be declaring? (e.g., financial transactions, data access, policy exceptions)
**Answer**: see above
- **Q4**: Are there existing compliance processes or systems that this application needs to integrate with or replace?
**Answer**: no - were making a new product.
### 1.2 Organizational Structure
- **Q5**: How large is the target organization? (number of users, departments, locations)
**Answer**: This will be a SaaS solution aimed at many customers - from small to enterprise scale. We will need to be able to scale rapidly during peak periods (e.g., attestation cycles). 
- **Q6**: What is the typical organizational hierarchy structure? (flat, matrix, traditional hierarchy)
**Answer**: Assume traditional hierarchy. We can come up with a scheme to group users - we may need to build this but we want to base it on common interfaces.
- **Q7**: Are there multiple business units or subsidiaries that need separate compliance processes?
**Answer**: Yes - let's assume that the user's business unit will be used to decide, for example, what fields they need to fill in. We should have a scheme where the selection is made on some ranking where we have a fallback option as a default and then we might select another if it's tied to some business unit.
- **Q8**: Do different regions/countries have different compliance requirements?
**Answer**: Yes, but let's use the above BU selection to select the definition/form they have to complete.
---

## 2. User Management & Authentication

### 2.1 User Identity & Access
- **Q9**: What identity provider will be used? (Azure AD, Active Directory, other)
**Answer**: Let's start with Azure AD - ideally we should be able to use multiple
**Answer**: change in plan. lets not support these - we should use SSO config per tenant.
- **Q10**: How are users initially provisioned? (manual, automated from HR system, self-registration)
**Answer**: Automated from the Azure AD
- **Q11**: What user attributes are available from the identity system? (department, manager, role, location)
**Answer**: I don't know - let's use whatever the default is - and then allow some simple mapping. The point is to allow our SaaS customers to integrate - so maybe specifying AD etc is not right - maybe we actually need to allow some SSO config
**Answer**: yes we need to support custom mapping so we can get things like groups, and then use groups in the product. 
I expect we would want to suggest they send us all groups, and then we allow admin to set a list of relevant groups - this way we can parse the list of groups from their attribute and then use that. 
We should provide custome mappings for other things for each user such as business unit and anything else that is available.
Suggest also how we can test this with multiple sso providers.
- **Q12**: Are there guest users or external reviewers who need access?
**Answer**: for now no

### 2.2 Role Management
- **Q13**: How are compliance officers identified and assigned? (manual assignment, role-based, department-based)
**Answer**: SSO - we will require somthing like group assignment so they can manage this within their idp. this should be configured per tenant
- **Q14**: Can a user have multiple roles simultaneously? (e.g., User + Reviewer + Compliance Officer)
**Answer**: Yes for sure. All users will the Users. Some users will also be Compliance. Reviewers should be based on a different meteric - ie we can create reviewe groups. Any user can efectively be a reviewer by being assigned a review.
- **Q15**: Are there different levels of compliance officers with different permissions?
**Answer**: THere might be - lets assume that we will manage this in the same way - ie we will provide mappings from our role groups to sso assinged groups from the idp.
- **Q16**: How are reviewer assignments managed? (automatic based on rules, manual assignment, hybrid)
**Answer**: THe workflow would be - if a declaration is sent to review, consider the declaration type and the users business unit - we will have a pattern of - for each type, go down list of review groups until one is for business unit the declarer works for - with a fallback option that must always be created.

---

## 3. Declaration Types & Forms

### 3.1 Activity Types
- **Q17**: What are the main categories of activities that require declaration?
**Answer**: lets start with the following
  - Personal Trade
  - Personal Trade Preclearance
  - Gift Received
  - Entertainment Received
  - Holdings Attestation
- **Q18**: Are activity types hierarchical? (e.g., Financial > Expense > Travel Expense)
**Answer**: No - but lets add a category so 
  - Personal Trade -> Personal Trading
  - Personal Trade Preclearance -> Personal Trading
  - Gift Received -> Hospitality
  - Entertainment Received  -> Hospitality
  - Holdings Attestation -> Personal Trading
- **Q19**: Can activity types be customized per organization or are they standardized?
**Answer**: Standard for now
- **Q20**: Are there seasonal or time-based activity types that appear/disappear?
**Answer**: No -but we will later want to be able to schedule declarations such that we ask users to complete a declaration - for example, we may want to make it so users have to complete a quarterly Holdings attestation.

### 3.2 Form Configuration
- **Q21**: What types of form fields are needed? (text, dropdowns, file uploads, date pickers, calculations)
**Answer**: Checkboxes, text, dropdowns, dates, file uploads, numbers, currency values. We will want some very limited control flow - so a checkbox or dropdown value may enable or disable another field.
- **Q22**: Are there conditional fields that appear based on previous answers?
**Answer**: yes - see above - some simple conditions are required/
- **Q23**: Can forms have multiple sections or pages?
MUltiple sections, single page
- **Q24**: Are there field validation rules that need to be configurable?
**Answer**: Yes - simple for now, ie field length, max min values, required or optional
- **Q25**: Can forms be versioned and have approval workflows for changes?
**Answer**: YEs - we want this for sure so that we can work on a new version of a form and then publish that to be live.

### 3.3 Form Selection Logic
- **Q26**: What criteria determine which form a user sees for a given activity type?
**Answer**: We should always have to have a fallhack form for each activity type. THen we can create a new form, and assign it to one or more user groups, and give it a ranking. When a user makes a declaration we should find the highest ranking form that matches their business unit or other user groups. THen if none we should use the fallback
- **Q27**: Can users see multiple forms for the same activity type and choose?
**Answer**: no - the system will decide
- **Q28**: Are there user-specific forms based on role, department, or other attributes?
**Answer**: See above
---

## 4. Business Rules & Automation

### 4.1 Rule Engine Requirements
- **Q29**: What types of rules are needed? (approval thresholds, risk scoring, compliance checks)
**Answer**: The rules will actually be based on the declaration type - for now lets keep this simple We should have a rules engine for each declaration type (allthough they should have the same structure and interfaces). We shoud pass the fields fixed for the declaration type and the form values to the appropriate rule engine 
- **Q30**: Can rules reference external data sources? (credit scores, market data, regulatory databases)
**Answer**: The rules engine for that declaration type can go and fetch additional data if erquired
- **Q31**: Are there complex rule combinations? (AND/OR logic, nested conditions)
**Answer**: YEs assume this is evaluated as a binary tree
- **Q32**: Can rules be time-based or have expiration dates?
**Answer**: yes
- **Q33**: Do rules need to be auditable with change tracking?
**Answer**: yes absolutely in both senses - ie changes to rule definitons should be autidet - abut also the evaluation of rules. we need to be able to go back and understand why a rule decision was made

### 4.2 Decision Outcomes
- **Q34**: Besides approve/deny/review, are there other possible outcomes? (conditional approval, partial approval)
**Answer**: not as such - but we should have the silent raised case option.
- **Q35**: Can decisions be reversed or appealed?
**Answer**: The review process is for this. an approved review is done - maybe we can re-open a denied review. 
- **Q36**: Are there different types of denials with different consequences?
**Answer**: No -but, we should have the ability for compliance to raise a case from any review - and we should have the ability for any reviewer to escalate any declaration they are reviewing to compliance - specifiying a reason why. 
- **Q37**: What happens when rules conflict or produce ambiguous results? 
**Answer**: always take the "worst" result ie Deny overrides review, review overrides approve.

### 4.3 Silent Case Creation
- **Q38**: What triggers the creation of silent cases?
**Answer**: rules can do this. It should work like this. Any rule must always have the approval set of conditions. It can optionally have a set of case conditions - these should be evaluated alongside the approval conditions. If, at the end of runnng all rules, any has flagged to raise a case, do so.
- **Q39**: Are silent cases visible to the original user or only to compliance officers?
**Answer**: Only ever to compliance officers - and since this could happen to a compliance officer, not to the compliance officer who is the user if it happens to them.
- **Q40**: Do silent cases have different priority levels or categories?
**Answer**: No lets keep it simple - case management needs its own definiton though
- **Q41**: Can silent cases be automatically closed based on time or other criteria?
**Answer**: No. cases must be managed by compliance.
---

## 5. Review Workflow

### 5.1 Reviewer Assignment
- **Q42**: How are reviewers selected? (manager hierarchy, department, expertise, availability)
**Answer**: We have review groups consisting of members and as we mentioned before, we will select the group tp reviwe bsaes on the users business unit. Note - reviewss may need approval from more than one group - eg we may need a manager, complicane, and legal.
- **Q43**: Can multiple reviewers be assigned to the same declaration?
**Answer**: yes but treat it as reviewer groups rather than reviewers
- **Q44**: Are there backup reviewers if primary reviewers are unavailable?
**Answer**: we should ahve groups as mentioned. COmplinace should be able to step in to approve in proxy of any group but this should be audited
- **Q45**: Can reviewers delegate or reassign reviews to others?
**Answer**: It should always be the group with compliance fallback. Its possible a group has one member but the expectation is they would have multipe members
- **Q46**: Are there reviewer capacity limits or workload balancing?
**Answer**: No - since we are using groups. BUT i think metrics on which groups get most reviews, and then within them who does the most reviews, which groups and individuals review in a timely manner, etc , are very important

### 5.2 Multi-Stage Reviews
- **Q47**: What are the typical review stages? (manager approval, compliance review, final approval)
**Answer**: that sounds reasonable but this is to be designed by the tenant. THe default should be to use a single group - not muitlple. 
- **Q48**: Can stages be parallel or must they be sequential?
**Answer**:  we will assume parallel always for now
- **Q49**: What happens if a reviewer in an earlier stage denies the declaration?
**Answer**: Its parallel - but any group denying means its denied.
- **Q50**: Can stages be skipped based on certain conditions?
**Answer**: no stages - parallel
- **Q51**: Are there time limits for each review stage?
**Answer**: No time limits but we should track aged reviews - so we can help teams improove their process or spot bottlenecks

### 5.3 Escalation & Break-Glass
- **Q52**: What constitutes a "stuck" review? (time-based, reviewer unavailable, conflicts)
**Answer**: LEt not set a rigid answe but we should have a ranked list of aged reviews that compliance can see - and any reviewers list of reviews to do should have the oldest at the top by default.
- **Q53**: Who can initiate break-glass processes? (compliance officers only, reviewers, users)
**Answer**: COmpliance officers can breakglass and decide a result - this needs careful audit!
- **Q54**: What actions are available in break-glass mode? (override, reassign, expedite)
**Answer**: SImply deciding an Approve / Deny state - but always with a reason provided
- **Q55**: Are break-glass actions audited differently?
**Answer**: Maybe not differently - we will audit carefully ALL decidisons - but we should be clear a breakglass operation has taken place

---

## 6. Case Management

### 6.1 Investigation Process
- **Q56**: What types of investigations are typically conducted?
**Answer**: that is entirely down to the compliance team - we should allow them to write copious notes add ntoes, each datestamped), upload attachments.
- **Q57**: Are there standard investigation procedures or templates?
**Answer**: No we just want lots of notes and attachments
- **Q58**: Can cases be assigned to external investigators or only internal staff?
**Answer**: We are assuming internal staff
- **Q59**: What evidence types need to be collected? (documents, interviews, system logs)
**Answer**: Compliance teams to determine
- **Q60**: Are there case priority levels or SLA requirements?
**Answer**: No

### 6.2 Case Lifecycle
- **Q61**: What are the typical case statuses? (open, investigating, pending, closed)
**Answer**: Yes those are good
- **Q62**: Can cases be reopened after closure?
**Answer**: Yes
- **Q63**: Are there automatic case closure rules?
#**Answer**: No
- **Q64**: What reporting is required for closed cases?
**Answer**: complaince team to decide - but it feels like they should always have to complete a findings section,

---

## 7. Notifications & Communication

### 7.1 Notification Requirements
- **Q65**: What events trigger notifications? (submission, assignment, decision, escalation)
**Answer**: all of those
- **Q66**: What notification channels are needed? (email, SMS, in-app, mobile push)
**Answer**: lets make it so that we start with email but the whole system is based around later expnading out to those, plus teams, slack, etc
- **Q67**: Can users customize their notification preferences?
**Answer**: Compliance can build templates which are completed from the declaration in a mail-merge kind of way. They can determine who these alerts will go to in terms of the declarer, the review team, compliance, and maybe some fixed addresses. other options to follow.
Recipients can not opt out.
- **Q68**: Are there notification templates that can be customized?
**Answer**: yes - based on the fixed fields of a declaration type, and things related to the declarting user, their BU, the reference of the declaration, etc.

### 7.2 Communication Features
- **Q69**: Do reviewers need to communicate with submitters during review?
**Answer**: No - but they might?
**Answer**: external tools. the closest we should have for internal messaging is that users who can review things should have a queue of things assigned to the groups they review for.
- **Q70**: Are there comment threads or discussion features?
**Answer**: I think multiple notes -so somthing like a comments thread
- **Q71**: Can reviewers request additional information from submitters?
**Answer**: That feels liek a good requirement - yes - they canand should be able to have that on their review stage that it is pending feedback?
- **Q72**: Are communications audited and stored?
**Answer**: they should be ideally - wbut we dont want to be an email client - and if its by phone i am not sure how tbh. at least provide the ability to add time-stamped notes & attachmentds.

---

## 8. Reporting & Analytics

### 8.1 Standard Reports
- **Q73**: What standard reports are needed? (submission volumes, approval rates, review times)
**Answer**: YEs lets keep as many metrics and kpi targets as possible for things like, number of submissions, how they are assigned to groups, who picks them up, who doesnt, turnarounf time, etc.
- **Q74**: Who needs access to different types of reports?
**Answer**: Compliance can acccess these dashboards and reports
- **Q75**: Are there regulatory reporting requirements?
**Answer**: Not as of yet - there may be. 
- **Q76**: Do reports need to be scheduled and automatically generated?
**Answer**: possibly. lets say no for now and leave that as a future feature/

### 8.2 Analytics & Dashboards
- **Q77**: What key performance indicators (KPIs) need to be tracked?
**Answer**: Average time to rewiew. Reviews handled. Time to investigte cases. All by group, individual, declation type, date range, month on month, year on year etc.
- **Q78**: Are there real-time dashboards needed?
Ideally of above
- **Q79**: Do different user roles need different dashboard views?
**Answer**: Lets only have dashboards for compliance now - we may have for reviewers where they can  see how their team ranks in terms of volume and speed, but without seeing the daya of other review grous.
- **Q80**: Are there predictive analytics requirements?
Not yet.

---

## 9. Integration & Data

### 9.1 External Systems
- **Q81**: What external systems need to be integrated? (HR, ERP, CRM, document management)
SSO for digning and authorization, etc. None other for now
- **Q82**: Are there real-time integration requirements or is batch processing acceptable?
Not for now
- **Q83**: What data needs to be synchronized between systems?
None for now othr than uders, and their BU, groupss, etc.
- **Q84**: Are there API requirements for external systems to consume?
**Answer**: N/A for now

### 9.2 Data Management
- **Q85**: How long must declaration data be retained?
**Answer**: lets assume 7 years but lets put deletion in the hands of the tenant with some very sdtrong guard rails in ppalce
- **Q86**: Are there data archiving requirements?
**Answer**: LEts have it so we go active => archive -> delete
- **Q87**: What data needs to be anonymized or pseudonymized?
**Answer**: None for now - we may want later for users to be able to insist on being "forgot"
- **Q88**: Are there data export requirements for compliance purposes?
**Answer**: lets assume compliance can export vies of data as csv

---

## 10. Technical & Deployment

### 10.1 Infrastructure
- **Q89**: What are the expected user volumes? (concurrent users, peak loads)
**Answer**: normally now in the handfull at a time. We need to be able to scale rapidly at times of, say, attestation, to support a lot of people. Scalability is key
- **Q90**: Are there specific Azure services that must be used?
**Answer**: No lets choose wisely.
- **Q91**: Are there data residency requirements? (specific regions, countries)
**Answer**: lets build using IAC in a way we can spin up new environments. Assumption for day 1 shoud be EU ans US first
- **Q92**: What are the disaster recovery and backup requirements?
**Answer**: We should be able to fail over within a region. We should bakup all data daily and with in-day logs so we can replay an rebui;d

### 10.2 Security & Compliance
- **Q93**: What security certifications are required? (SOC 2, ISO 27001, FedRAMP)
**Answer**: SOC2 and ISO for sure
- **Q94**: Are there specific encryption requirements?
**Answer**: We should encrypt at the db leved
- **Q95**: What are the audit logging requirements?
We should audit all decisions - so all maring as approved / denied etc should result in a thorough log of who, what, ehwn, why they decided what.
- **Q96**: Are there penetration testing requirements?
**Answer**: Eventualyl yes - lets buildeveryting with owasp in mond, and no sql injection possible.

### 10.3 Development & Deployment
- **Q97**: What is the preferred development methodology? (Agile, DevOps, CI/CD)
**Answer**: Kanhan, using Azure Devops to track tasks adn do CI/CD
- **Q98**: Are there specific technology stack preferences?
**Answer**: I am by training a Microsoft stack person - however I am learning Python.
Other than being in Azure I want strong opinion and suggestions.
**Answer**: I would like suggestions here. I can provide MCPs - please write a tech stack suggestions doc, listing options and providing pros / cons.
The "easy" route for me would be c# and sql server back end - however, my azure knowledge is medium at best. It feels like we'd use service bus - but i am very interested in learning Kafka as that seems a very popular way of dealing with this. I'd also like to boost my earning potential - so i am looking for 
Strong architetural patterns for cloud microservice based applications
Use of marketable skills - so patterns and tools that have high earning potentials (eg, at least in theory i believe python devs earn more than c# devs).
For front end - i have not much experience - i want somthing that works well with apis. I think we might want a backend for frontend pattern - consider that please. We MIGHT want micro front ends - but i dont want to overcomplicate it. 
Suggest options based on the same criteria but assume my starting knowledge is not relevant. 
- **Q99**: What are the deployment frequency requirements?
On demand - promoting from dev/qa to "staging" to live
- **Q100**: Are there change management and approval processes for deployments?
**Answer**: Yes there should be but lets not gget overwraught o that.
---

## 11. Success Criteria & Metrics

### 11.1 Business Success
- **Q101**: What defines success for this application?
We can onboard a new tenant easily 
e can add a new declaration type, spin up a rules engine for it, and have that new type be declarable within a day. We will then need to spend ectra time with rulesand with building all the ficrd filrds part of what they are doung
- **Q102**: What are the key business metrics to track?
**Answer**: None for noe
- **Q103**: Are there cost savings targets?
**Answer**: None for now
- **Q104**: What is the expected ROI timeline?
**Answer**: unknown - this is a long slow burn personal project for now.

### 11.2 User Adoption
- **Q105**: What is the expected user adoption timeline?
**Answer**: none for now
- **Q106**: Are there training requirements or change management needs
**Answer**: non for now - make good documentation!
- **Q107**: How will user feedback be collected and incorporated?
**Answer**: yes in the future
- **Q108**: Are there pilot programs or phased rollouts planned?
**Answer**: unknown

---

## Summary of Clarification Status

### ✅ Well-Defined Requirements
- **Industry Focus**: Financial services with generic declaration platform approach
- **Declaration Types**: Personal Trade, Personal Trade Preclearance, Gift Received, Entertainment Received, Holdings Attestation
- **Architecture**: Multi-tenant SaaS with Azure deployment
- **Authentication**: Azure AD SSO with role mapping
- **Review Process**: Parallel reviewer groups with business unit-based assignment
- **Rule Engine**: Declaration type-specific rules with audit trails
- **Case Management**: Silent case creation and investigation tracking
- **Data Management**: 7-year retention with tenant-controlled deletion

### ✅ Recently Resolved
- **Q9**: Per-tenant SSO configuration (no additional providers needed)
- **Q11**: Custom attribute mapping with group parsing and business unit mapping
- **Q69**: External communication tools with reviewer queue interface
- **Q98**: Technology stack recommendations provided (Python + FastAPI + React + Kafka)

### 📋 Questions Removed from PRD
The following questions have been answered sufficiently and their requirements incorporated into the PRD:
- Q1-Q8: Business context and organizational structure
- Q10, Q12-Q16: User management and role assignment
- Q17-Q28: Declaration types and form configuration
- Q29-Q41: Business rules and automation
- Q42-Q55: Review workflow and escalation
- Q56-Q64: Case management
- Q65-Q68, Q70-Q72: Notifications and communication
- Q73-Q80: Reporting and analytics
- Q81-Q88: Integration and data management
- Q89-Q97, Q99-Q100: Technical and deployment
- Q101-Q108: Success criteria and metrics

## Next Steps

All clarification questions have been resolved! The next steps would be:

1. **Review Technology Stack**: Review the comprehensive tech stack recommendations document
2. **Create User Stories**: Develop detailed user stories for each persona and use case
3. **Define Acceptance Criteria**: Establish clear acceptance criteria for each feature
4. **Architecture Design**: Create detailed technical architecture based on requirements
5. **Implementation Planning**: Develop phased implementation plan with milestones
6. **Risk Assessment**: Identify and plan mitigation for technical and business risks
7. **Development Environment Setup**: Set up Docker Compose environment with recommended stack

