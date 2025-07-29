#!/bin/bash

set -e

echo "🚀 Deploying Stock News System with Pre-built Frontend..."

# --- Colors and Helper Functions ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[INFO]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Prerequisite Checks ---
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"; exit 1;
fi
if ! command -v docker &> /dev/null; then
    print_error "docker is not installed or not in PATH"; exit 1;
fi
if ! command -v sudo &> /dev/null; then
    print_error "sudo is required for NFS setup. Please run with a user that has sudo privileges."; exit 1;
fi

# --- Namespace ---
print_status "Creating namespace 'stock-news'..."
kubectl create namespace stock-news

# --- Docker Image Build & Push ---
print_status "Building and pushing Docker images to Docker Hub..."
docker build -t company-service:latest ./company_service/
docker tag company-service:latest tieudaochannhan/company-service:latest
docker push tieudaochannhan/company-service:latest

docker build -t news-service:latest ./news_service/
docker tag news-service:latest tieudaochannhan/news-service:latest
docker push tieudaochannhan/news-service:latest

docker build -t notification-service:latest ./notification_service/
docker tag notification-service:latest tieudaochannhan/notification-service:latest
docker push tieudaochannhan/notification-service:latest

docker build -t frontend:latest ./frontend/
docker tag frontend:latest tieudaochannhan/frontend:latest
docker push tieudaochannhan/frontend:latest

# --- Kubernetes Infrastructure Setup ---
print_status "Setting up RBAC for monitoring..."
kubectl apply -f k8s/monitoring/rbac.yaml

print_status "Applying secrets..."
kubectl apply -f k8s/secrets.yaml

# --- NFS Storage Setup ---
print_status "🚀 Deploying with NFS Storage..."

# ✅ FIX 1: Install and configure the HOST's NFS server properly
print_status "📁 Setting up NFS server on the host..."
sudo apt-get update > /dev/null 2>&1
sudo apt-get install -y nfs-kernel-server > /dev/null 2>&1
sudo mkdir -p /srv/nfs/k8s-storage
sudo chown nobody:nogroup /srv/nfs/k8s-storage
sudo chmod 777 /srv/nfs/k8s-storage
echo "/srv/nfs/k8s-storage *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee /etc/exports
sudo systemctl restart nfs-kernel-server
sudo exportfs -a
print_status "✅ Host NFS server is running."

# ✅ FIX 2: Install ONLY the NFS CSI Driver, not the example server
print_status "📁 Installing NFS CSI Driver..."
curl -skSL https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/v4.11.0/deploy/install-driver.sh | bash -s v4.11.0 --
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/deploy/example/nfs-provisioner/nfs-server.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/deploy/example/storageclass-nfs.yaml
print_status "Waiting for NFS CSI driver to be ready..."
kubectl wait --for=condition=ready pod -l app=csi-nfs-controller -n kube-system --timeout=300s
print_status "✅ NFS CSI Driver is ready."

print_status "💾 Creating NFS StorageClass..."
kubectl apply -f k8s/nfs-storage-class.yaml

# --- Application Services Deployment ---
print_status "Deploying PostgreSQL..."
kubectl apply -f k8s/postgresql-deployment.yaml
print_status "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgresql -n stock-news --timeout=300s

print_status "Deploying RabbitMQ..."
kubectl apply -f k8s/rabbitmq-deployment.yaml
print_status "Waiting for RabbitMQ to be ready..."
kubectl wait --for=condition=ready pod -l app=rabbitmq -n stock-news --timeout=300s

print_status "Deploying Monitoring Stack..."
kubectl apply -f k8s/monitoring/prometheus-config.yaml
kubectl apply -f k8s/monitoring/prometheus-deployment.yaml
kubectl apply -f k8s/monitoring/grafana-config.yaml
kubectl apply -f k8s/monitoring/grafana-deployment.yaml

print_status "Deploying Backend Microservices..."
kubectl apply -f k8s/company-service-deployment.yaml
kubectl apply -f k8s/news-service-deployment.yaml
kubectl apply -f k8s/notification-service-deployment.yaml

print_status "Deploying Frontend..."
kubectl apply -f k8s/frontend-deployment.yaml

print_status "Deploying Service Discovery..."
kubectl apply -f k8s/company-service-service.yaml
kubectl apply -f k8s/news-service-service.yaml
kubectl apply -f k8s/notification-service-service.yaml

print_status "Deploying Airflow..."
kubectl apply -f k8s/airflow-configmap.yaml
kubectl apply -f k8s/airflow-deployment.yaml
kubectl apply -f k8s/airflow-service.yaml

# --- Ingress Setup ---
print_status "Deploying Ingress Controller and Rules..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.0/deploy/static/provider/cloud/deploy.yaml
# ✅ FIX 3: Use a proper wait command
print_status "Waiting for Ingress Controller to be ready..."
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=300s
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/airflow-ingress.yaml
kubectl apply -f k8s/monitoring-ingress.yaml

# --- Final Health Checks ---
print_status "Waiting for all services to be ready..."
kubectl wait --for=condition=ready pod -l app=company-service -n stock-news --timeout=300s
kubectl wait --for=condition=ready pod -l app=news-service -n stock-news --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service -n stock-news --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n stock-news --timeout=300s
kubectl wait --for=condition=ready pod -l app=prometheus -n stock-news --timeout=300s
kubectl wait --for=condition=ready pod -l app=grafana -n stock-news --timeout=300s

print_status "Setting up local DNS via /etc/hosts..."
if ! grep -q "stock-news.local" /etc/hosts; then
    echo "127.0.0.1 stock-news.local" | sudo tee -a /etc/hosts
fi

# --- Final Output ---
echo ""
print_status "✅ Deployment completed successfully!"
echo ""
# ✅ FIX 4: Add the correct port to the access URLs
echo "🌐 Access URLs:"
echo "   Frontend (Flutter Web):  http://stock-news.local:8082"
echo "   API Documentation:       http://stock-news.local:8082/api/v1/docs"
echo "   Prometheus:              http://stock-news.local:8082/prometheus"
echo "   Grafana:                 http://stock-news.local:8082/grafana (admin/admin123)"
echo "   RabbitMQ Management:     http://stock-news.local:8082/rabbitmq (guest/guest)"
echo ""
echo "📱 Frontend Features:"
echo "   - Real-time stock news dashboard"
echo "   - Company financial metrics"
echo "   - AI-powered news analysis"
echo "   - Watchlist management"
echo "   - Dark/Light theme support"
echo ""
echo "🔍 Useful commands:"
echo "   kubectl get pods -n stock-news"
echo "   kubectl logs -f deployment/frontend -n stock-news"
echo "   kubectl port-forward svc/frontend 3000:80 -n stock-news"
