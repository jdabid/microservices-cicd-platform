# Local Deployment with kind (Kubernetes in Docker)

This guide demonstrates deploying the microservices platform to a local Kubernetes
cluster using kind, kubectl, and Helm.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or OrbStack
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) (v0.20+)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (v1.28+)
- [Helm](https://helm.sh/docs/intro/install/) (v3.12+)

## Step 1: Create the kind Cluster

```bash
kind create cluster --name microservices-demo --wait 120s
```

Verify:
```bash
kubectl cluster-info --context kind-microservices-demo
kubectl get nodes --context kind-microservices-demo
```

## Step 2: Build and Load Docker Images

Build the three application images:
```bash
docker build -t microservices-backend:local -f backend-api/Dockerfile backend-api/
docker build -t microservices-worker:local -f backend-api/Dockerfile.worker backend-api/
docker build -t microservices-frontend:local -f frontend/Dockerfile frontend/
```

Load them into the kind cluster:
```bash
kind load docker-image microservices-backend:local microservices-worker:local microservices-frontend:local --name microservices-demo
```

## Step 3: Create Namespace and Secrets

Create the namespace with Helm-compatible labels:
```bash
kubectl create namespace microservices-cicd-platform --context kind-microservices-demo

kubectl label namespace microservices-cicd-platform app.kubernetes.io/managed-by=Helm --context kind-microservices-demo

kubectl annotate namespace microservices-cicd-platform \
  meta.helm.sh/release-name=demo \
  meta.helm.sh/release-namespace=microservices-cicd-platform \
  --context kind-microservices-demo
```

Create the required secrets:
```bash
kubectl create secret generic postgres-secrets \
  --namespace microservices-cicd-platform \
  --context kind-microservices-demo \
  --from-literal=postgres-db=appointments \
  --from-literal=postgres-user=admin \
  --from-literal=postgres-password=your-password-here

kubectl create secret generic backend-secrets \
  --namespace microservices-cicd-platform \
  --context kind-microservices-demo \
  --from-literal=database-url='postgresql+asyncpg://admin:your-password-here@demo-microservices-platform-postgres:5432/appointments' \
  --from-literal=redis-url='redis://demo-microservices-platform-redis:6379/0' \
  --from-literal=secret-key='your-secret-key-here'
```

## Step 4: Deploy with Helm

```bash
helm upgrade --install demo helm/microservices-platform/ \
  --namespace microservices-cicd-platform \
  --kube-context kind-microservices-demo \
  --set backendApi.image.repository=microservices-backend \
  --set backendApi.image.tag=local \
  --set backendApi.image.pullPolicy=Never \
  --set backendApi.autoscaling.enabled=false \
  --set backendApi.replicaCount=1 \
  --set backendWorker.image.repository=microservices-worker \
  --set backendWorker.image.tag=local \
  --set backendWorker.image.pullPolicy=Never \
  --set frontend.image.repository=microservices-frontend \
  --set frontend.image.tag=local \
  --set frontend.image.pullPolicy=Never \
  --set ingress.enabled=false \
  --set networkPolicy.enabled=false \
  --timeout 3m
```

Verify the deployment:
```bash
kubectl get all -n microservices-cicd-platform --context kind-microservices-demo
helm list -n microservices-cicd-platform --kube-context kind-microservices-demo
```

## Step 5: Access the Application

Use port-forwarding to access services locally:

**Backend API:**
```bash
kubectl port-forward svc/demo-microservices-platform-backend-api 8000:8000 \
  -n microservices-cicd-platform --context kind-microservices-demo
# Visit: http://localhost:8000/docs (Swagger UI)
# Health: http://localhost:8000/health
```

**Frontend:**
```bash
kubectl port-forward svc/demo-microservices-platform-frontend 8080:80 \
  -n microservices-cicd-platform --context kind-microservices-demo
# Visit: http://localhost:8080
```

## Teardown

Remove the Helm release and delete the cluster:
```bash
helm uninstall demo -n microservices-cicd-platform --kube-context kind-microservices-demo
kind delete cluster --name microservices-demo
```

## Deployed Resources

The Helm chart deploys the following Kubernetes resources:

| Component      | Type       | Port |
|----------------|------------|------|
| Backend API    | Deployment | 8000 |
| Backend Worker | Deployment | -    |
| Frontend       | Deployment | 80   |
| PostgreSQL     | Deployment | 5432 |
| Redis          | Deployment | 6379 |

Each deployment has a corresponding ClusterIP service, plus:
- PersistentVolumeClaim for PostgreSQL data
- Secrets for database credentials and backend config
- Resource requests/limits on all containers
- Liveness and readiness probes
- SecurityContext (runAsNonRoot)

## Evidence Files

The `docs/deployment-demo/` directory contains captured outputs from a real deployment:

- `cluster-info.txt` - Kubernetes cluster information
- `clusters.txt` - kind clusters list
- `pods-status.txt` - Pod status with node placement
- `services.txt` - ClusterIP services
- `all-resources.txt` - All deployed K8s resources
- `helm-release.txt` - Helm release information
- `pods-describe.txt` - Detailed pod descriptions
- `events.txt` - Cluster events timeline
- `health-check.txt` - Backend health check result

## Known Issues in Local Deployment

1. **Frontend CrashLoopBackOff**: The nginx config references `backend-api` as upstream,
   but the actual K8s service name is `demo-microservices-platform-backend-api`. This
   can be fixed by updating the nginx configuration to use the full service name or
   environment variables.

2. **Backend restarts**: The backend API may restart several times while waiting for
   PostgreSQL to be ready. The readiness/liveness probes eventually stabilize once
   the database connection is established.
