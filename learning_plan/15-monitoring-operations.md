# Phase 15: Monitoring and operations

[← Master plan](README.md) · Previous: [14 CD, rollbacks, migrations](14-cd-rollbacks-migrations.md) · Next: [16 Capstone and job prep →](16-capstone-job-prep.md)

**Estimated effort:** 15–18 hours · **Depends on:** Phase 14

## Outcome

Metrics, logs and traces for the whole system, dashboards for both infrastructure and LLM behaviour, service level objectives with alerts that reach you, runbooks for the likely incidents, and one practised incident from alert to postmortem.

Langfuse (Phase 05) tells you what the agent did and how well. This phase tells you whether the system is healthy and what it costs.

## Concepts

- **Three signals**: metrics, logs, traces, and how a trace ID connects them.
- **OpenTelemetry**: API, SDK, auto-instrumentation, the Collector, OTLP, semantic conventions including those for generative AI.
- **Prometheus**: pull model, metric types (counter, gauge, histogram), labels and cardinality, PromQL basics, recording and alerting rules.
- **Methods**: RED (rate, errors, duration) for services; USE (utilisation, saturation, errors) for resources.
- **SLIs, SLOs and error budgets**; burn-rate alerting; alerting on symptoms and not causes.
- **Alert quality**: actionable, with a runbook link, routed, deduplicated. You know what alert fatigue looks like from flaky tests.
- **LLM-specific signals**: time to first token, tokens per second, tokens and cost per run, steps per run, tool error rate, provider error and rate-limit rate, guardrail triggers, interrupt wait time, online eval scores, user feedback rate.

## Build steps

### Instrumentation

- [ ] OpenTelemetry in the API and worker: auto-instrument FastAPI, HTTP clients, SQLAlchemy, Redis and MongoDB.
- [ ] Custom metrics: active WebSocket connections, runs started, completed, failed and cancelled, time to first token, run duration, tokens in and out by model, estimated cost, tool calls by tool and outcome, queue depth, ingestion throughput, rate-limit rejections.
- [ ] Keep label cardinality bounded: never user ID, conversation ID or raw error text as a label.
- [ ] Structured logs carrying trace ID and span ID.
- [ ] Put the OTel trace ID on the Langfuse trace and the Langfuse trace ID in logs, so you can move between an infrastructure trace and an agent trace in one step.
- [ ] Frontend: basic error reporting and Web Vitals (optional).

### Stack on the cluster

- [ ] OpenTelemetry Collector receiving OTLP from the applications.
- [ ] kube-prometheus-stack (Prometheus, Alertmanager, Grafana, node and Kubernetes metrics), managed by Argo CD.
- [ ] Loki for logs and Tempo for traces, or the Azure managed equivalents if you want less to run. Write an ADR on the choice and its cost.
- [ ] ServiceMonitors for your services, the Postgres operator or exporter, Redis and the gateway.

### Dashboards (as code, in the repository)

- [ ] **Service overview**: request rate, error rate, latency percentiles, saturation, per deployment version.
- [ ] **Chat experience**: active connections, time to first token p50 and p95, run duration, cancellation and error rates, reconnects.
- [ ] **LLM usage and cost**: tokens and cost by model, by agent and per run; provider errors and rate limits; cache-hit tokens.
- [ ] **Agent behaviour**: steps per run, tool call rate and failures, router distribution, interrupts pending, guardrail triggers.
- [ ] **Data stores**: Postgres connections, slow queries and replication; Redis memory and stream lengths; queue depth.
- [ ] **Cost**: cloud spend from Azure cost data beside LLM spend, with cost per conversation.

### SLOs and alerts

- [ ] Define three or four SLOs in `docs/slo.md`. Suggestions: chat availability (runs that complete without a system error), time to first token under a threshold for 95% of runs, API availability, ingestion freshness.
- [ ] Multi-window burn-rate alerts for each SLO.
- [ ] Cause-based alerts only where they are clearly actionable: pod crash loops, database connections near the limit, certificate expiry, queue backlog, daily LLM spend above budget, online eval score below threshold.
- [ ] Alertmanager routing to a channel you will see (email, Slack or a phone push service). Every alert links to a runbook.
- [ ] Wire the Argo Rollouts AnalysisTemplate from Phase 14 to these metrics, so a bad canary aborts on its own.

### Synthetic monitoring

- [ ] A scheduled probe that logs in, opens a WebSocket, sends a message in fake-LLM mode and checks the stream. Reuse your k6 or Playwright scripts.
- [ ] A second, less frequent probe using a real model, to catch provider problems.

### Runbooks

Write one page each in `docs/runbooks/`: symptoms, dashboards to open, checks in order, mitigations, escalation.

- [ ] LLM provider outage or rate limiting (fallback model, degrade to docs-only, user messaging).
- [ ] Time to first token degraded.
- [ ] Runaway cost.
- [ ] Database connection exhaustion.
- [ ] Stuck or failed migration.
- [ ] Bad prompt or model release (ties to the Phase 14 rollback runbook).
- [ ] Redis unavailable.

### Game day

- [ ] Pick a failure, inject it in staging without looking at dashboards first, and work only from the alert: detect, diagnose with the runbook, mitigate, verify.
- [ ] Write a blameless postmortem: timeline, impact, root cause, what went well, action items. Measure time to detect and time to recover.

## Break it on purpose

- Make the mock LLM return errors for 20% of calls and see which alert fires, and how long it takes.
- Add a metric label with unbounded values and watch Prometheus memory.
- Deploy a canary that adds 3 seconds of latency and confirm the automatic abort.
- Let a TLS certificate approach expiry on staging by breaking renewal.
- Start an agent loop that burns tokens and see whether the cost alert or the per-run limit catches it first.
- Delete a dashboard by hand and confirm it comes back from Git.

## Definition of done

- [ ] From a slow chat response you can get to the responsible span, its logs and the Langfuse trace in under two minutes.
- [ ] Six dashboards exist as code and are deployed through GitOps.
- [ ] SLOs are documented, with burn-rate alerts that have fired at least once in a drill.
- [ ] Every alert links to a runbook.
- [ ] A canary has aborted automatically from metric analysis.
- [ ] Synthetic probes run on a schedule and alert on failure.
- [ ] One game day is done, with a written postmortem.

## Be able to explain

- What is the difference between monitoring and observability?
- How do you choose SLIs for a streaming chat product? Why is plain request latency a poor one?
- What is burn-rate alerting, and why is it better than a static threshold?
- Which metrics exist only because this is an LLM application?
- How do you track and control LLM cost in production?
- What do you do when the model provider is down?
- What is metric cardinality, and how did you keep it under control?

## Resources

- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [Prometheus documentation](https://prometheus.io/docs/)
- [Grafana documentation](https://grafana.com/docs/)
- [Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) (Google SRE Workbook)
- [Langfuse documentation](https://langfuse.com/docs) (OpenTelemetry integration, metrics API)
