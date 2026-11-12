# AI Shop Assistant

A small, containerized e-commerce demo built from five independently deployable Python/FastAPI microservices, a React/Vite frontend, MySQL, and MongoDB. The payment integration is deliberately simulated; it does not charge real money.

## Architecture

```text
Browser
  -> React + Nginx (same-origin /api routing)
       -> Product Catalog -> MySQL: catalog_db
       -> Cart            -> MySQL: cart_db
       -> Orders          -> MySQL: orders_db -> Payments -> MySQL: payments_db
       -> AI Assistant    -> MongoDB: ai_assistant
                                -> Product Catalog (product context)
```

MySQL runs as one server locally, with a separate database and least-privilege account for each of the four SQL-owning services. The AI Assistant owns MongoDB and stores conversation history there. Services communicate over HTTP and do not query another service's database.

## Services

| Service | Responsibility | Storage | Local API |
|---|---|---|---|
| `catalog` | Product listing, detail, filters, relevance-ranked search, seed catalog | MySQL `catalog_db` | `http://localhost:8001/docs` |
| `cart` | Demo shopper's cart and quantities | MySQL `cart_db` | `http://localhost:8002/docs` |
| `orders` | Price snapshots, stock checks, order status and payment orchestration | MySQL `orders_db` | `http://localhost:8003/docs` |
| `payments` | Demo-only payment authorization records; no real payment gateway | MySQL `payments_db` | `http://localhost:8004/docs` |
| `assistant` | Natural-language product matching, optional LLM response, conversation history | MongoDB `ai_assistant` | `http://localhost:8005/docs` |

The browser uses the frontend's same-origin `/api` endpoints. Vite proxies these paths to the local services during development; Nginx does the routing in the frontend container.

## Run with Docker Compose

Docker Desktop must be running. From the repository root:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the local example database passwords. `OPENAI_API_KEY` is optional: without it, the assistant uses its Python fallback and still returns catalog products. Then run:

```powershell
docker compose up --build
```

Open the application at <http://localhost/>. The service APIs are also published on ports 8001–8005 for local development. MySQL and MongoDB ports are bound to loopback only. Data persists in the `mysql_data` and `mongo_data` Compose volumes.

Stop the stack with `docker compose down`; use `docker compose down -v` only when intentionally deleting local database data.

## Run the frontend locally

Start the Compose services, then run Vite in another terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Vite's `/api` proxy keeps browser requests same-origin and forwards them to the local service ports.

## API examples

```text
GET    /api/products?q=gaming%20laptop&max_price=100000
GET    /api/products/{id}
GET    /api/cart
POST   /api/cart                 {"product_id": 1, "quantity": 1}
PUT    /api/cart/{item_id}       {"quantity": 2}
DELETE /api/cart/{item_id}
POST   /api/orders               {"items": [{"product_id": 1, "quantity": 1}]}
POST   /api/chat                 {"message": "I need a laptop under 70000"}
```

The frontend's **Checkout (demo)** button creates an order and requests a simulated payment. It is not a real checkout or payment processor.

Each service exposes `/health` for liveness, `/ready` for dependency readiness, and `/docs` for FastAPI's OpenAPI documentation.

## Kubernetes readiness

Starter manifests and local deployment notes are in [`k8s/`](./k8s/). They include the five services, frontend, MySQL and MongoDB workloads, persistent volume claims, probes, resource requests/limits, ConfigMaps, and Secret references. They are templates: build and publish the service images to a registry, create the documented Kubernetes Secret, then apply the base manifests. Storage classes, ingress/TLS, secret management, backups, and production scaling should be configured for the target cluster.

## Technology

- React, Vite, JavaScript, CSS, Nginx
- Python, FastAPI, SQLAlchemy
- MySQL 8 for catalog, cart, orders, and demo payments
- MongoDB for AI conversation history
- Docker Compose; Kubernetes starter manifests
- Pytest

## Project layout

```text
frontend/                 React UI, local proxy and production Nginx
services/catalog/         Product catalog microservice
services/cart/            Shopping cart microservice
services/orders/          Order and payment orchestration microservice
services/payments/        Demo payment microservice
services/assistant/       AI assistant and MongoDB conversation history
services/common/          Shared DB/health helpers (no cross-service business logic)
mysql/init/                Local MySQL database/user bootstrap
k8s/base/                 Kubernetes starter resources
docker-compose.yml        Local container orchestration
.env.example              Local environment-variable template
```
