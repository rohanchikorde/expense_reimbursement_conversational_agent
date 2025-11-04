# 🚀 Deployment Guide

<div align="center">

![Deployment](https://img.shields.io/badge/Deployment-Ready-green.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)
![Cloud](https://img.shields.io/badge/Cloud-AWS%20%7C%20GCP%20%7C%20Azure-orange.svg)

**Complete deployment guide for the Expense Reimbursement Conversational Agent**

</div>

---

## 📋 Deployment Options

### 🐳 Docker Deployment (Recommended)

#### **Quick Docker Setup**

1. **Build the Docker image**
   ```bash
   docker build -t expense-agent .
   ```

2. **Run with environment variables**
   ```bash
   docker run -p 8505:8505 \
     -e OPENROUTER_API_KEY=your-api-key \
     -e LLM_MODEL=anthropic/claude-3-haiku \
     expense-agent
   ```

3. **Access the application**
   ```
   http://localhost:8505
   ```

#### **Docker Compose (Production)**
```yaml
# docker-compose.yml
version: '3.8'
services:
  expense-agent:
    build: .
    ports:
      - "8505:8505"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - LLM_MODEL=anthropic/claude-3-haiku
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

```bash
# Deploy with compose
docker-compose up -d
```

### ☸️ Kubernetes Deployment (Enterprise)

#### **Production Kubernetes Setup**

1. **Prerequisites**
   ```bash
   # Required tools
   kubectl version --client
   helm version
   kustomize version

   # Cluster requirements
   # - Kubernetes 1.24+
   # - 3+ nodes for HA
   # - Storage class for persistent volumes
   # - Ingress controller (NGINX/Ingress)
   # - Cert-manager for TLS
   ```

2. **Deploy with Helm**
   ```bash
   # Add helm repository
   helm repo add expense-agent https://charts.expense-agent.com
   helm repo update

   # Create namespace
   kubectl create namespace expense-agent

   # Install with production values
   helm install expense-agent expense-agent/expense-agent \
     --namespace expense-agent \
     --values production-values.yaml \
     --create-namespace
   ```

3. **Production Helm Values**
   ```yaml
   # production-values.yaml
   replicaCount: 3

   image:
     repository: expense-agent
     tag: "v1.2.3"
     pullPolicy: IfNotPresent

   service:
     type: ClusterIP
     port: 8505

   ingress:
     enabled: true
     className: nginx
     annotations:
       cert-manager.io/cluster-issuer: "letsencrypt-prod"
       nginx.ingress.kubernetes.io/ssl-redirect: "true"
       nginx.ingress.kubernetes.io/rate-limit: "100"
       nginx.ingress.kubernetes.io/rate-limit-window: "1m"
     hosts:
       - host: expenses.company.com
         paths:
           - path: /
             pathType: Prefix
     tls:
       - secretName: expense-agent-tls
         hosts:
           - expenses.company.com

   resources:
     limits:
       cpu: 1000m
       memory: 2Gi
     requests:
       cpu: 500m
       memory: 1Gi

   autoscaling:
     enabled: true
     minReplicas: 3
     maxReplicas: 10
     targetCPUUtilizationPercentage: 70
     targetMemoryUtilizationPercentage: 80

   # Database configuration
   database:
     enabled: true
     postgresql:
       enabled: true
       auth:
         database: expense_agent
         username: expense_user
       architecture: replication
       primary:
         persistence:
           enabled: true
           size: 50Gi
       readReplicas:
         persistence:
           enabled: true
           size: 50Gi

   # Redis for caching
   redis:
     enabled: true
     architecture: replication
     auth:
       enabled: true
     master:
       persistence:
         enabled: true
         size: 10Gi

   # Monitoring
   prometheus:
     enabled: true
     serviceMonitor:
       enabled: true

   grafana:
     enabled: true
     adminPassword: "change-me-in-production"

   # Security
   podSecurityContext:
     runAsNonRoot: true
     runAsUser: 1001
     fsGroup: 1001

   securityContext:
     allowPrivilegeEscalation: false
     readOnlyRootFilesystem: true
     runAsNonRoot: true
     runAsUser: 1001
     capabilities:
       drop:
         - ALL

   # Secrets management
   secrets:
     openrouterApiKey: "openrouter-api-key-secret"
     databaseUrl: "database-secret"
     jwtSecret: "jwt-secret"

   # Network policies
   networkPolicy:
     enabled: true
     ingressRules:
       - from:
           - namespaceSelector:
               matchLabels:
                 name: ingress-nginx
         ports:
           - port: 8505
   ```

#### **Kubernetes Resources**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: expense-agent
  namespace: expense-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: expense-agent
  template:
    metadata:
      labels:
        app: expense-agent
    spec:
      serviceAccountName: expense-agent-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
      containers:
      - name: expense-agent
        image: expense-agent:v1.2.3
        ports:
        - containerPort: 8505
        env:
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: expense-agent-secrets
              key: openrouter-api-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: expense-agent-secrets
              key: database-url
        resources:
          limits:
            cpu: 1000m
            memory: 2Gi
          requests:
            cpu: 500m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8505
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8505
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1001
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - expense-agent
              topologyKey: kubernetes.io/hostname
```

### 🔗 Service Mesh Integration

#### **Istio Service Mesh**
```yaml
# istio-config.yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: expense-agent-gateway
  namespace: expense-agent
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: expense-agent-tls
    hosts:
    - expenses.company.com

---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: expense-agent
  namespace: expense-agent
spec:
  hosts:
  - expenses.company.com
  gateways:
  - expense-agent-gateway
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: expense-agent
        port:
          number: 8505
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
    corsPolicy:
      allowOrigins:
      - exact: https://app.company.com
      allowMethods: ["GET", "POST", "PUT", "DELETE"]
      allowHeaders: ["*"]
      allowCredentials: true

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: expense-agent-auth
  namespace: expense-agent
spec:
  selector:
    matchLabels:
      app: expense-agent
  action: ALLOW
  rules:
  - from:
    - source:
        requestPrincipals: ["*"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/*"]
```

### 🏢 Enterprise Integration Patterns

#### **API Gateway Integration**
```yaml
# Kong Gateway Configuration
kong_config:
  services:
    - name: expense-agent
      url: http://expense-agent.expense-agent.svc.cluster.local:8505
      routes:
        - name: expense-agent-route
          paths:
            - /api/expenses
          methods: ["GET", "POST"]
          strip_path: false

  plugins:
    - name: cors
      service: expense-agent
      config:
        origins:
          - https://app.company.com
        methods: ["GET", "POST", "PUT", "DELETE"]
        headers: ["Authorization", "Content-Type"]
        credentials: true

    - name: rate-limiting
      service: expense-agent
      config:
        minute: 100
        hour: 1000
        policy: local

    - name: request-transformer
      service: expense-agent
      config:
        add:
          headers:
            - "X-API-Key:$(req.header.apikey)"

    - name: jwt
      service: expense-agent
      config:
        secret_is_base64: false
        run_on_preflight: true
```

#### **Enterprise Service Bus (ESB) Integration**
```xml
<!-- MuleSoft ESB Configuration -->
<mule xmlns="http://www.mulesoft.org/schema/mule/core"
      xmlns:http="http://www.mulesoft.org/schema/mule/http"
      xmlns:expense="http://www.company.com/schema/expense">

    <http:listener-config name="HTTP_Listener_config"
                         host="0.0.0.0" port="8081"/>

    <flow name="expense-integration-flow">
        <http:listener config-ref="HTTP_Listener_config"
                      path="/expenses"/>

        <expense:validate-expense-request/>

        <http:request config-ref="ExpenseAgent_HTTP_Request_config"
                     path="/api/expenses"
                     method="POST">
            <http:body>#[payload]</http:body>
        </http:request>

        <expense:transform-response/>

        <logger level="INFO" message="Expense processed: #[payload.id]"/>
    </flow>
</mule>
```

### 🔐 Advanced Security Deployments

#### **Zero-Trust Architecture**
```yaml
# OPA Gatekeeper Policies
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: expense-agent-required-labels
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces: ["expense-agent"]
  parameters:
    labels:
      - key: security.scan/snyk
        allowedValues: ["passed"]
      - key: security.scan/trivy
        allowedValues: ["passed"]

---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPSPHostFilesystem
metadata:
  name: expense-agent-host-filesystem
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces: ["expense-agent"]
  parameters:
    allowedHostPaths:
      - pathPrefix: "/tmp"
        readOnly: false
```

#### **Secrets Management**
```yaml
# External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: expense-agent-secrets
  namespace: expense-agent
spec:
  refreshInterval: 15s
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: expense-agent-secrets
    creationPolicy: Owner
  data:
  - secretKey: openrouter-api-key
    remoteRef:
      key: prod/expense-agent/openrouter-api-key
  - secretKey: database-url
    remoteRef:
      key: prod/expense-agent/database-url
  - secretKey: jwt-secret
    remoteRef:
      key: prod/expense-agent/jwt-secret
```

### 📊 Enterprise Monitoring Stack

#### **Complete Observability Setup**
```yaml
# kube-prometheus-stack values
monitoring:
  prometheus:
    enabled: true
    serviceMonitorSelector: {}
    ruleSelector: {}
    serviceMonitorSelectorNilUsesHelmValues: false
    ruleSelectorNilUsesHelmValues: false
    prometheusSpec:
      retention: 30d
      retentionSize: "50GB"
      resources:
        limits:
          cpu: 2000m
          memory: 8Gi
        requests:
          cpu: 1000m
          memory: 4Gi

  grafana:
    enabled: true
    adminPassword: "change-me-in-production"
    persistence:
      enabled: true
      size: 10Gi
    dashboards:
      expense-agent:
        gnetId: 12345
        revision: 1
        datasource: Prometheus

  alertmanager:
    enabled: true
    config:
      global:
        smtp_smarthost: 'smtp.company.com:587'
        smtp_from: 'alerts@company.com'
      route:
        group_by: ['alertname']
        group_wait: 10s
        group_interval: 10s
        repeat_interval: 1h
        receiver: 'email'
      receivers:
      - name: 'email'
        email_configs:
        - to: 'engineering@company.com'
```

### 🚀 Blue-Green Deployment Strategy

#### **Blue-Green Setup**
```bash
# Create blue environment
kubectl create namespace expense-agent-blue
helm install expense-agent-blue expense-agent/expense-agent \
  --namespace expense-agent-blue \
  --set image.tag=v1.2.3 \
  --set ingress.enabled=false

# Create green environment
kubectl create namespace expense-agent-green
helm install expense-agent-green expense-agent/expense-agent \
  --namespace expense-agent-green \
  --set image.tag=v1.2.4 \
  --set ingress.enabled=false

# Switch traffic to green
kubectl patch ingress expense-agent-ingress \
  --type='json' \
  -p='[{"op": "replace", "path": "/spec/rules/0/http/paths/0/backend/service/name", "value": "expense-agent-green"}]'

# Verify and cleanup
kubectl delete namespace expense-agent-blue
```

### 🔄 CI/CD Pipeline (Enterprise)

#### **GitOps with ArgoCD**
```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: expense-agent
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/company/expense-agent-deploy
    targetRevision: HEAD
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: expense-agent
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
```

#### **Advanced CI/CD Pipeline**
```yaml
# .github/workflows/enterprise-deploy.yml
name: Enterprise Deployment

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=src --cov-report=xml
    - name: Security scan
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - name: Build and push
      uses: docker/build-push-action@v3
      with:
        context: .
        push: true
        tags: expense-agent:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
    - name: Deploy to staging
      uses: azure/k8s-deploy@v1
      with:
        namespace: expense-agent-staging
        manifests: k8s/overlays/staging/
        images: expense-agent:${{ github.sha }}

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
    - name: Manual approval
      uses: trstringer/manual-approval@v1
      with:
        secret: ${{ github.TOKEN }}
        approvers: engineering-manager,product-owner
        minimum-approvals: 2
        issue-title: "Deploy expense-agent to production"
        issue-body: "Please approve or deny the deployment of expense-agent to production"

    - name: Deploy to production
      uses: azure/k8s-deploy@v1
      with:
        namespace: expense-agent
        manifests: k8s/overlays/production/
        images: expense-agent:${{ github.sha }}
```

---

## 🏢 Enterprise Deployment Checklist

### Pre-Deployment
- [ ] Security review completed
- [ ] Performance testing finished
- [ ] Infrastructure capacity verified
- [ ] Backup strategy implemented
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented
- [ ] Communication plan ready

### Deployment Day
- [ ] Pre-deployment backup taken
- [ ] Monitoring dashboards verified
- [ ] Team standup completed
- [ ] Deployment window scheduled
- [ ] Rollback procedures tested
- [ ] Customer communication sent

### Post-Deployment
- [ ] Application health verified
- [ ] Monitoring alerts checked
- [ ] Performance benchmarks run
- [ ] User acceptance testing
- [ ] Documentation updated
- [ ] Retrospective scheduled

---

## 📞 Enterprise Support

### Production Support Model

#### **Support Tiers**
```yaml
support_tiers:
  tier_1:  # L1 Support (24/7)
    response_time: 15min
    resolution_time: 4h
    coverage: 24x7x365
    channels: [phone, email, chat]
    responsibilities:
      - Initial triage
      - Basic troubleshooting
      - Service restart
      - Monitoring alerts

  tier_2:  # L2 Support (Business Hours)
    response_time: 30min
    resolution_time: 8h
    coverage: 8x5x5
    channels: [email, ticket]
    responsibilities:
      - Advanced troubleshooting
      - Code fixes
      - Configuration changes
      - Performance optimization

  tier_3:  # L3 Support (Development Team)
    response_time: 2h
    resolution_time: 24h
    coverage: 8x5x5
    channels: [slack, ticket]
    responsibilities:
      - Root cause analysis
      - Architecture changes
      - New feature development
      - Security patches
```

#### **Escalation Matrix**
```yaml
escalation_matrix:
  severity_1:  # Critical - Service Down
    response: immediate
    notification: [oncall_engineer, engineering_manager, cto]
    communication: [customers, executives]

  severity_2:  # High - Major Feature Impact
    response: 30min
    notification: [oncall_engineer, engineering_manager]
    communication: [product_team, customers]

  severity_3:  # Medium - Minor Feature Impact
    response: 2h
    notification: [assigned_engineer, team_lead]
    communication: [product_team]

  severity_4:  # Low - Cosmetic Issues
    response: 8h
    notification: [assigned_engineer]
    communication: []
```

---

<div align="center">

**🚀 Enterprise-grade deployment for mission-critical expense processing**

[⬆️ Back to Top](#-deployment-guide) • [🏗️ Architecture](architecture.md) • [📊 Monitoring](monitoring.md) • [🏠 Home](../README.md)

</div>

2. **Configure security group**
   - Allow inbound traffic on port 8505
   - Allow SSH (port 22) for management

3. **Install dependencies on EC2**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip tesseract-ocr

   # Install Python dependencies
   pip3 install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   export OPENROUTER_API_KEY=your-api-key
   export LLM_MODEL=anthropic/claude-3-haiku
   ```

5. **Run the application**
   ```bash
   nohup streamlit run app.py --server.port 8505 --server.address 0.0.0.0 &
   ```

#### **Google Cloud Run**

1. **Build and push to GCR**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/expense-agent
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy expense-agent \
     --image gcr.io/PROJECT-ID/expense-agent \
     --platform managed \
     --port 8505 \
     --set-env-vars OPENROUTER_API_KEY=your-api-key \
     --allow-unauthenticated
   ```

#### **Azure Container Instances**

1. **Build and push to ACR**
   ```bash
   az acr build --registry myregistry --image expense-agent .
   ```

2. **Deploy to ACI**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name expense-agent \
     --image myregistry.azurecr.io/expense-agent \
     --ports 8505 \
     --environment-variables OPENROUTER_API_KEY=your-api-key \
     --dns-name-label expense-agent-unique-label
   ```

### 🖥️ Local Development Deployment

#### **Windows Deployment**

1. **Install Python and dependencies**
   ```powershell
   # Install Python 3.8+
   winget install Python.Python.3.8

   # Install Tesseract
   winget install UB-Mannheim.TesseractOCR

   # Create virtual environment
   python -m venv .venv
   .\.venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```powershell
   # Create .env file
   @"
   OPENROUTER_API_KEY=your-api-key-here
   LLM_MODEL=anthropic/claude-3-haiku
   "@ | Out-File -FilePath .env -Encoding UTF8
   ```

3. **Run the application**
   ```powershell
   streamlit run app.py
   ```

#### **Linux/macOS Deployment**

1. **Install system dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install -y python3 python3-pip tesseract-ocr

   # macOS
   brew install python tesseract
   ```

2. **Setup Python environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure and run**
   ```bash
   echo "OPENROUTER_API_KEY=your-api-key" > .env
   streamlit run app.py
   ```

---

## ⚙️ Configuration Management

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API authentication | - | ✅ |
| `LLM_MODEL` | LLM model to use | `anthropic/claude-3-haiku` | ❌ |
| `STREAMLIT_SERVER_PORT` | Port for Streamlit | `8505` | ❌ |
| `STREAMLIT_SERVER_ADDRESS` | Bind address | `localhost` | ❌ |
| `TESSERACT_CMD` | Path to Tesseract binary | Auto-detected | ❌ |

### Advanced Configuration

#### **Custom Settings**
```python
# src/config/settings.py
class Settings:
    # OCR settings
    OCR_CONFIDENCE_THRESHOLD = 0.7
    TESSERACT_CONFIG = r'--oem 3 --psm 6'

    # LLM settings
    LLM_TEMPERATURE = 0.1
    LLM_MAX_TOKENS = 1000

    # Business rules
    AUTO_APPROVE_LIMIT_BEFORE_2024 = 50
    AUTO_APPROVE_LIMIT_AFTER_2024 = 75
```

#### **Docker Environment File**
```bash
# .env.docker
OPENROUTER_API_KEY=your-production-key
LLM_MODEL=anthropic/claude-3-sonnet
STREAMLIT_SERVER_PORT=8505
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
```

---

## 🔒 Security Considerations

### API Key Management

#### **Production Secrets**
```bash
# Use secret managers
# AWS Secrets Manager
aws secretsmanager create-secret \
  --name expense-agent-api-key \
  --secret-string '{"OPENROUTER_API_KEY":"your-key"}'

# Docker secrets
echo "your-api-key" | docker secret create openrouter_api_key -
```

#### **Environment Isolation**
```bash
# Separate environments
export ENV=production
export OPENROUTER_API_KEY=$(aws secretsmanager get-secret-value --secret-id expense-agent-api-key --query SecretString --output text | jq -r .OPENROUTER_API_KEY)
```

### Network Security

#### **Firewall Configuration**
```bash
# UFW (Ubuntu)
sudo ufw allow 8505
sudo ufw allow ssh
sudo ufw --force enable

# Windows Firewall
New-NetFirewallRule -DisplayName "Expense Agent" -Direction Inbound -Protocol TCP -LocalPort 8505 -Action Allow
```

#### **SSL/TLS Setup**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Run with SSL
streamlit run app.py --server.sslCertPath cert.pem --server.sslKeyPath key.pem
```

---

## 📊 Monitoring & Logging

### Application Logging

#### **Configure Logging**
```python
# In app.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/expense_agent.log'),
        logging.StreamHandler()
    ]
)
```

#### **Log Rotation**
```bash
# logrotate configuration
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Health Checks

#### **Application Health Endpoint**
```python
# Add to app.py
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Expose via /health endpoint
```

#### **Docker Health Check**
```yaml
# docker-compose.yml
services:
  expense-agent:
    # ... other config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8505/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Performance Monitoring

#### **Resource Monitoring**
```bash
# Docker stats
docker stats expense-agent

# System monitoring
htop
iotop
nvidia-smi  # For GPU usage
```

#### **APM Integration**
```python
# Add application monitoring
from datadog import initialize, statsd

initialize(api_key='your-datadog-key')
statsd.increment('expense_agent.requests')
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy Expense Agent

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python tests/run_tests.py

    - name: Build Docker image
      run: |
        docker build -t expense-agent .

    - name: Deploy to production
      run: |
        echo "Deployment commands here"
```

### Automated Testing

#### **Pre-deployment Tests**
```bash
# Run full test suite
python tests/run_tests.py

# Performance tests
python tests/performance_tests.py

# Security scan
bandit -r src/
safety check
```

---

## 🚨 Backup & Recovery

### Data Backup

#### **Application Data**
```bash
# Backup configuration
tar -czf backup_$(date +%Y%m%d).tar.gz \
  --exclude='*.log' \
  --exclude='.venv' \
  .

# Database backup (if applicable)
pg_dump expense_db > expense_backup.sql
```

#### **Automated Backups**
```bash
# Cron job for daily backups
0 2 * * * /path/to/backup.sh

# Backup script
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d)
tar -czf $BACKUP_DIR/expense_agent_$DATE.tar.gz /opt/expense_agent
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### Disaster Recovery

#### **Recovery Procedure**
1. **Stop the application**
   ```bash
   docker-compose down
   ```

2. **Restore from backup**
   ```bash
   tar -xzf backup_20231201.tar.gz -C /opt/
   ```

3. **Rebuild and restart**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

4. **Verify functionality**
   ```bash
   curl http://localhost:8505/health
   ```

---

## 📈 Scaling Considerations

### Horizontal Scaling

#### **Load Balancer Setup**
```nginx
# nginx.conf
upstream expense_agents {
    server 127.0.0.1:8505;
    server 127.0.0.1:8506;
    server 127.0.0.1:8507;
}

server {
    listen 80;
    location / {
        proxy_pass http://expense_agents;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### **Multiple Instances**
```bash
# Run multiple instances
docker run -d -p 8505:8505 --name agent-1 expense-agent
docker run -d -p 8506:8505 --name agent-2 expense-agent
docker run -d -p 8507:8505 --name agent-3 expense-agent
```

### Performance Optimization

#### **Caching Strategy**
```python
# Add Redis caching
import redis

cache = redis.Redis(host='localhost', port=6379)

@cache.memoize(expire=3600)
def expensive_llm_call(prompt):
    return llm.invoke(prompt)
```

#### **Async Processing**
```python
# Process receipts asynchronously
import asyncio

async def process_receipt_async(receipt_data):
    # OCR processing
    text = await asyncio.to_thread(extract_text, receipt_data)

    # LLM analysis
    result = await asyncio.to_thread(analyze_text, text)

    return result
```

---

## 🔧 Maintenance Tasks

### Regular Maintenance

#### **Weekly Tasks**
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Clear old logs
find logs/ -name "*.log" -mtime +30 -delete

# Update Tesseract
# Check for updates and install if available

# Database maintenance
# VACUUM ANALYZE if using PostgreSQL
```

#### **Monthly Tasks**
```bash
# Security updates
pip install --upgrade pip
pip install --upgrade setuptools wheel

# Performance review
# Analyze logs for bottlenecks
# Review error rates and response times

# Backup verification
# Test backup restoration procedure
```

### Monitoring Alerts

#### **Critical Alerts**
- Application down
- High error rate (>5%)
- Memory usage >90%
- Disk space <10% free

#### **Warning Alerts**
- Response time >30s
- OCR accuracy <80%
- API rate limit approaching

---

<div align="center">

**🚀 Deploy with confidence using this comprehensive guide**

[⬆️ Back to Top](#-deployment-guide) • [📚 API Docs](api.md) • [🔧 Troubleshooting](troubleshooting.md) • [🏠 Home](../README.md)

</div>