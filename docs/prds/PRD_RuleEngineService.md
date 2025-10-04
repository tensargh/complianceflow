# Rule Engine Service PRD
## Compliance Flow Platform

### Service Information
- **Service Name**: Rule Engine Service
- **Version**: 1.0
- **Date**: December 2024
- **Domain**: Decision Automation

---

## 1. Service Overview

### 1.1 Purpose
The Rule Engine Service evaluates submitted declarations against configurable business rules to automatically approve, deny, or route declarations for human review. It also manages silent case creation for compliance investigation.

### 1.2 Responsibilities
- **Rule Evaluation**: Execute business rules against declaration data
- **Decision Making**: Generate approval/denial decisions with reasoning
- **Silent Case Detection**: Flag suspicious activities for investigation
- **Rule Management**: CRUD operations for business rules
- **Audit Trail**: Comprehensive logging of all rule evaluations

### 1.3 Service Boundaries
- **Owns**: Rules, Rule Evaluations, Decision Logic
- **Reads From**: Declaration Service (declaration data), External APIs (for rule conditions)
- **Writes To**: Decision events, Case events (Kafka)
- **Triggers**: Silent case creation, Review workflow initiation

---

## 2. Core Entities

### 2.1 Rule Definition
```json
{
  "rule_id": "UUID",
  "tenant_id": "UUID",
  "declaration_type": "personal_trade|gift_received|entertainment_received|holdings_attestation",
  "name": "string",
  "description": "string",
  "priority": "integer",
  "status": "active|inactive|draft",
  "conditions": {
    "type": "AND|OR",
    "rules": [
      {
        "field": "trade_amount",
        "operator": "greater_than",
        "value": 10000,
        "data_type": "number"
      },
      {
        "field": "user.business_unit",
        "operator": "equals",
        "value": "trading_desk",
        "data_type": "string"
      }
    ]
  },
  "action": {
    "decision": "approve|deny|review",
    "reason": "string",
    "create_case": "boolean",
    "case_priority": "low|medium|high",
    "case_reason": "string"
  },
  "expiry_date": "timestamp",
  "created_by": "UUID",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 2.2 Rule Evaluation
```json
{
  "evaluation_id": "UUID",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "rule_id": "UUID",
  "rule_version": "integer",
  "input_data": "object",
  "evaluation_result": "boolean",
  "decision": "approve|deny|review",
  "reason": "string",
  "create_case": "boolean",
  "execution_time_ms": "integer",
  "evaluated_at": "timestamp"
}
```

### 2.3 External Data Request
```json
{
  "request_id": "UUID",
  "rule_id": "UUID",
  "declaration_id": "UUID",
  "endpoint": "string",
  "request_data": "object",
  "response_data": "object",
  "status": "success|failure|timeout",
  "response_time_ms": "integer",
  "created_at": "timestamp"
}
```

---

## 3. API Specifications

### 3.1 Rule Evaluation APIs

#### POST /evaluate
```json
{
  "declaration_id": "UUID",
  "declaration_type": "personal_trade",
  "declaration_data": {
    "trade_amount": 15000,
    "symbol": "AAPL",
    "trade_type": "buy"
  },
  "user_context": {
    "user_id": "UUID",
    "business_unit": "trading_desk",
    "roles": ["trader"]
  }
}
```
Response: Evaluation result with decision

#### GET /evaluations/{declaration_id}
Response: All evaluations for a declaration

#### GET /evaluations/{evaluation_id}
Response: Specific evaluation details

### 3.2 Rule Management APIs

#### GET /rules?tenant_id={tenant_id}&declaration_type={type}
Response: List of rules with filtering

#### POST /rules
```json
{
  "tenant_id": "UUID",
  "declaration_type": "personal_trade",
  "name": "High Value Trade Check",
  "description": "Flag trades above threshold",
  "conditions": {
    "type": "AND",
    "rules": [
      {
        "field": "trade_amount",
        "operator": "greater_than",
        "value": 50000,
        "data_type": "number"
      }
    ]
  },
  "action": {
    "decision": "review",
    "reason": "High value trade requires review",
    "create_case": true,
    "case_priority": "medium"
  }
}
```

#### PUT /rules/{rule_id}
Update rule definition

#### DELETE /rules/{rule_id}
Soft delete rule (deactivate)

### 3.3 Testing and Simulation APIs

#### POST /rules/{rule_id}/test
```json
{
  "test_data": {
    "trade_amount": 75000,
    "symbol": "TSLA"
  },
  "user_context": {
    "business_unit": "trading_desk"
  }
}
```
Response: Evaluation result without persistence

#### POST /rules/simulate
```json
{
  "declaration_type": "personal_trade",
  "test_data": "object",
  "rule_ids": ["UUID", "UUID"]
}
```
Response: Results from multiple rules

---

## 4. Rule Evaluation Engine

### 4.1 Evaluation Algorithm
```python
class RuleEvaluator:
    def evaluate_declaration(self, declaration_data, user_context):
        # Get active rules for declaration type
        rules = self.get_active_rules(declaration_data.type)
        
        # Sort by priority (highest first)
        rules.sort(key=lambda r: r.priority, reverse=True)
        
        final_decision = "approve"  # Default
        case_flags = []
        
        for rule in rules:
            result = self.evaluate_rule(rule, declaration_data, user_context)
            
            # Apply decision hierarchy: deny > review > approve
            if result.decision == "deny":
                final_decision = "deny"
            elif result.decision == "review" and final_decision != "deny":
                final_decision = "review"
                
            # Collect case creation flags
            if result.create_case:
                case_flags.append(result.case_info)
                
        return EvaluationResult(
            decision=final_decision,
            case_flags=case_flags,
            rule_results=results
        )
```

### 4.2 Condition Evaluation
```python
OPERATORS = {
    "equals": lambda a, b: a == b,
    "not_equals": lambda a, b: a != b,
    "greater_than": lambda a, b: float(a) > float(b),
    "less_than": lambda a, b: float(a) < float(b),
    "contains": lambda a, b: str(b).lower() in str(a).lower(),
    "in_list": lambda a, b: a in b,
    "regex_match": lambda a, b: re.match(b, str(a)) is not None
}

def evaluate_condition(condition, data):
    field_value = get_nested_field(data, condition.field)
    operator_func = OPERATORS[condition.operator]
    return operator_func(field_value, condition.value)
```

### 4.3 External Data Integration
```python
class ExternalDataProvider:
    async def fetch_market_data(self, symbol):
        # Call external market data API
        pass
        
    async def fetch_user_history(self, user_id):
        # Call internal analytics service
        pass
        
    async def fetch_regulatory_data(self, instrument):
        # Call regulatory database
        pass
```

---

## 5. Events Published

### 5.1 Decision Events
```json
{
  "event_type": "declaration.rule_evaluated",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "decision": "approve|deny|review",
  "reason": "string",
  "rules_applied": ["UUID"],
  "execution_time_ms": "integer",
  "timestamp": "ISO8601"
}
```

```json
{
  "event_type": "decision.approved",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "reason": "string",
  "auto_decision": "boolean",
  "timestamp": "ISO8601"
}
```

```json
{
  "event_type": "decision.sent_to_review",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "reason": "string",
  "reviewer_groups": ["UUID"],
  "timestamp": "ISO8601"
}
```

### 5.2 Case Events
```json
{
  "event_type": "case.flagged",
  "declaration_id": "UUID",
  "tenant_id": "UUID",
  "case_type": "silent",
  "priority": "low|medium|high",
  "reason": "string",
  "rule_id": "UUID",
  "timestamp": "ISO8601"
}
```

---

## 6. External Dependencies

### 6.1 Service Dependencies
- **Declaration Service**: Declaration data for evaluation
- **User Service**: User context and business unit information

### 6.2 External APIs
- **Market Data**: Stock prices, trading volumes
- **Regulatory Data**: Compliance databases, watch lists
- **Historical Data**: User trading history, patterns

### 6.3 Event Subscriptions
- **Declaration Events**: declaration.submitted (trigger evaluation)

---

## 7. Data Storage

### 7.1 Database Schema
- **Primary Database**: PostgreSQL
- **Rule Storage**: JSON columns for flexible rule definitions
- **Evaluation History**: Immutable record of all evaluations
- **Performance**: Indexes on tenant_id, declaration_type, evaluated_at

### 7.2 Caching Strategy
- **Active Rules**: Cache rules by tenant + declaration_type (5 min TTL)
- **External Data**: Cache API responses (configurable TTL)
- **User Context**: Cache user business unit data (15 min TTL)

### 7.3 Performance Requirements
- **Rule Evaluation**: < 500ms for simple rules, < 2s for complex rules with external data
- **Rule Retrieval**: < 100ms for cached rules
- **Bulk Evaluation**: Support 100+ concurrent evaluations

---

## 8. Security Requirements

### 8.1 Rule Access Control
- **Rule Creation**: Only compliance officers can create/modify rules
- **Rule Viewing**: Reviewers can view rules affecting their declarations
- **Evaluation History**: Full audit trail with immutable records

### 8.2 External API Security
- **API Keys**: Secure storage in Azure Key Vault
- **Rate Limiting**: Respect external API limits
- **Data Privacy**: No PII in external API calls

---

## 9. Implementation Notes

### 9.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with JSON support
- **Rule Engine**: Custom Python implementation
- **External APIs**: httpx for async HTTP calls
- **Caching**: Redis for rule and data caching

### 9.2 Rule Versioning
- **Version Control**: Rules are versioned on each change
- **Backwards Compatibility**: Old evaluations reference specific rule versions
- **Migration**: Automated migration of rule format changes

### 9.3 Error Handling
- **External API Failures**: Graceful degradation, use cached data
- **Rule Evaluation Errors**: Log error, default to "review" decision
- **Timeout Handling**: Circuit breaker for external API calls

---

## 10. Testing Strategy

### 10.1 Unit Tests
- Rule condition evaluation
- Decision hierarchy logic
- External data integration
- Error handling scenarios

### 10.2 Integration Tests
- End-to-end rule evaluation
- External API integration
- Event publishing
- Database operations

### 10.3 Performance Tests
- Rule evaluation under load
- Complex rule performance
- External API timeout handling
- Concurrent evaluation scenarios
