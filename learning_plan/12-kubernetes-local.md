# Phase 12: Kubernetes locally

[← Master plan](README.md) · Previous: [11 CI pipeline](11-ci-pipeline.md) · Next: [13 Cloud with Terraform →](13-cloud-terraform.md)

**Estimated effort:** 15–18 hours · **Depends on:** Phase 11

## Outcome

The whole application runs on a local Kubernetes cluster (kind) from Helm charts you wrote: API, worker, web and MCP server, with databases in the cluster, traffic through the Gateway API including WebSockets, autoscaling, and graceful shutdown of streaming connections. You have also broken it in the standard ways and fixed it with `kubectl`.

Everything here costs nothing. The charts carry over to the cloud unchanged in Phase 13.

## Concepts

- **Workloads**: Pod, Deployment, ReplicaSet, StatefulSet, Job, CronJob.
- **Configuration**: ConfigMap, Secret, environment versus mounted files, why Secrets are not encrypted by default.
- **Networking**: Service types, cluster DNS, **Gateway API** (GatewayClass, Gateway, HTTPRoute), NetworkPolicy.
- **Health**: startup, readiness and liveness probes, and what each one causes Kubernetes to do.
- **Resources**: requests versus limits, quality-of-service classes, OOM kills, CPU throttling.
- **Scaling and availability**: HorizontalPodAutoscaler, PodDisruptionBudget, topology spread, rolling update parameters (`maxSurge`, `maxUnavailable`).
- **Pod lifecycle**: `SIGTERM`, `preStop` hooks, termination grace period, endpoint removal timing. This matters a great deal for WebSockets.
- **Security**: ServiceAccounts, RBAC, security contexts, Pod Security Standards.
- **Helm**: charts, values, templates, hooks, releases and revisions, `helm diff`.
- **Operators**: custom resources and controllers, using CloudNativePG as the example.

## Build steps

### Cluster

- [ ] A kind cluster with one control-plane and two worker nodes, created from a config file in the repository.
- [ ] Install a Gateway API implementation (for example Envoy Gateway). Do not use ingress-nginx; it was retired in 2026.
- [ ] Install metrics-server.

### Dependencies in the cluster

- [ ] Postgres through the CloudNativePG operator, with the pgvector extension.
- [ ] Redis or Valkey and MongoDB from maintained charts or operators. Check the image source and licence; several widely used public charts changed terms in 2025.
- [ ] These in-cluster databases are for kind and learning only. Note in the docs what you would use in production.

### Your Helm chart

- [ ] One chart for the application, with a Deployment each for `api`, `worker`, `web` and `mcp-ci`, driven by values.
- [ ] Images referenced by git SHA tag on kind (locally loaded images) and by digest from a registry. Never `latest`.
- [ ] ConfigMap for non-secret configuration; Secrets created outside the chart for now (Phase 13 adds proper secret management).
- [ ] A migration **Job** as a Helm pre-upgrade hook that runs `alembic upgrade head`.
- [ ] Probes: `/healthz` for liveness, `/readyz` for readiness, a startup probe for slow starts.
- [ ] Resource requests and limits on every container, based on what you measure, not guesses.
- [ ] Security context: non-root, read-only root filesystem, dropped capabilities, no privilege escalation.
- [ ] A dedicated ServiceAccount per workload, with no extra permissions.
- [ ] `helm lint` and a template rendering test in CI; validate rendered manifests against schemas.

### Traffic

- [ ] Gateway and HTTPRoutes for the web app, REST API and WebSocket path.
- [ ] Check idle and request timeouts on the WebSocket route; a streaming answer must not be cut off.
- [ ] TLS with a locally trusted certificate, so the browser uses `wss`.

### WebSockets under rolling updates

- [ ] `preStop` hook and termination grace period sized to your longest expected run.
- [ ] On `SIGTERM` the API stops accepting new connections, finishes or hands over active runs, and closes sockets with a "going away" code so clients reconnect to another pod.
- [ ] Rolling update settings that never drop below the capacity you need.
- [ ] Run the Phase 03 reconnect E2E test during a `kubectl rollout restart`. No user-visible errors.

### Scaling and resilience

- [ ] HPA for the API on CPU. Then discuss why CPU is a poor signal for a WebSocket service and what would be better (active connections or run queue depth, through KEDA or custom metrics, as a stretch).
- [ ] HPA or queue-based scaling for the worker.
- [ ] PodDisruptionBudgets for API and web.
- [ ] NetworkPolicies: default deny, then allow only the paths in the architecture diagram.

### Automation

- [ ] `make kind-up` builds images, loads them into kind and installs everything.
- [ ] A CI job that brings up kind, installs the chart and runs a smoke test.

## Break it on purpose

Diagnose each with `kubectl get`, `describe`, `logs`, `events`, `exec` and `debug` before fixing. Write the symptoms and the diagnosis path in `docs/k8s-debugging.md`.

- Wrong image tag → `ImagePullBackOff`.
- Missing environment variable → `CrashLoopBackOff`.
- Memory limit too low → `OOMKilled`.
- Requests larger than any node → `Pending`.
- Readiness probe pointing at the wrong path → rollout hangs, old pods keep serving.
- Liveness probe that checks the database, then stop the database → restart storm.
- A migration Job that fails → what happens to the upgrade?
- Delete the Postgres primary pod → what does the operator do, and what does the API see?
- `kubectl drain` a node with and without PodDisruptionBudgets.
- NetworkPolicy that blocks the API from Redis.

## Definition of done

- [ ] `make kind-up` gives a working application at an `https` URL, with streaming chat.
- [ ] A rolling restart during an active stream causes no visible error (automated test).
- [ ] Every container has probes, resources and a restrictive security context.
- [ ] Default-deny NetworkPolicies are in place and the app still works.
- [ ] `docs/k8s-debugging.md` covers at least eight failure scenarios.
- [ ] The chart installs in CI on kind.

## Be able to explain

- What happens, in order, from `kubectl apply` of a new image to the old pod being gone?
- Why can requests still reach a pod after it receives `SIGTERM`, and how do you handle that?
- What is the difference between requests and limits, and what happens when each is exceeded?
- How do you deploy a WebSocket service without dropping connections?
- Why is the Gateway API replacing Ingress?
- What does a readiness probe failure do compared with a liveness probe failure?
- Would you run Postgres in Kubernetes in production? Argue both sides.

## Resources

- [Kubernetes documentation](https://kubernetes.io/docs/)
- [Gateway API](https://gateway-api.sigs.k8s.io/)
- [Ingress NGINX retirement notice](https://www.kubernetes.dev/blog/2025/11/12/ingress-nginx-retirement/)
- [Helm documentation](https://helm.sh/docs/)
- [kind](https://kind.sigs.k8s.io/)
- [CloudNativePG](https://cloudnative-pg.io/)
