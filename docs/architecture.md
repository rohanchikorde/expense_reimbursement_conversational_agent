# 🏗️ Enterprise Architecture

<div align="center">

![Enterprise](https://img.shields.io/badge/Enterprise-Ready-blue.svg)
![Security](https://img.shields.io/badge/Security-SOC2--Compliant-green.svg)
![Scalability](https://img.shields.io/badge/Scalability-Auto--Scaling-orange.svg)
![Compliance](https://img.shields.io/badge/Compliance-GDPR--Ready-purple.svg)

**Production Enterprise Architecture for the Expense Reimbursement Conversational Agent**

</div>

---

## 🏢 Enterprise Architecture Overview

The Expense Reimbursement Conversational Agent is designed with **enterprise-grade architecture** that ensures security, scalability, compliance, and operational excellence in production environments.

### 🏛️ Enterprise Principles

- **� Security-First**: Zero-trust architecture with comprehensive security controls
- **📈 Scalability**: Auto-scaling architecture supporting thousands of concurrent users
- **�️ Compliance**: GDPR, SOC 2, and enterprise security standards compliance
- **� Observability**: Complete monitoring, logging, and alerting capabilities
- **🔄 Resilience**: Multi-region deployment with automatic failover
- **🔗 Integration**: Enterprise system integration via APIs and webhooks
- **🚀 DevOps**: CI/CD pipelines with automated testing and deployment

---

---

## 🏗️ High-Level Enterprise Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🌐 GLOBAL LOAD BALANCER                            │
│                    (Cloudflare/AWS Global Accelerator)                      │
└─────────────────────┬───────────────────────────────────────────────────────┘
                      │
           ┌──────────▼──────────┐
           │   🌍 REGIONAL HUB   │
           │                     │
           │  ┌─────────────────┐│
           │  │   WAF & DDoS    ││
           │  │   Protection    ││
           │  └─────────────────┘│
           └──────────┬──────────┘
                      │
           ┌──────────▼──────────┐
           │  🏢 ENTERPRISE VPC  │
           │                     │
           │  ┌─────┬─────┬─────┐ │
           │  │ DMZ │ APP │ DB  │ │
           │  │     │     │     │ │
           │  └─────┴─────┴─────┘ │
           └─────────────────────┘
                      │
           ┌──────────▼──────────┐
           │   🚀 APPLICATION    │
           │                     │
           │  ┌─────────────────┐│
           │  │  API Gateway    ││
           │  │  ┌─────────────┐ ││
           │  │  │ Streamlit  │ ││
           │  │  │   UI       │ ││
           │  │  └─────────────┘ ││
           │  └─────────────────┘│
           │                     │
           │  ┌─────────────────┐│
           │  │  LangGraph     ││
           │  │  Workflow      ││
           │  │  ┌─────────────┐ ││
           │  │  │ AI Agents  │ ││
           │  │  │ System     │ ││
           │  │  └─────────────┘ ││
           │  └─────────────────┘│
           └─────────────────────┘
                      │
           ┌──────────▼──────────┐
           │   💾 DATA LAYER     │
           │                     │
           │  ┌─────┬─────┬─────┐ │
           │  │ RDS │ S3  │     │ │
           │  │     │     │     │ │
           │  └─────┴─────┴─────┘ │
           └─────────────────────┘
```

---

## 🔒 Security Architecture

### Zero-Trust Security Model

#### **Authentication & Authorization**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Identity  │───▶│   OAuth2/   │───▶│  JWT Token  │
│  Provider  │    │   SAML      │    │  Validation │
│ (Azure AD/  │    │             │    │             │
│  Okta/AD)  │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
                      │
                      ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  RBAC       │───▶│  API       │───▶│  Resource   │
│  Policies   │    │  Gateway   │    │  Access     │
│             │    │  (Kong/    │    │  Control    │
│             │    │  Apigee)   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### **Network Security Layers**
- **Perimeter Security**: WAF, DDoS protection, IP whitelisting
- **Network Segmentation**: VPC isolation, security groups, NACLs
- **Application Security**: Input validation, rate limiting, CORS policies
- **Data Security**: Encryption at rest/transit, key management

#### **Secrets Management**
```yaml
# AWS Secrets Manager / Azure Key Vault
secrets:
  openrouter_api_key:
    type: SecureString
    rotation: automatic
    access_policy: restricted-to-app-role

  database_credentials:
    type: SecureString
    rotation: 30-days
```

### Data Protection

#### **Encryption Strategy**
- **Data at Rest**: AES-256 encryption for all stored data
- **Data in Transit**: TLS 1.3 with perfect forward secrecy
- **Key Management**: HSM-backed key rotation every 90 days

#### **Data Classification**
| Data Type | Classification | Protection Level |
|-----------|----------------|------------------|
| Receipt Images | Sensitive | Encrypted, access logged |
| PII Data | Confidential | Tokenized, masked |
| Financial Data | Restricted | Encrypted, audit trailed |
| LLM Responses | Internal | Encrypted, retention 90d |

---

## 📈 Scalability Architecture

### Auto-Scaling Strategy

#### **Horizontal Scaling**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load          │───▶│   Application   │───▶│   Database      │
│   Balancer      │    │   Auto Scaling  │    │   Read Replicas │
│                 │    │   Group         │    │                 │
│ • Health Checks │    │ • CPU > 70%     │    │ • Connection    │
│ • Session       │    │ • Memory > 80%  │    │   Pooling       │
│   Affinity      │    │ • Request Queue │    │ • Read/Write    │
│                 │    │   > 100         │    │   Splitting     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **Scaling Policies**
```yaml
# Application Auto Scaling
scaling_policies:
  cpu_based:
    metric: CPUUtilization
    target: 70
    min_capacity: 2
    max_capacity: 20

  request_based:
    metric: RequestCountPerTarget
    target: 1000
    min_capacity: 2
    max_capacity: 50

  custom_metric:
    metric: WorkflowQueueDepth
    target: 10
    min_capacity: 2
    max_capacity: 100
```

### Performance Optimization

#### **Caching Strategy**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  CloudFront │───▶│  API        │───▶│  Redis      │
│  CDN        │    │  Gateway    │    │  Cache      │
│             │    │  Caching    │    │             │
│ • Static    │    │ • Response  │    │ • Session    │
│   Assets    │    │   Caching   │    │   State      │
│ • Images    │    │ • Rate      │    │ • Workflow   │
│             │    │   Limiting  │    │   Results    │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### **Database Optimization**
- **Connection Pooling**: PgBouncer for PostgreSQL
- **Read Replicas**: Geographic distribution
- **Sharding**: Horizontal partitioning by tenant/region
- **Indexing**: Composite indexes on query patterns

---

## 📊 Observability Architecture

### Monitoring Stack

#### **Metrics Collection**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Application │───▶│   Prometheus │───▶│  Grafana    │
│   Metrics   │    │   Metrics    │    │  Dashboards │
│             │    │   Collection │    │             │
│ • Response  │    │ • Custom     │    │ • SLO/SLI    │
│   Time      │    │   Business   │    │   Tracking   │
│ • Error     │    │   Metrics    │    │ • Alerting   │
│   Rates     │    │ • Performance │    │             │
│ • Throughput│    │   Metrics    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### **Key Metrics**
```yaml
# Business Metrics
business_metrics:
  - name: expense_processing_duration
    type: histogram
    buckets: [1, 5, 10, 30, 60, 300]
    labels: [department, approval_type]

  - name: ocr_accuracy
    type: gauge
    description: "OCR text extraction accuracy percentage"

  - name: auto_approval_rate
    type: gauge
    description: "Percentage of expenses auto-approved"

# Technical Metrics
technical_metrics:
  - name: llm_api_latency
    type: histogram
    description: "LLM API response time"

  - name: workflow_queue_depth
    type: gauge
    description: "Number of queued workflows"

  - name: agent_processing_time
    type: histogram
    labels: [agent_name]
```

### Logging Architecture

#### **Structured Logging**
```json
{
  "timestamp": "2024-01-15T10:30:45Z",
  "level": "INFO",
  "service": "expense-agent",
  "component": "receipt-processor",
  "request_id": "req-12345",
  "user_id": "user-67890",
  "operation": "ocr_processing",
  "duration_ms": 2340,
  "metadata": {
    "image_size": "1024x768",
    "confidence_score": 0.95,
    "text_length": 450
  }
}
```

#### **Log Aggregation**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Application │───▶│   Fluentd   │───▶│  Elasticsearch│
│   Logs      │    │   Collector │    │              │
│             │    │             │    │ • Indexing   │
│ • Structured│    │ • Filtering │    │ • Search     │
│ • JSON      │    │ • Enrichment│    │ • Analytics  │
│ • Multi-    │    │             │    │              │
│   level     │    │             │    │              │
└─────────────┘    └─────────────┘    └─────────────────┘
                      │
                      ▼
           ┌─────────────────┐
           │   Kibana        │
           │   Dashboards    │
           │                 │
           │ • Log Analysis  │
           │ • Error Tracking│
           │ • Performance   │
           │   Monitoring    │
           └─────────────────┘
```

### Alerting Strategy

#### **Alert Hierarchy**
```yaml
alerts:
  # Critical Alerts (Page immediately)
  critical:
    - name: service_down
      condition: up == 0
      severity: critical
      channels: [pagerduty, slack, email]

    - name: high_error_rate
      condition: rate(errors_total[5m]) > 0.1
      severity: critical

  # Warning Alerts (Monitor closely)
  warning:
    - name: high_latency
      condition: histogram_quantile(0.95, rate(http_request_duration_seconds[5m])) > 30
      severity: warning

    - name: queue_depth_high
      condition: workflow_queue_depth > 100
      severity: warning

  # Info Alerts (Track trends)
  info:
    - name: deployment_completed
      condition: deployment_status == "success"
      severity: info
```

---

## 🛡️ Compliance Architecture

### Regulatory Compliance

#### **GDPR Compliance**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Data        │───▶│ Consent     │───▶│ Right to    │
│ Collection  │    │ Management │    │ be Forgotten│
│             │    │             │    │             │
│ • Minimal   │    │ • User      │    │ • Data      │
│   Data      │    │   Consent   │    │   Deletion  │
│ • Purpose   │    │ • Granular  │    │ • Audit     │
│   Limitation│    │   Controls  │    │   Trail     │
└─────────────┘    └─────────────┘    └─────────────┘
                      │
                      ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Data       │───▶│ Encryption │───▶│ Access     │
│ Residency  │    │ at Rest    │    │ Logging     │
│             │    │            │    │             │
│ • EU Data  │    │ • AES-256  │    │ • Who/When/ │
│   Location │    │ • Key      │    │   What       │
│ • Cross-   │    │   Rotation │    │ • Compliance │
│   Border   │    │            │    │   Reports    │
│   Controls │    │            │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### **SOC 2 Compliance**
- **Security**: Access controls, encryption, network security
- **Availability**: SLA monitoring, disaster recovery, redundancy
- **Processing Integrity**: Data validation, error handling, audit trails
- **Confidentiality**: Data classification, access controls, encryption
- **Privacy**: Data handling procedures, consent management

### Audit Architecture

#### **Audit Trail**
```sql
-- Audit table structure
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255)
);

-- Partitioning by month for performance
CREATE INDEX CONCURRENTLY ON audit_log (timestamp);
```

#### **Compliance Reporting**
- **Automated Reports**: Daily/weekly/monthly compliance reports
- **Data Retention**: Configurable retention policies (7 years for financial data)
- **Access Reviews**: Quarterly access entitlement reviews
- **Incident Response**: 24/7 incident response with documented procedures

---

## 🔄 Disaster Recovery Architecture

### Multi-Region Deployment

#### **Active-Active Configuration**
```
┌─────────────────┐          ┌─────────────────┐
│   Region 1      │          │   Region 2      │
│   (Primary)     │◄────────►│   (Secondary)   │
│                 │          │                 │
│ ┌─────────────┐ │          │ ┌─────────────┐ │
│ │ Application │ │          │ │ Application │ │
│ │   Fleet     │ │          │ │   Fleet     │ │
│ └─────────────┘ │          │ └─────────────┘ │
│                 │          │                 │
│ ┌─────────────┐ │          │ ┌─────────────┐ │
│ │ Database    │ │          │ │ Database    │ │
│ │ Read/Write  │ │          │ │ Read/Write  │ │
│ └─────────────┘ │          │ └─────────────┘ │
└─────────────────┘          └─────────────────┘
         │                            │
         └────────────────────────────┘
               Global Load Balancer
```

#### **RTO/RPO Targets**
| Component | RTO | RPO | Strategy |
|-----------|-----|-----|----------|
| Application | 15 min | 0 | Blue-green deployment |
| Database | 30 min | 5 min | Multi-AZ with replicas |
| File Storage | 1 hour | 15 min | Cross-region replication |
| DNS | 5 min | N/A | Global DNS with health checks |

### Backup Strategy

#### **Multi-Layer Backup**
```yaml
backup_strategy:
  # Database backups
  database:
    frequency: hourly
    retention: 30 days
    type: incremental
    location: s3://backups/database/

  # Application state
  application:
    frequency: daily
    retention: 90 days
    type: snapshot
    location: s3://backups/application/

  # Configuration
  configuration:
    frequency: on-change
    retention: 1 year
    type: git + s3
    location: s3://backups/config/

  # Logs
  logs:
    frequency: hourly
    retention: 90 days
    type: compressed
    location: s3://backups/logs/
```

---

## 🔗 Integration Architecture

### Enterprise System Integration

#### **ERP Integration**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Expense     │───▶│   API       │───▶│   ERP       │
│ Agent       │    │   Gateway   │    │   System    │
│             │    │             │    │             │
│ • Approval  │    │ • RESTful   │    │ • SAP       │
│   Status    │    │ • GraphQL   │    │ • Oracle    │
│ • Expense   │    │ • Webhooks  │    │ • Workday   │
│   Data      │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### **Identity Integration**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   HR        │───▶│   Identity  │───▶│ Expense     │
│   System    │    │   Provider  │    │ Agent       │
│             │    │             │    │             │
│ • Employee  │    │ • SAML      │    │ • SSO       │
│   Data      │    │ • OAuth2    │    │ • RBAC      │
│ • Org       │    │ • SCIM      │    │ • User      │
│   Structure │    │             │    │   Sync      │
└─────────────┘    └─────────────┘    └─────────────┘
```

### API Architecture

#### **RESTful API Design**
```yaml
openapi: 3.0.3
info:
  title: Expense Reimbursement Agent API
  version: 1.0.0

paths:
  /expenses:
    post:
      summary: Submit expense for processing
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                receipt:
                  type: string
                  format: binary
                metadata:
                  type: object
      responses:
        '202':
          description: Expense submitted for processing
          headers:
            Location:
              schema:
                type: string
              description: URL to check processing status

  /expenses/{id}/status:
    get:
      summary: Get expense processing status
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Processing status
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExpenseStatus'
```

---

## 🚀 DevOps Architecture

### CI/CD Pipeline

#### **GitOps Workflow**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Git Push  │───▶│   CI/CD     │───▶│   Staging   │
│             │    │   Pipeline  │    │   Deploy    │
│ • Code      │    │             │    │             │
│ • Config    │    │ • Unit      │    │ • Smoke     │
│ • Tests     │    │   Tests     │    │   Tests     │
│             │    │ • Security  │    │ • Integration│
│             │    │   Scan      │    │   Tests     │
└─────────────┘    └─────────────┘    └─────────────────┘
                      │
                      ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Approval   │───▶│ Production │───▶│ Monitoring  │
│  Gate       │    │   Deploy   │    │             │
│             │    │             │    │ • Health    │
│ • Manual    │    │ • Blue-     │    │   Checks    │
│   Review    │    │   Green     │    │ • Metrics   │
│ • Automated │    │ • Canary    │    │ • Alerts    │
│   Checks    │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

#### **Infrastructure as Code**
```hcl
# Terraform module structure
modules/
├── vpc/           # Network infrastructure
├── security/      # Security groups, WAF
├── application/   # ECS/EC2 configuration
├── database/      # RDS configuration
├── monitoring/    # CloudWatch, alerts
└── pipeline/      # CodePipeline configuration
```

### Environment Strategy

#### **Multi-Environment Setup**
```yaml
environments:
  development:
    instances: 1
    instance_type: t3.small
    auto_scaling:
      min: 1
      max: 2

  staging:
    instances: 2
    instance_type: t3.medium
    auto_scaling:
      min: 2
      max: 4

  production:
    instances: 4
    instance_type: t3.large
    auto_scaling:
      min: 4
      max: 20
    multi_az: true
    backup_retention: 30
```

---

## 📋 Operational Architecture

### Service Level Objectives

#### **SLO Definitions**
```yaml
service_level_objectives:
  availability:
    target: 99.9%  # 8.77 hours downtime/year
    measurement_window: 30d
    error_budget: 0.1%

  latency:
    target: 95% of requests < 5s
    measurement_window: 1h

  throughput:
    target: 1000 requests/second
    measurement_window: 1h

  accuracy:
    ocr_accuracy: 95%
    classification_accuracy: 90%
    auto_approval_rate: 75%
```

### Capacity Planning

#### **Resource Forecasting**
```python
# Capacity planning calculations
def calculate_capacity_requirements(user_count, avg_request_rate):
    # Application servers
    app_servers = math.ceil((user_count * avg_request_rate) / 1000)

    # Database connections
    db_connections = app_servers * 10

    # Cache requirements
    cache_memory_gb = (user_count * 0.1) / 1024  # 100KB per user

    return {
        'app_servers': app_servers,
        'db_connections': db_connections,
        'cache_memory_gb': cache_memory_gb
    }
```

---

## 🔮 Future Architecture Evolution

### Microservices Migration Path

#### **Phase 1: Service Extraction**
```
┌─────────────────┐    ┌─────────────────┐
│   Monolith      │───▶│   Receipt       │
│   Application   │    │   Service       │
│                 │    │                 │
│ • OCR           │    │ • OCR Processing│
│ • Classification│    │ • Image Storage │
│ • Workflow      │    │                 │
└─────────────────┘    └─────────────────┘
```

#### **Phase 2: Domain Services**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Receipt       │    │   Classification│    │   Workflow      │
│   Service       │    │   Service       │    │   Service       │
│                 │    │                 │    │                 │
│ • OCR           │    │ • ML Models     │    │ • State Mgmt    │
│ • Image Storage │    │ • Training      │    │ • Orchestration │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### **Phase 3: Event-Driven Architecture**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Event      │───▶│  Event      │───▶│  Event      │
│  Producer   │    │  Stream     │    │  Consumer   │
│             │    │  Processing │    │             │
│ • Receipt   │    │ • Kafka/    │    │ • Async      │
│   Uploaded  │    │   Kinesis   │    │   Processing │
│ • Expense   │    │             │    │ • Real-time  │
│   Processed │    │             │    │   Updates    │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

<div align="center">

**🏢 Enterprise-ready architecture for mission-critical expense processing**

[⬆️ Back to Top](#️-enterprise-architecture) • [🚀 Deployment](deployment.md) • [📊 Monitoring](monitoring.md) • [🏠 Home](../README.md)

</div>

---

## 🔍 Detailed Component Analysis

### 🎨 User Interface Layer

#### Streamlit Application (`app.py`)

**Responsibilities:**
- File upload handling for receipt images
- Conversational chat interface
- Real-time status updates and progress indicators
- Interrupt handling for human clarification
- Session state management

**Key Features:**
```python
# Session management
st.session_state.thread_id
st.session_state.workflow_started
st.session_state.last_interrupt

# UI components
st.file_uploader("Upload receipt")
st.chat_message("assistant")
st.chat_input("Your response")
```

### 🔄 Workflow Orchestration Layer

#### LangGraph Workflow (`src/workflow.py`)

**Core Components:**
- **StateGraph**: Defines the workflow structure
- **MemorySaver**: Provides checkpointing for HITL
- **Interrupt Handling**: Pauses for human input
- **Agent Routing**: Deterministic next-agent selection

**Workflow Definition:**
```python
workflow = StateGraph(ExpenseState)

# Add nodes (agents)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("receipt_processor", receipt_processor_agent_node)
# ... other agents

# Define edges
workflow.add_edge(START, "supervisor")
workflow.add_edge("receipt_processor", "supervisor")
# ... other connections

# Compile with checkpointer
app = workflow.compile(checkpointer=MemorySaver())
```

### 🤖 Agent Layer

#### Supervisor Agent (`src/agents/supervisor.py`)

**Decision Logic:**
```python
def supervisor_agent(state: ExpenseState) -> Command:
    if not state.get("ocr_complete", False):
        return Command(goto="receipt_processor", update=state)
    elif not state.get("country_identified", False):
        return Command(goto="location_analyst", update=state)
    # ... additional routing logic
```

**Routing Table:**

| Condition | Next Agent | Purpose |
|-----------|------------|---------|
| `not ocr_complete` | `receipt_processor` | Extract text from receipt |
| `not country_identified` | `location_analyst` | Determine geographic context |
| `not department_confirmed` | `classification` | Classify expense type |
| `needs_clarification` | `hitl` | Human clarification needed |
| `not rules_applied` | `policy_engine` | Apply business rules |
| `policy_violation` | `exception_handler` | Handle violations |
| `not approval_determined` | `approval_router` | Final approval decision |
| All complete | `finalize` | Complete workflow |

#### Receipt Processor Agent (`src/agents/receipt_processor.py`)

**OCR Pipeline:**
```python
def receipt_processor_agent_node(state: ExpenseState) -> Command:
    # 1. Extract text using Tesseract
    text = pytesseract.image_to_string(state["receipt_image"])

    # 2. Parse with LLM
    response = llm.invoke([HumanMessage(content=prompt)])
    info = extract_json_from_llm_response(response.content)

    # 3. Update state
    state.update(info)
    state["ocr_complete"] = True

    return Command(goto="supervisor", update=state)
```

#### Location Analyst Agent (`src/agents/location_analyst.py`)

**Geographic Analysis:**
```python
def location_analyst_agent_node(state: ExpenseState) -> Command:
    locations = f"{state.get('pickup_location', '')} {state.get('dropoff_location', '')}"
    prompt = f"Identify the country from these locations: {locations}"

    response = llm.invoke([HumanMessage(content=prompt)])
    country = response.content.strip()

    state["country"] = country
    state["country_identified"] = True

    return Command(goto="supervisor", update=state)
```

#### Classification Agent (`src/agents/classification.py`)

**Expense Classification:**
```python
def classification_agent_node(state: ExpenseState) -> Command:
    prompt = f"""
    Analyze this expense:
    Dropoff: {state.get('dropoff_location', '')}
    Date: {state.get('expense_date', '')}
    Amount: {state.get('amount', '')}

    Infer department and purpose. Confidence 0-100.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    parsed = extract_json_from_llm_response(response.content)

    if parsed["confidence"] < CLASSIFICATION_CONFIDENCE_THRESHOLD:
        state["needs_clarification"] = True
        return Command(goto="hitl", update=state)
    else:
        state["department_confirmed"] = True
        return Command(goto="supervisor", update=state)
```

#### HITL Agent (`src/agents/hitl.py`)

**Human-in-the-Loop:**
```python
def hitl_agent_node(state: ExpenseState) -> Command:
    clarification_questions = state.get("clarification_questions", [])

    # Create interrupt for user input
    interrupt_message = f"""
    I need clarification for this expense:
    {chr(10).join(f"- {q}" for q in clarification_questions)}
    """

    # This will pause execution and wait for user input
    return Command(interrupt=interrupt_message, update=state)
```

#### Policy Engine Agent (`src/agents/policy_engine.py`)

**Business Rules Application:**
```python
def policy_engine_agent_node(state: ExpenseState) -> Command:
    amount = state.get("amount", 0)
    expense_date = state.get("expense_date", "")

    # Apply approval rules
    if expense_date < "2024-01-01":
        threshold = 50.00
    else:
        threshold = 75.00

    if amount <= threshold:
        state["requires_manager_approval"] = False
        state["applied_rule"] = f"Auto-approved: amount ≤ ${threshold}"
    else:
        state["requires_manager_approval"] = True
        state["applied_rule"] = f"Requires approval: amount > ${threshold}"

    state["rules_applied"] = True
    return Command(goto="supervisor", update=state)
```

#### Approval Router Agent (`src/agents/approval_router.py`)

**Final Approval Decision:**
```python
def approval_router_agent_node(state: ExpenseState) -> Command:
    if state.get("policy_violation", False):
        state["approval_status"] = "rejected"
    elif state.get("requires_manager_approval", False):
        state["approval_status"] = "requires_approval"
    else:
        state["approval_status"] = "auto_approved"

    state["approval_determined"] = True
    return Command(goto="supervisor", update=state)
```

#### Finalize Agent (`src/agents/finalize.py`)

**Workflow Completion:**
```python
def finalize_agent_node(state: ExpenseState) -> Command:
    # Log completion
    print("=== WORKFLOW COMPLETED ===")

    # Add completion message
    state["messages"].append(AIMessage(content="Expense processing completed."))

    # Return final state (workflow ends)
    return Command(update=state)
```

---

## 📊 State Management

### ExpenseState Schema (`src/types/state.py`)

```python
class ExpenseState(TypedDict):
    # Receipt processing
    receipt_image: Optional[Image.Image]
    ocr_text: str
    ocr_complete: bool

    # Extracted data
    amount: Optional[float]
    currency: Optional[str]
    expense_date: Optional[str]
    merchant: Optional[str]
    pickup_location: Optional[str]
    dropoff_location: Optional[str]

    # Geographic context
    country: Optional[str]
    city: Optional[str]
    country_identified: bool

    # Classification
    department: Optional[str]
    purpose: Optional[str]
    classification_confidence: Optional[int]
    department_confirmed: bool

    # Human clarification
    needs_clarification: bool
    clarification_questions: List[str]
    user_provided_context: Optional[str]

    # Business rules
    rules_applied: bool
    applied_rule: Optional[str]
    requires_manager_approval: Optional[bool]
    approval_status: Optional[str]
    policy_violation: bool
    violations: List[str]

    # Workflow control
    current_agent: Optional[str]
    messages: List[Union[HumanMessage, AIMessage]]
    employee_id: str
    approval_determined: bool
```

### State Transitions

```
Initial State
    ↓ (receipt upload)
OCR Processing → Data Extraction
    ↓
Geographic Analysis → Country Identification
    ↓
Expense Classification → Department/Purpose
    ↓ (if unclear)
Human Clarification ←→ Re-classification
    ↓
Policy Application → Rule Evaluation
    ↓ (if violation)
Exception Handling → Violation Resolution
    ↓
Approval Routing → Final Decision
    ↓
Workflow Finalization → Completion
```

---

## 🔄 Data Flow

### Receipt Processing Pipeline

```
Receipt Image
    ↓
Tesseract OCR → Raw Text
    ↓
LLM Extraction → Structured Data
    ↓
State Update → Next Agent
```

### Classification Pipeline

```
Structured Data
    ↓
LLM Analysis → Department & Purpose
    ↓
Confidence Check → High/Low Confidence
    ↓
Auto-Classification ←→ Human Clarification
    ↓
Confirmed Classification
```

### Approval Pipeline

```
Classification + Amount + Date
    ↓
Rule Evaluation → Approval Threshold
    ↓
Auto-Approval ←→ Manager Review
    ↓
Final Status
```

---

## 🛡️ Error Handling & Resilience

### Exception Handling Strategy

1. **OCR Failures**: Fallback to mock data with user notification
2. **LLM Errors**: Retry with exponential backoff
3. **State Corruption**: Checkpoint restoration
4. **Network Issues**: Graceful degradation with cached responses

### Logging & Monitoring

```python
# Structured logging throughout agents
logger.info("OCR processing started", extra={
    "agent": "receipt_processor",
    "image_size": image.size,
    "timestamp": datetime.now()
})
```

---

## 🔧 Configuration Management

### Settings Hierarchy (`src/config/settings.py`)

```python
# API Configuration
LLM_MODEL = "anthropic/claude-3-haiku"
LLM_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Processing Thresholds
CLASSIFICATION_CONFIDENCE_THRESHOLD = 70
OCR_CONFIDENCE_THRESHOLD = 80

# Business Rules
AUTO_APPROVAL_THRESHOLD_PRE_2024 = 50.00
AUTO_APPROVAL_THRESHOLD_POST_2024 = 75.00
```

### Environment Variables

```bash
# .env file
OPENROUTER_API_KEY=your_api_key
DEBUG=true  # Enable debug logging
LOG_LEVEL=INFO
```

---

## 🚀 Performance Considerations

### Optimization Strategies

- **Lazy Loading**: Load agents only when needed
- **Caching**: Cache LLM responses for repeated queries
- **Async Processing**: Non-blocking I/O operations
- **Memory Management**: Clean up large objects (images)

### Performance Metrics

| Component | Target | Current |
|-----------|--------|---------|
| OCR Processing | <5s | ~2s |
| LLM Inference | <10s | ~3s |
| Total Processing | <30s | ~15s |
| Memory Usage | <500MB | ~200MB |

---

## 🔮 Extensibility

### Adding New Agents

1. **Create Agent Module**
   ```python
   # src/agents/new_agent.py
   def new_agent_node(state: ExpenseState) -> Command:
       # Agent logic here
       return Command(goto="supervisor", update=state)
   ```

2. **Register in Workflow**
   ```python
   # src/workflow.py
   workflow.add_node("new_agent", new_agent_node)
   workflow.add_edge("new_agent", "supervisor")
   ```

3. **Update Supervisor Logic**
   ```python
   # src/agents/supervisor.py
   elif condition_for_new_agent:
       next_agent = "new_agent"
   ```

### Customizing Business Rules

```python
# src/agents/policy_engine.py
def apply_custom_rules(state: ExpenseState) -> None:
    # Custom business logic
    if custom_condition:
        state["custom_flag"] = True
```

---

## 🧪 Testing Architecture

### Test Structure

```
tests/
├── unit/              # Unit tests for individual agents
├── integration/       # Integration tests for workflows
├── e2e/              # End-to-end user journey tests
└── fixtures/         # Test data and mock objects
```

### Test Categories

- **Unit Tests**: Individual agent functions
- **Integration Tests**: Agent-to-agent communication
- **Workflow Tests**: Complete state transitions
- **UI Tests**: Streamlit interface interactions

---

<div align="center">

**🏢 Enterprise-ready architecture for mission-critical expense processing**

[⬆️ Back to Top](#️-enterprise-architecture) • [🚀 Deployment](deployment.md) • [🔧 Troubleshooting](troubleshooting.md) • [🏠 Home](../README.md)

</div>