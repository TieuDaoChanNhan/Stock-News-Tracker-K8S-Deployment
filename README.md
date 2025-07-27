# 📈 Stock News Tracking System

<div align="center">

**Smart stock news tracking system with AI-powered analysis and real-time notifications**

[🚀 Demo](#demo) - [📖 Documentation](#documentation) - [🛠️ Installation](#installation) - [🤝 Contributing](#contributing)

</div>

## 📋 Table of Contents

1. [Overview](#-general-information)
2. [System Architecture](#-system-architecture-architecture)
3. [Key Features](#-technical-prerequisites)
4. [Tech Stack](#-tech-stack)
5. [Prerequisites](#-prerequisites)
6. [Install and Deploy](#-c%C3%A0i-%C4%91%E1%BA%B7t-v%C3%A0-deploy)
7. [API Documentation](#-api-documentation)
8. [Monitoring](#-monitoring)
9. [Troubleshooting](#-troubleshooting)
10. [Contributing](#-contributing)
11. [License](#-license)

## 🎯 Overview

**Stock News Tracking System** is a comprehensive microservices system designed to:

- 📰 **Crawl and analyze news** from multiple sources (VnExpress, etc.)
- 🤖 **AI-powered analysis** using Google Gemini to analyze news impact
- 📊 **Track financial metrics** real-time from Financial Modeling Prep API
- 🔔 **Smart notifications** via Telegram for important keywords
- 📈 **Visual dashboard** with Flutter web interface
- ⚡ **Automated scheduling** with Apache Airflow

The system is built with **cloud-native architecture**, deployed on **Kubernetes** with full monitoring and observability.

## 🏗️ System architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        KUBERNETES CLUSTER                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌──────────────────────────────────────┐│
│  │  NGINX INGRESS  │    │              FRONTEND                ││
│  │   Controller    │ -> │          (Flutter Web)               ││
│  │   Port: 8082    │    │            Port: 80                  ││
│  └─────────────────┘    └──────────────────────────────────────┘│
│           │                                                     │
│  ┌────────▼───────────────────────────────────────────────────┐ │
│  │                 MICROSERVICES LAYER                        │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │ │
│  │  │  COMPANY    │ │    NEWS     │ │    NOTIFICATION     │   │ │
│  │  │   SERVICE   │ │   SERVICE   │ │      SERVICE        │   │ │
│  │  │ Port: 8000  │ │ Port: 8000  │ │     Port: 8000      │   │ │
│  │  │             │ │             │ │                     │   │ │
│  │  │ • Financial │ │ • News      │ │ • User watchlist    │   │ │
│  │  │   Metrics   │ │   Crawling  │ │ • Telegram          │   │ │
│  │  │ • FMP API   │ │ • AI        │ │   Notifications     │   │ │
│  │  │   Integratio│ │   Analysis  │ │ • Keywords          │   │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘   │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                    │                    │           │
│  ┌────────▼────────────────────▼────────────────────▼─────────┐ │
│  │                   DATA LAYER                               │ │
│  │  ┌─────────────┐              ┌─────────────────────────┐  │ │
│  │  │ POSTGRESQL  │              │       RABBITMQ          │  │ │
│  │  │ Multi-DB:   │              │    Message Queue        │  │ │
│  │  │ • company_db│              │     Port: 5672          │  │ │
│  │  │ • news_db   │              │   Management: 15672     │  │ │
│  │  │ • user_db   │              └─────────────────────────┘  │ │
│  │  │ • airflow_db│                                           │ │
│  │  │Port: 5432   │                                           │ │
│  │  └─────────────┘                                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│           │                                                     │
│  ┌────────▼────────────────────────────────────────────────────┐│
│  │                 AUTOMATION LAYER                            ││
│  │  ┌─────────────┐              ┌─────────────────────────┐   ││
│  │  │   AIRFLOW   │              │      MONITORING         │   ││
│  │  │  Scheduler  │              │  ┌─────────┐ ┌────────┐ │   ││
│  │  │Port: 8080   │              │  │PROMETHEUS│ │GRAFANA ││   ││
│  │  │             │              │  │Port:9090 │ │Port:3K ││   ││
│  │  │ • Auto      │              │  └─────────┘ └────────┘ │   ││
│  │  │   Crawling  │              │                         │   ││
│  │  │ • Metrics   │              │ • Resource monitoring   │   ││
│  │  │   Fetching  │              │ • Custom dashboards     │   ││
│  │  │ • Every 4h  │              │ • Alerting              │   ││
│  │  └─────────────┘              └─────────────────────────┘   ││
│  └──────────────────────────────────────────────────────────── ┘│
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    STORAGE LAYER                           │ │
│  │                 NFS Persistent Storage                     │ │
│  │               (/srv/nfs/k8s-storage)                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

External APIs:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Financial       │    │ Google Gemini   │    │ Telegram Bot    │
│ Modeling Prep   │    │ AI API          │    │ API             │
│ (FMP) API       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```


### 🔄 Data Flow

1. **Airflow Scheduler** triggers tasks every 4 hours
2. **Company Service** fetches financial metrics from FMP API
3. **News Service** crawls news from configured sources
4. **AI Analysis** processes news articles via Gemini API
5. **Notification Service** sends alerts via Telegram
6. **Frontend** displays real-time dashboard
7. **Monitoring** tracks all system metrics

## ✨ Main features

### 📊 Financial Data Management

- **Real-time metrics**: PE ratio, P/B ratio, Market Cap, EPS, ROE, ROA
- **Multiple data sources**: Financial Modeling Prep API integration
- **Historical tracking**: Complete metrics history and trends
- **Portfolio management**: Add/remove companies from watchlist


### 📰 Intelligent News Processing

- **Multi-source crawling**: VnExpress, Cafef, and custom sources
- **AI-powered analysis**: Google Gemini AI analyzes sentiment and impact
- **Automated categorization**: Technology, Financial, Healthcare sectors
- **Content filtering**: Eliminate spam and duplicate content


### 🔔 Smart Notifications

- **Keyword-based alerts**: Custom watchlist for important keywords
- **Telegram integration**: Instant notifications via Telegram bot
- **Impact scoring**: AI-generated impact scores for news events
- **User preferences**: Personalized notification settings


### 📈 Real-time Dashboard

- **Flutter web interface**: Modern, responsive design
- **Dark/Light themes**: User preference support
- **Interactive charts**: Financial metrics visualization
- **Live updates**: Real-time data refresh
- **Mobile-responsive**: Works on all devices


### ⚡ Automation \& Scheduling

- **Apache Airflow**: Robust workflow management
- **Automated crawling**: Every 4 hours news updates
- **Parallel processing**: Concurrent task execution
- **Error handling**: Comprehensive retry logic
- **Manual triggers**: On-demand scheduler execution


### 🔍 Monitoring \& Observability

- **Prometheus metrics**: System performance tracking
- **Grafana dashboards**: Visual monitoring interface
- **Health checks**: Service availability monitoring
- **Log aggregation**: Centralized logging
- **Alerting**: Proactive issue detection


## 🛠️ Tech Stack

### **Backend Services**

- **FastAPI** - Modern, high-performance web framework
- **SQLAlchemy** - Python ORM với PostgreSQL
- **Pydantic** - Data validation and serialization
- **aio-pika** - Async RabbitMQ client


### **Frontend**

- **Flutter Web** - Cross-platform UI toolkit
- **Dart** - Client-optimized programming language
- **HTTP Client** - RESTful API communication


### **Infrastructure**

- **Kubernetes** - Container orchestration platform
- **Docker** - Containerization platform
- **NGINX Ingress** - Load balancing and routing
- **NFS Storage** - Persistent volume storage


### **Databases \& Message Queue**

- **PostgreSQL** - Relational database (multi-schema)
- **RabbitMQ** - Message broker cho async processing


### **Monitoring \& Automation**

- **Apache Airflow** - Workflow management
- **Prometheus** - Metrics collection and monitoring
- **Grafana** - Data visualization and dashboards


### **External APIs**

- **Financial Modeling Prep** - Financial data provider
- **Google Gemini AI** - Natural language processing
- **Telegram Bot API** - Notification delivery


## 📋 Prerequisites

### **System Requirements**

- **OS**: Ubuntu 20.04+ / macOS 10.15+ / Windows 10+ with WSL2
- **RAM**: Minimum 8GB (Recommended 16GB+)
- **CPU**: 4+ cores
- **Storage**: 50GB+ available space
- **Network**: Stable internet connection cho external APIs


### **Required Tools**

```bash
# Kubernetes cluster (local or cloud)
kubectl >= 1.31
minikube >= 1.30 (for local development)

# Container runtime
docker >= 20.10
docker-compose >= 2.0

# Package managers
npm >= 8.0 (for frontend dependencies)
pip >= 21.0 (for Python dependencies)

# Development tools
git >= 2.30
curl >= 7.70
```


### **External API Keys** (Required)

```bash
# Financial Modeling Prep API
FMP_API_KEY=your_fmp_api_key_here

# Google Gemini AI API  
GOOGLE_API_KEY=your_gemini_api_key_here

# Telegram Bot API
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```


### **Get API Keys**

1. **FMP API**: Register at [financialmodelingprep.com](https://financialmodelingprep.com)
2. **Google Gemini**: Get key from [Google AI Studio](https://aistudio.google.com)
3. **Telegram Bot**: Create bot via [@BotFather](https://t.me/botfather)

## 🚀 Install and Deploy

### **Option 1: Quick Deploy (Recommended)**

```bash
#1. Clone repository
git clone https://github.com/yourusername/stock-news-tracking-system.git
cd stock-news-tracking-system/microservices

#2. Configure API keys
cp k8s/secrets.yaml.example k8s/secrets.yaml
# Edit k8s/secrets.yaml with your API keys

# 3. Run automated deployment script
chmod +x k8s/deploy.sh
./k8s/deploy.sh

#4. Wait for deployment (5-10 minutes)
kubectl get pods -n stock-news -w

#5. Access applications
echo "127.0.0.1 stock-news.local" | sudo tee -a /etc/hosts
open http://localhost:8082 # or http://stock-news.local:8082
```


### **Option 2: Manual Step-by-step**

<details>
<summary>Click to expand manual installation</summary>

#### **Step 1: Setup Kubernetes Cluster**
```bash
# For local development with minikube
minikube start --memory=8192 --cpus=4
minikube addons enable ingress

# For production cluster, ensure kubectl context is set
kubectl config current-context
```

#### **Step 2: Create Namespace**
```bash
kubectl create namespace stock-news
kubectl config set-context --current --namespace=stock-news
```

#### **Step 3: Setup Storage**
```bash
# Install NFS server (Ubuntu)
sudo apt-get update
sudo apt-get install -y nfs-kernel-server
sudo mkdir -p /srv/nfs/k8s-storage
sudo chown nobody:nogroup /srv/nfs/k8s-storage
sudo chmod 777 /srv/nfs/k8s-storage

# Configure NFS exports
echo "/srv/nfs/k8s-storage *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee /etc/exports
sudo systemctl restart nfs-kernel-server

# Install NFS CSI driver
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/v4.6.0/deploy/rbac-csi-nfs-controller.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/v4.6.0/deploy/csi-nfs-driverinfo.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/v4.6.0/deploy/csi-nfs-controller.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/v4.6.0/deploy/csi-nfs-node.yaml

# Apply storage class
kubectl apply -f k8s/nfs-storage-class.yaml
```

#### **Step 4: Configure Secrets**
```bash
# Create secrets file
cp k8s/secrets.yaml.example k8s/secrets.yaml

# Edit with actual API keys (base64 encoded)
echo -n "your_fmp_api_key" | base64
echo -n "your_gemini_api_key" | base64
echo -n "your_telegram_token" | base64

# Apply secrets
kubectl apply -f k8s/secrets.yaml
```

#### **Step 5: Deploy Infrastructure**
```bash
# PostgreSQL database
kubectl apply -f k8s/postgresql-deployment.yaml

# RabbitMQ message queue  
kubectl apply -f k8s/rabbitmq-deployment.yaml

# Wait for databases
kubectl wait --for=condition=ready pod -l app=postgresql --timeout=300s
kubectl wait --for=condition=ready pod -l app=rabbitmq --timeout=300s
```

#### **Step 6: Build và Push Images**
```bash
# Build all service images
docker build -t your-registry/company-service:latest ./company_service/
docker build -t your-registry/news-service:latest ./news_service/
docker build -t your-registry/notification-service:latest ./notification_service/
docker build -t your-registry/frontend:latest ./frontend/

# Push to registry
docker push your-registry/company-service:latest
docker push your-registry/news-service:latest  
docker push your-registry/notification-service:latest
docker push your-registry/frontend:latest

# Update image references in deployment files
sed -i 's/tieudaochannhan/your-registry/g' k8s/*-deployment.yaml
```

#### **Step 7: Deploy Application Services**
```bash
# Backend microservices
kubectl apply -f k8s/company-service-deployment.yaml
kubectl apply -f k8s/news-service-deployment.yaml
kubectl apply -f k8s/notification-service-deployment.yaml

# Frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Wait for services
kubectl wait --for=condition=ready pod -l app=company-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=news-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
```

#### **Step 8: Setup Monitoring**
```bash
# Prometheus
kubectl apply -f k8s/monitoring/prometheus-config.yaml
kubectl apply -f k8s/monitoring/prometheus-deployment.yaml

# Grafana
kubectl apply -f k8s/monitoring/grafana-config.yaml
kubectl apply -f k8s/monitoring/grafana-deployment.yaml

# Wait for monitoring
kubectl wait --for=condition=ready pod -l app=prometheus --timeout=300s
kubectl wait --for=condition=ready pod -l app=grafana --timeout=300s
```

#### **Step 9: Deploy Airflow Scheduler**
```bash
# Airflow configuration
kubectl apply -f k8s/airflow-configmap.yaml

# Airflow services
kubectl apply -f k8s/airflow-deployment.yaml
kubectl apply -f k8s/airflow-service.yaml

# Wait for Airflow
kubectl wait --for=condition=ready pod -l app=airflow-scheduler --timeout=300s
kubectl wait --for=condition=ready pod -l app=airflow-webserver --timeout=300s
```

#### **Step 10: Setup Networking**
```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=300s

# Apply ingress rules
kubectl apply -f k8s/ingress.yaml

# Setup NodePort access
kubectl apply -f k8s/nginx-ingress-nodeport.yaml
```

#### **Step 11: Configure DNS**
```bash
# Add local DNS entry
echo "127.0.0.1 stock-news.local" | sudo tee -a /etc/hosts

# For cloud deployment, update DNS records to point to LoadBalancer IP
kubectl get svc -n ingress-nginx
```

</details>

### **Verification**

```bash
# Check all pods are running
kubectl get pods -n stock-news

# Check services
kubectl get svc -n stock-news

# Test API endpoints
curl http://localhost:8082/api/v1/companies
curl http://localhost:8082/api/v1/articles/count

# Access web interfaces
open http://localhost:8082           # Frontend Dashboard
open http://localhost:8082/airflow   # Airflow UI (admin/admin)
open http://localhost:8082/grafana   # Grafana (admin/admin123)
```


## 📚 API Documentation

### **Company Service** (`/api/v1/companies`)

<details>
<summary>Company Management APIs</summary>

#### **GET /api/v1/companies**
List all tracked companies
```bash
curl http://localhost:8082/api/v1/companies
```

#### **POST /api/v1/companies**  
Add new company to tracking
```bash
curl -X POST http://localhost:8082/api/v1/companies \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics"
  }'
```

#### **GET /api/v1/companies/{symbol}**
Get specific company details
```bash
curl http://localhost:8082/api/v1/companies/AAPL
```

#### **GET /api/v1/companies/{symbol}/metrics**
Get financial metrics history
```bash
curl http://localhost:8082/api/v1/companies/AAPL/metrics?limit=10
```

#### **POST /api/v1/companies/{symbol}/fetch-metrics**
Manually trigger metrics fetch
```bash
curl -X POST http://localhost:8082/api/v1/companies/AAPL/fetch-metrics
```

</details>

### **News Service** (`/api/v1/articles`, `/api/v1/crawl-sources`)

<details>
<summary>News Management APIs</summary>

#### **GET /api/v1/articles**
List all news articles
```bash
curl http://localhost:8082/api/v1/articles?limit=20&skip=0
```

#### **GET /api/v1/articles/count**
Get total articles count
```bash
curl http://localhost:8082/api/v1/articles/count
```

#### **GET /api/v1/articles/{article_id}**
Get specific article with AI analysis
```bash
curl http://localhost:8082/api/v1/articles/1
```

#### **GET /api/v1/crawl-sources**
List all crawl sources
```bash
curl http://localhost:8082/api/v1/crawl-sources
```

#### **POST /api/v1/crawl-sources**
Add new crawl source
```bash
curl -X POST http://localhost:8082/api/v1/crawl-sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "VnExpress Technology",
    "url": "https://vnexpress.net/so-hoa",
    "article_container_selector": ".item-news",
    "title_selector": "h3 a",
    "link_selector": "h3 a",
    "summary_selector": ".description",
    "date_selector": ".time",
    "is_active": true
  }'
```

#### **GET /api/v1/ai-analysis/high-impact**
Get high-impact news articles
```bash
curl http://localhost:8082/api/v1/ai-analysis/high-impact
```

</details>

### **Notification Service** (`/api/v1/users`)

<details>
<summary>User & Notification APIs</summary>

#### **GET /api/v1/users/{user_id}/watchlist**
Get user's watchlist
```bash
curl http://localhost:8082/api/v1/users/user123/watchlist
```

#### **POST /api/v1/users/{user_id}/watchlist**
Add keyword to watchlist
```bash
curl -X POST http://localhost:8082/api/v1/users/user123/watchlist \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "Apple earnings",
    "notification_type": "telegram",
    "is_active": true
  }'
```

#### **DELETE /api/v1/users/{user_id}/watchlist/{item_id}**
Remove item from watchlist
```bash
curl -X DELETE http://localhost:8082/api/v1/users/user123/watchlist/1
```

</details>

### **Scheduler APIs**

<details>
<summary>Manual Scheduler Triggers</summary>

#### **POST /api/v1/companies-scheduler/run**
Trigger company metrics fetching
```bash
curl -X POST http://localhost:8082/api/v1/companies-scheduler/run
```

#### **POST /api/v1/news-scheduler/run**  
Trigger news crawling and AI analysis
```bash
curl -X POST http://localhost:8082/api/v1/news-scheduler/run
```

#### **GET /api/v1/companies-scheduler/status**
Get scheduler status
```bash
curl http://localhost:8082/api/v1/companies-scheduler/status
```

</details>

### **Interactive API Documentation**

Visit these URLs for interactive Swagger documentation:

- **Company Service**: `http://localhost:8082/api/v1/docs` (port-forward to 8001)
- **News Service**: `http://localhost:8082/api/v1/docs` (port-forward to 8002)
- **Notification Service**: `http://localhost:8082/api/v1/docs` (port-forward to 8003)


## 📊 Monitoring

### **Prometheus Metrics**

Access Prometheus at `http://localhost:8082/prometheus`

**Key Metrics to Monitor:**

```promql
# System resources
container_memory_usage_bytes
container_cpu_usage_seconds_total
kube_pod_status_ready

# Application metrics  
http_requests_total
http_request_duration_seconds
database_connections_active
api_requests_per_minute

# Custom business metrics
news_articles_crawled_total
companies_metrics_fetched_total
telegram_notifications_sent_total
ai_analysis_processing_time
```


### **Grafana Dashboards**

Access Grafana at `http://localhost:8082/grafana` (admin/admin123)

**Pre-configured Dashboards:**

1. **System Overview**: CPU, Memory, Network usage across pods
2. **Application Performance**: Request rates, response times, errors
3. **Business Metrics**: Articles crawled, companies tracked, notifications sent
4. **Database Monitoring**: Connection pools, query performance
5. **External APIs**: FMP API usage, Gemini AI requests, Telegram status

### **Health Checks**

```bash
# Check all services health
curl http://localhost:8082/health  # Overall system
curl http://localhost:8082/api/v1/companies/health  # Company Service
curl http://localhost:8082/api/v1/articles/health   # News Service

# Check individual pods
kubectl get pods -n stock-news
kubectl describe pod <pod-name> -n stock-news

# Check logs
kubectl logs -f deployment/company-service -n stock-news
kubectl logs -f deployment/news-service -n stock-news
kubectl logs -f deployment/airflow-scheduler -n stock-news
```


### **Alerting Rules**

Prometheus alerting rules in `k8s/monitoring/alerts.yaml`:

- Pod restarts > 5 in 10 minutes
- API response time > 5 seconds
- Database connection failures
- External API rate limit proximity
- Disk usage > 85%


## 🔧 Troubleshooting

### **Common Issues**

<details>
<summary>Pods not starting</summary>

```bash
# Check pod status
kubectl get pods -n stock-news

# Describe problematic pod
kubectl describe pod <pod-name> -n stock-news

# Check logs
kubectl logs <pod-name> -n stock-news

# Common fixes:
# 1. Image pull errors - check image names/tags
# 2. Resource limits - check memory/CPU limits
# 3. ConfigMap/Secret issues - verify base64 encoding
# 4. PVC mounting issues - check NFS server status
```

</details>
<details>
<summary>Database connection issues</summary>

```bash
# Check PostgreSQL pod
kubectl get pods -l app=postgresql -n stock-news

# Check database logs  
kubectl logs -f deployment/postgresql -n stock-news

# Test database connection
kubectl exec -it deployment/postgresql -n stock-news -- psql -U stock_tracker_user -d company_db -c "SELECT 1;"

# Common fixes:
# 1. Wrong database URLs in secrets
# 2. Database not initialized - check init scripts
# 3. Network policies blocking connections
# 4. Password encoding issues
```

</details>
<details>
<summary>API endpoints returning 404</summary>

```bash
# Check ingress configuration
kubectl describe ingress stock-news-ingress -n stock-news

# Check service endpoints
kubectl get endpoints -n stock-news

# Test direct service access
kubectl port-forward svc/company-service-k8s 8001:8000 -n stock-news
curl http://localhost:8001/api/v1/companies

# Common fixes:
# 1. Ingress path mismatches
# 2. Service selector labels incorrect  
# 3. Pod not ready/healthy
# 4. Wrong port configurations
```

</details>
<details>
<summary>External API failures</summary>

```bash
# Check API key configuration
kubectl get secret api-secrets -n stock-news -o yaml

# Check service logs for API errors
kubectl logs -f deployment/company-service -n stock-news | grep -i "api\|error"

# Test API keys manually
curl "https://financialmodelingprep.com/api/v3/profile/AAPL?apikey=YOUR_KEY"

# Common fixes:
# 1. Invalid API keys
# 2. Rate limit exceeded
# 3. Network connectivity issues
# 4. API endpoint changes
```

</details>
<details>
<summary>Airflow DAG issues</summary>

```bash
# Check Airflow scheduler logs
kubectl logs -f deployment/airflow-scheduler -n stock-news

# Access Airflow UI
kubectl port-forward svc/airflow-webserver 8080:8080 -n stock-news
# Visit http://localhost:8080 (admin/admin)

# Check DAG parsing
kubectl exec -it deployment/airflow-scheduler -n stock-news -- airflow dags list

# Common fixes:
# 1. Python syntax errors in DAG files
# 2. Missing dependencies
# 3. DAG not enabled in UI
# 4. Scheduler not running
```

</details>

### **Debug Commands**

```bash
# Comprehensive system check
kubectl get all -n stock-news

# Check events for errors
kubectl get events -n stock-news --sort-by='.lastTimestamp'

# Resource usage
kubectl top pods -n stock-news
kubectl top nodes

# Network connectivity test
kubectl run test-pod --image=curlimages/curl -it --rm -n stock-news -- /bin/sh

# Port forward for direct access
kubectl port-forward svc/company-service-k8s 8001:8000 -n stock-news &
kubectl port-forward svc/news-service-k8s 8002:8000 -n stock-news &
kubectl port-forward svc/notification-service-k8s 8003:8000 -n stock-news &
```


### **Log Analysis**

```bash
# Follow multiple logs
kubectl logs -f deployment/company-service -n stock-news | tee company.log &
kubectl logs -f deployment/news-service -n stock-news | tee news.log &
kubectl logs -f deployment/airflow-scheduler -n stock-news | tee airflow.log &

# Search for specific errors
grep -i "error\|exception\|failed" *.log

# Monitor real-time performance
watch kubectl get pods -n stock-news
```


## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# 1. Fork và clone repository
git clone https://github.com/yourusername/stock-news-tracking-system.git
cd stock-news-tracking-system

# 2. Create development branch
git checkout -b feature/your-feature-name

# 3. Setup pre-commit hooks
pip install pre-commit
pre-commit install

# 4. Make changes và test locally
./scripts/run-tests.sh

# 5. Submit pull request
```


### Code Style

- **Python**: Follow PEP 8, use `black` formatter
- **Dart/Flutter**: Follow Dart style guide
- **YAML**: 2-space indentation
- **Commit messages**: Use conventional commits format

## 🙏 Acknowledgments

- **Financial Modeling Prep** for financial data API
- **Google Gemini AI** for news analysis capabilities
- **Kubernetes Community** for excellent documentation
- **Flutter Team** for cross-platform UI framework
- **FastAPI** for modern Python web framework
- **Apache Airflow** for workflow management
