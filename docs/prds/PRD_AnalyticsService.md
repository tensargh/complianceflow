# Analytics Service PRD
## Compliance Flow Platform

### Service Information
- **Service Name**: Analytics Service
- **Version**: 1.0
- **Date**: December 2024
- **Domain**: Reporting & Analytics

---

## 1. Service Overview

### 1.1 Purpose
The Analytics Service provides comprehensive reporting, dashboards, and analytics capabilities for the Compliance Flow platform, enabling compliance officers and reviewers to monitor performance, identify trends, and generate compliance reports.

### 1.2 Responsibilities
- **Data Aggregation**: Collect and aggregate data from all services
- **Report Generation**: Generate standard and custom reports
- **Dashboard Management**: Provide real-time dashboards and KPIs
- **Performance Metrics**: Track review times, approval rates, and user activity
- **Data Export**: Export data for external compliance reporting

### 1.3 Service Boundaries
- **Owns**: Aggregated Metrics, Reports, Dashboard Configurations
- **Reads From**: All services (via events and direct queries)
- **Writes To**: Analytics events (Kafka), Export files
- **Does NOT**: Modify operational data in other services

---

## 2. Core Entities

### 2.1 Metric Definition
```json
{
  "metric_id": "UUID",
  "name": "avg_review_time",
  "description": "Average time to complete reviews",
  "category": "performance|compliance|usage",
  "data_type": "number|percentage|count",
  "unit": "hours|days|count|percentage",
  "calculation": {
    "type": "average|sum|count|percentage",
    "source_events": ["review.completed"],
    "formula": "AVG(completed_at - assigned_at)",
    "filters": ["status = 'completed'"],
    "group_by": ["tenant_id", "declaration_type"]
  },
  "refresh_frequency": "real_time|hourly|daily|weekly"
}
```

### 2.2 Dashboard Configuration
```json
{
  "dashboard_id": "UUID",
  "tenant_id": "UUID",
  "name": "Compliance Overview",
  "description": "Main dashboard for compliance officers",
  "user_roles": ["compliance_officer"],
  "widgets": [
    {
      "widget_id": "UUID",
      "type": "metric_card|chart|table|gauge",
      "title": "Average Review Time",
      "metric_id": "UUID",
      "position": {"x": 0, "y": 0, "width": 4, "height": 2},
      "configuration": {
        "chart_type": "line|bar|pie",
        "time_range": "7d|30d|90d",
        "filters": {},
        "thresholds": {"warning": 24, "critical": 48}
      }
    }
  ],
  "created_by": "UUID",
  "created_at": "timestamp"
}
```

### 2.3 Report Definition
```json
{
  "report_id": "UUID",
  "tenant_id": "UUID",
  "name": "Monthly Compliance Report",
  "description": "Monthly summary of declaration activity",
  "type": "scheduled|on_demand",
  "format": "pdf|excel|csv",
  "parameters": {
    "date_range": "monthly",
    "include_sections": ["summary", "by_type", "by_department"],
    "filters": {"status": ["approved", "denied"]}
  },
  "schedule": {
    "frequency": "monthly",
    "day_of_month": 1,
    "time": "09:00",
    "timezone": "UTC"
  },
  "recipients": ["compliance@company.com"],
  "created_by": "UUID",
  "created_at": "timestamp"
}
```

### 2.4 Aggregated Data
```json
{
  "aggregate_id": "UUID",
  "tenant_id": "UUID",
  "metric_name": "string",
  "dimensions": {
    "declaration_type": "personal_trade",
    "business_unit": "trading_desk",
    "time_period": "2024-01"
  },
  "value": "number",
  "timestamp": "timestamp",
  "calculated_at": "timestamp"
}
```

---

## 3. API Specifications

### 3.1 Dashboard APIs

#### GET /dashboards?tenant_id={tenant_id}&user_role={role}
Response: Available dashboards for user

#### GET /dashboards/{dashboard_id}
Response: Dashboard configuration and data

#### POST /dashboards
```json
{
  "tenant_id": "UUID",
  "name": "Reviewer Performance",
  "description": "Dashboard for review team performance",
  "user_roles": ["reviewer"],
  "widgets": [...]
}
```

#### PUT /dashboards/{dashboard_id}
Update dashboard configuration

#### GET /dashboards/{dashboard_id}/data?time_range={range}
Response: Real-time dashboard data

### 3.2 Metrics APIs

#### GET /metrics?tenant_id={tenant_id}&category={category}
Response: Available metrics

#### GET /metrics/{metric_id}/data?time_range={range}&filters={filters}
Response: Metric data with optional filtering

#### POST /metrics/query
```json
{
  "metric_ids": ["UUID", "UUID"],
  "time_range": "30d",
  "group_by": ["declaration_type"],
  "filters": {
    "business_unit": "trading_desk"
  }
}
```

### 3.3 Reporting APIs

#### GET /reports?tenant_id={tenant_id}&type={type}
Response: Available reports

#### POST /reports/generate
```json
{
  "report_id": "UUID",
  "parameters": {
    "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
    "filters": {"status": ["approved", "denied"]}
  },
  "format": "pdf"
}
```

#### GET /reports/{report_id}/schedule
Response: Report schedule configuration

#### POST /reports/{report_id}/schedule
```json
{
  "frequency": "weekly",
  "day_of_week": "monday",
  "time": "08:00",
  "recipients": ["compliance@company.com"]
}
```

### 3.4 Data Export APIs

#### POST /exports
```json
{
  "tenant_id": "UUID",
  "export_type": "declarations|reviews|cases",
  "format": "csv|excel",
  "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
  "filters": {},
  "columns": ["declaration_id", "status", "submitted_at"]
}
```

#### GET /exports/{export_id}
Response: Export status and download link

#### GET /exports/{export_id}/download
Response: File download

---

## 4. Key Metrics & KPIs

### 4.1 Declaration Metrics
- **Submission Volume**: Declarations submitted per period
- **Approval Rate**: Percentage of declarations approved
- **Automation Rate**: Percentage of declarations auto-processed
- **Average Processing Time**: Time from submission to final decision
- **Peak Usage Periods**: Identification of high-volume periods

### 4.2 Review Metrics
- **Average Review Time**: Time to complete reviews by type/reviewer
- **Review Backlog**: Number of pending reviews
- **Reviewer Workload**: Reviews assigned vs completed per reviewer
- **Escalation Rate**: Percentage of reviews escalated to compliance
- **SLA Compliance**: Reviews completed within target timeframes

### 4.3 Case Metrics
- **Case Volume**: Number of cases opened per period
- **Case Resolution Time**: Average time to close cases
- **Case Types**: Distribution of silent vs escalated cases
- **Investigation Outcomes**: Distribution of case outcomes
- **Case Backlog**: Number of open cases by age

### 4.4 Performance Metrics
- **System Response Times**: API response time percentiles
- **Error Rates**: System error rates by service
- **User Activity**: Login frequency, feature usage
- **Data Quality**: Completeness and accuracy metrics

---

## 5. Data Processing

### 5.1 Event Processing
```python
class AnalyticsEventProcessor:
    def process_declaration_event(self, event):
        if event.type == "declaration.submitted":
            self.update_submission_metrics(event)
        elif event.type == "declaration.approved":
            self.update_approval_metrics(event)
            self.calculate_processing_time(event)
    
    def process_review_event(self, event):
        if event.type == "review.completed":
            self.update_review_time_metrics(event)
            self.update_reviewer_workload(event)
    
    def process_case_event(self, event):
        if event.type == "case.created":
            self.update_case_volume_metrics(event)
        elif event.type == "case.closed":
            self.calculate_case_resolution_time(event)
```

### 5.2 Aggregation Engine
```python
class MetricAggregator:
    def calculate_hourly_aggregates(self):
        # Calculate hourly metrics for real-time dashboards
        pass
    
    def calculate_daily_aggregates(self):
        # Calculate daily metrics for trend analysis
        pass
    
    def calculate_monthly_aggregates(self):
        # Calculate monthly metrics for reporting
        pass
```

### 5.3 Real-time Processing
- **Stream Processing**: Real-time event processing for live dashboards
- **Batch Processing**: Scheduled aggregation for historical analysis
- **Incremental Updates**: Efficient updates for large datasets

---

## 6. External Dependencies

### 6.1 Service Dependencies
- **All Services**: Event data and direct queries for report generation
- **User Service**: User and business unit context
- **Declaration Service**: Declaration details and status

### 6.2 Event Subscriptions
- **Declaration Events**: All declaration lifecycle events
- **Review Events**: All review workflow events
- **Case Events**: All case management events
- **User Events**: User activity and role changes

---

## 7. Implementation Notes

### 7.1 Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL for aggregated data
- **Time Series**: InfluxDB for high-frequency metrics
- **Caching**: Redis for dashboard data
- **Reports**: ReportLab for PDF generation
- **Charts**: Chart.js or similar for web dashboards

### 7.2 Data Architecture
- **Event Store**: Immutable event log for audit and replay
- **OLAP Cubes**: Pre-aggregated data for fast query performance
- **Data Warehouse**: Historical data for long-term analysis
- **Real-time Views**: Materialized views for live dashboards

### 7.3 Performance Optimization
- **Data Partitioning**: Partition by tenant and time period
- **Indexing Strategy**: Optimize for common query patterns
- **Caching**: Cache dashboard data and frequent queries
- **Parallel Processing**: Parallel report generation for large datasets

---

## 8. Security & Privacy

### 8.1 Data Access Control
- **Role-Based Access**: Different dashboards for different roles
- **Tenant Isolation**: Strict separation of tenant analytics data
- **Anonymization**: Option to anonymize personal data in reports

### 8.2 Audit Requirements
- **Report Access**: Log all report generation and access
- **Data Export**: Track all data exports for compliance
- **Dashboard Usage**: Monitor dashboard access patterns

---

## 9. Testing Strategy

### 9.1 Unit Tests
- Metric calculation algorithms
- Data aggregation logic
- Report generation functions
- Dashboard data preparation

### 9.2 Integration Tests
- Event processing pipeline
- Cross-service data queries
- Report scheduling and delivery
- Dashboard real-time updates

### 9.3 Performance Tests
- Large dataset aggregation
- Concurrent dashboard access
- Report generation under load
- Real-time event processing throughput
