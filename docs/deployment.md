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

### ☁️ Cloud Deployment

#### **AWS EC2 Deployment**

1. **Launch EC2 instance**
   ```bash
   # Ubuntu 20.04 LTS, t3.medium or higher
   aws ec2 run-instances \
     --image-id ami-0c55b159cbfafe1d0 \
     --instance-type t3.medium \
     --key-name your-key-pair
   ```

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