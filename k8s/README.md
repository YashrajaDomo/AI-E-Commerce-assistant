# Kubernetes deployment starter

The manifests in [`base/`](./base/) describe the five application microservices, the frontend, one MySQL StatefulSet with four isolated databases/users, and one MongoDB StatefulSet. They include persistent-volume claims, dependency configuration, resource requests/limits, and health/readiness probes.

These are deployment templates, not a production-hardened cluster install. Configure the target cluster's StorageClass, ingress/TLS, registry, monitoring, backup/restore, network policies, and external secret manager before production use.

## 1. Build and publish application images

From the repository root, build each image with its service name:

```powershell
docker build -f services/Dockerfile --build-arg SERVICE_NAME=catalog -t <registry>/ai-shop-catalog:1.0.0 .
docker build -f services/Dockerfile --build-arg SERVICE_NAME=cart -t <registry>/ai-shop-cart:1.0.0 .
docker build -f services/Dockerfile --build-arg SERVICE_NAME=orders -t <registry>/ai-shop-orders:1.0.0 .
docker build -f services/Dockerfile --build-arg SERVICE_NAME=payments -t <registry>/ai-shop-payments:1.0.0 .
docker build -f services/Dockerfile --build-arg SERVICE_NAME=assistant -t <registry>/ai-shop-assistant:1.0.0 .
docker build -f frontend/Dockerfile -t <registry>/ai-shop-frontend:1.0.0 frontend
```

Push those images and update the six `image:` fields in [`base/applications.yaml`](./base/applications.yaml) to the published tags.

## 2. Create secrets

Create `ai-shop-secrets` in the same namespace before applying the manifests. Use unique strong values; the following is a template, not a command with usable credentials:

```powershell
kubectl create secret generic ai-shop-secrets `
  --from-literal=MYSQL_ROOT_PASSWORD='<strong-mysql-root-password>' `
  --from-literal=CATALOG_DB_PASSWORD='<catalog-password>' `
  --from-literal=CART_DB_PASSWORD='<cart-password>' `
  --from-literal=ORDERS_DB_PASSWORD='<orders-password>' `
  --from-literal=PAYMENTS_DB_PASSWORD='<payments-password>' `
  --from-literal=MONGO_ROOT_PASSWORD='<strong-mongodb-password>' `
  --from-literal=OPENAI_API_KEY='<optional-api-key>'
```

Use alphanumeric database passwords unless the URL-encoding behavior is extended before introducing reserved URI characters. Never commit a populated Secret manifest or local `.env`.

## 3. Apply and inspect

```powershell
kubectl apply -k k8s/base
kubectl get pods,services
kubectl port-forward service/frontend 8080:80
```

Open <http://localhost:8080>. The AI assistant uses its local fallback if `OPENAI_API_KEY` is omitted from the Kubernetes Secret.

## Storage ownership

- Catalog, Cart, Orders, and Payments use separate MySQL databases and users on the MySQL server.
- AI Assistant stores its conversation history in MongoDB.
- Services communicate over cluster-local HTTP Services and access only their own datastore.
