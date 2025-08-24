# K8s Microservices Starter (FastAPI + Postgres, Node.js + MongoDB)

This starter bundles two microservices and their databases with Dockerfiles, Docker Compose, and Kubernetes YAMLs.

## Quick start (Docker Compose)
```bash
docker compose up --build -d
```

- FastAPI service: http://localhost:8000  
- Node service: http://localhost:3000  

## CRUD Endpoints

### FastAPI (PostgreSQL)
- `GET /items`
- `GET /items/{id}`
- `POST /items`
- `PUT /items/{id}`
- `DELETE /items/{id}`

### Node (MongoDB)
- `GET /items`
- `GET /items/:id`
- `POST /items`
- `PUT /items/:id`
- `DELETE /items/:id`


## Kubernetes (minikube example)

1) Build images where your cluster can pull them. For minikube:
```bash
eval $(minikube -p minikube docker-env)
docker build -t fastapi-svc:latest ./fastapi-service
docker build -t node-svc:latest ./node-service
```

2) Apply everything:
```bash
kubectl apply -k k8s/
```

3) Add host entry for the ingress (minikube IP):
```bash
minikube ip
# Add to /etc/hosts or Windows hosts:
# <MINIKUBE_IP> micro.local
```

4) Test:
```bash
curl http://micro.local/api/py/health
curl http://micro.local/api/node/health
```
