# Kubernetes Deployment Guide

Complete guide for deploying REE AI platform to Kubernetes.

## Directory Structure

```
k8s/
├── base/                 # Base configurations (common)
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── postgres.yaml
│   ├── api-gateway.yaml
│   └── kustomization.yaml
├── overlays/
│   ├── dev/             # Development environment
│   └── prod/            # Production environment
└── README.md
```

## Prerequisites

1. **Kubernetes Cluster** (v1.24+)
   - Local: Minikube, Kind, Docker Desktop
   - Cloud: GKE, EKS, AKS

2. **kubectl** installed and configured

3. **kustomize** (optional, kubectl has built-in support)

4. **Docker images** pushed to registry

## Quick Start

### 1. Update Secrets

```bash
# Edit secrets in k8s/base/secret.yaml
kubectl create secret generic ree-ai-secrets \
  --from-literal=OPENAI_API_KEY=sk-your-key \
  --from-literal=POSTGRES_PASSWORD=your-password \
  --from-literal=JWT_SECRET_KEY=your-jwt-secret \
  -n ree-ai --dry-run=client -o yaml > k8s/base/secret.yaml
```

### 2. Build and Push Docker Images

```bash
# Build all services
docker-compose build

# Tag and push
export REGISTRY=your-docker-registry
for service in core-gateway db-gateway orchestrator api-gateway auth-service; do
  docker tag ree-ai-$service:latest $REGISTRY/ree-ai-$service:latest
  docker push $REGISTRY/ree-ai-$service:latest
done
```

### 3. Deploy to Kubernetes

```bash
# Apply base configuration
kubectl apply -k k8s/base/

# Or deploy to specific environment
kubectl apply -k k8s/overlays/dev/
kubectl apply -k k8s/overlays/prod/
```

### 4. Verify Deployment

```bash
# Check all resources
kubectl get all -n ree-ai

# Check pod status
kubectl get pods -n ree-ai

# View logs
kubectl logs -f deployment/api-gateway -n ree-ai
```

## Service Architecture

```
┌─────────────────────────────────────────────┐
│  Ingress / LoadBalancer                     │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  API Gateway (8888)                         │
│  - Rate limiting                            │
│  - Authentication                           │
│  - Request routing                          │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  Auth Service (8085)                        │
│  - User authentication                      │
│  - JWT token generation                     │
└─────────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  Business Services                          │
│  - Orchestrator (8090)                      │
│  - RAG Service (8091)                       │
│  - Classification (8083)                    │
│  - Semantic Chunking (8082)                 │
└──────────────────┬──────────────────────────┘
                   ↓
┌─────────────────────────────────────────────┐
│  Infrastructure Services                    │
│  - PostgreSQL (5432)                        │
│  - Redis (6379)                             │
│  - OpenSearch (9200)                        │
└─────────────────────────────────────────────┘
```

## Scaling

### Manual Scaling

```bash
# Scale API Gateway
kubectl scale deployment api-gateway --replicas=5 -n ree-ai

# Scale Orchestrator
kubectl scale deployment orchestrator --replicas=3 -n ree-ai
```

### Auto Scaling (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Monitoring

### Prometheus & Grafana

```bash
# Deploy monitoring stack
kubectl apply -f k8s/monitoring/

# Access Grafana
kubectl port-forward svc/grafana 3001:3000 -n ree-ai

# Open http://localhost:3001
# Username: admin
# Password: admin
```

### View Metrics

```bash
# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n ree-ai

# Open http://localhost:9090
```

## Troubleshooting

### Pod not starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n ree-ai

# View logs
kubectl logs <pod-name> -n ree-ai

# Get events
kubectl get events -n ree-ai --sort-by='.lastTimestamp'
```

### Database connection issues

```bash
# Check PostgreSQL pod
kubectl logs deployment/postgres -n ree-ai

# Test connection
kubectl run -it --rm debug --image=postgres:15 --restart=Never -n ree-ai -- \
  psql -h postgres -U ree_ai_user -d ree_ai
```

### Service discovery issues

```bash
# Check services
kubectl get svc -n ree-ai

# Check endpoints
kubectl get endpoints -n ree-ai

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -n ree-ai -- \
  nslookup postgres
```

## Production Checklist

- [ ] Update all secrets in `k8s/base/secret.yaml`
- [ ] Configure resource limits for all services
- [ ] Set up persistent volumes for databases
- [ ] Configure horizontal pod autoscaling
- [ ] Set up ingress with TLS
- [ ] Configure network policies
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure backup strategy for databases
- [ ] Set up logging (ELK/Loki)
- [ ] Configure CI/CD pipeline
- [ ] Set up health checks and readiness probes
- [ ] Review security policies

## Environment-Specific Configurations

### Development

```bash
kubectl apply -k k8s/overlays/dev/
```

- Single replicas
- Debug mode enabled
- Lower resource limits

### Production

```bash
kubectl apply -k k8s/overlays/prod/
```

- Multiple replicas
- Production mode
- Higher resource limits
- Auto-scaling enabled

## Useful Commands

```bash
# Get all resources
kubectl get all -n ree-ai

# Watch pod status
kubectl get pods -n ree-ai -w

# Port forward to service
kubectl port-forward svc/api-gateway 8888:8080 -n ree-ai

# Execute command in pod
kubectl exec -it <pod-name> -n ree-ai -- /bin/bash

# View resource usage
kubectl top pods -n ree-ai
kubectl top nodes

# Delete all resources
kubectl delete -k k8s/base/
```

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
