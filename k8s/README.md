# Kubernetes Readiness

This project is intentionally structured to be ready for future Kubernetes deployment.

Future manifests may include:

- backend-deployment.yaml
- backend-service.yaml
- frontend-deployment.yaml
- frontend-service.yaml
- configmap.yaml
- secret.yaml

The application currently uses environment variables for configuration, keeps application state minimal, and exposes health checks for future readiness and liveness probes.
