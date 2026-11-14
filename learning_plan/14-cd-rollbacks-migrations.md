# Phase 14: Continuous delivery, rollbacks and migrations

[← Master plan](README.md) · Previous: [13 Cloud with Terraform](13-cloud-terraform.md) · Next: [15 Monitoring and operations →](15-monitoring-operations.md)

**Estimated effort:** 18–22 hours · **Depends on:** Phase 13

## Outcome

Merging to `main` deploys to staging automatically; production is a reviewed promotion with a canary. You have rolled back a bad release, shipped a breaking schema change with no downtime, and rolled out and rolled back a prompt and a model independently of code.

An agentic application has more things to version than a normal service. Each needs its own rollout and rollback path:

| What changes | How it is rolled out | How it is rolled back |
|--------------|---------------------|-----------------------|
| Application code | New image digest through GitOps | Revert the commit in the GitOps repository |
| Database schema | Expand/contract migrations | Roll forward; the old code must still work on the new schema |
| Prompts | Langfuse label moved to a new version | Move the label back |
| Model version | Configuration change behind an eval gate | Revert the configuration |
| Embedding model | Dual-write, backfill, switch, drop | Switch reads back to the old column |
| Agent state schema | Backward-compatible state changes | Old threads must still load |
| Infrastructure | Terraform plan and apply | Revert and apply; some changes are not reversible |

## Concepts

- **Continuous delivery versus deployment**; promotion between environments.
- **GitOps**: desired state in Git, a controller reconciles the cluster, pull versus push deployment, drift correction.
- **Deployment strategies**: rolling, blue/green, canary; automated analysis; feature flags as a separate release mechanism.
- **Rollback**: what it means for stateless code versus stateful data; why "roll back the database" is usually the wrong plan.
- **Expand/contract** (parallel change): add the new shape, write to both, backfill, switch reads, remove the old shape, across several releases.
- **Safe Postgres changes**: locks taken by DDL, `CREATE INDEX CONCURRENTLY`, adding constraints as `NOT VALID` then validating, lock timeouts, batching backfills.
- **Compatibility window**: during any rollout two code versions run at once against one schema and one set of checkpoints.
- **Backups and restore**: point-in-time recovery, recovery point and recovery time objectives.

## Build steps

### GitOps with Argo CD

- [ ] Install Argo CD on the cluster (through Terraform or a bootstrap script).
- [ ] `deploy/gitops/`: an Application per environment (`staging`, `prod`) pointing at your chart with per-environment values. Add the platform components (gateway, cert-manager, External Secrets) as Applications too.
- [ ] Staging syncs automatically with self-heal; production requires a merged pull request.
- [ ] CI on merge to `main` commits the new image digest to the staging values. No `kubectl` or `helm` from CI.
- [ ] Argo CD verifies image signatures or an admission policy rejects unsigned images (stretch).

### Promotion

- [ ] After staging sync: automated smoke tests (Playwright against staging, a short k6 run, the eval smoke suite against the deployed build).
- [ ] If they pass, a workflow opens a pull request that promotes the same digest to production.
- [ ] Deployment markers sent to Langfuse (release tag) and to your dashboards.

### Progressive delivery

- [ ] Argo Rollouts for the API: canary steps (for example 10%, 50%, 100%) with pauses.
- [ ] An AnalysisTemplate that queries error rate and latency and aborts the rollout automatically. Wire it to real metrics in Phase 15; use a manual gate until then.
- [ ] Make sure canary traffic splitting works for WebSocket connections, and that existing connections drain as in Phase 12.

### Rollback drills

- [ ] Ship a release that returns 500 on one endpoint. Roll back three ways and time each: `git revert` in the GitOps repository, Argo CD's history rollback, and an aborted canary. Write down which you would use in an incident and why.
- [ ] Ship a release whose readiness probe never passes. Observe that the rollout stalls and nothing is harmed.

### Zero-downtime schema migration

- [ ] Confirm how the migration Job runs under Argo CD (it treats Helm pre-upgrade hooks as PreSync hooks). Decide what happens to the sync when the Job fails, and test it.
- [ ] Add a migration check to CI that flags dangerous operations (table rewrites, `NOT NULL` without default, non-concurrent index creation).
- [ ] **Drill**: rename `conversations.title` to `name` with no downtime, as separate releases: add the column → write to both → backfill in batches → read from the new column → stop writing the old one → drop it. Run the k6 test throughout and show zero errors.
- [ ] Do it the wrong way once on staging (a single rename migration during a rolling update) and capture the errors.
- [ ] Build an index on `chunks` with `CREATE INDEX CONCURRENTLY` and note why it cannot run inside a transaction.
- [ ] Set a lock timeout in migrations so a blocked DDL statement fails fast.

### AI-specific rollouts

- [ ] **Prompt**: promote a new prompt version by moving a Langfuse label, gated by the eval suite. Roll it back by moving the label. No deploy involved. Decide who is allowed to move the `production` label.
- [ ] **Model**: pin exact model versions in configuration. Upgrade through a pull request that includes an eval comparison. Run old and new side by side on a slice of traffic with a feature flag and compare scores in Langfuse.
- [ ] **Embedding model migration**: add a second embedding column for a new model, dual-write on ingest, backfill with a worker job, compare retrieval metrics on both, switch reads behind a flag, then drop the old column. This is expand/contract applied to vectors.
- [ ] **Agent state**: add a field to a graph's state and deploy while old threads exist. Confirm that old checkpoints load and that a run paused at an interrupt before the deploy can be resumed after it. Write down your rules for compatible state changes.
- [ ] **Feature flags**: a simple flag mechanism (configuration or a small open-source flag service) used for at least the model switch and the embedding switch.

### Backup and restore

- [ ] Restore managed Postgres to a point in time into a new server, point staging at it, and verify data. Record how long it took.
- [ ] Decide what you would do about MongoDB and Redis data in a disaster, and write it down.

## Break it on purpose

- Deploy code that needs a column before the migration has run.
- Roll back code after a contract-phase migration has dropped the column it needs.
- Start a long-running transaction, then run a migration that needs a lock on the same table, with and without a lock timeout.
- Change a value by hand with `kubectl edit` and watch Argo CD revert it.
- Remove a field from the agent state that old checkpoints contain, and resume an old thread.
- Move the production prompt label to a deliberately bad version, notice it from Langfuse scores, and roll back. Time the detection, not only the fix.

## Definition of done

- [ ] A merge to `main` reaches staging with no manual step; production is one reviewed pull request away.
- [ ] A bad release has been rolled back three ways, with timings recorded.
- [ ] The column rename drill completed with zero failed requests under load.
- [ ] A prompt and a model have each been rolled out and rolled back without a code deploy.
- [ ] The embedding model migration completed with before and after retrieval metrics.
- [ ] A run interrupted before a deploy resumed successfully after it.
- [ ] A point-in-time restore has been performed and timed.
- [ ] `docs/runbooks/rollback.md` describes each rollback path.

## Be able to explain

- How do you ship a breaking schema change with zero downtime?
- Why is rolling back a database migration usually a bad idea, and what do you do instead?
- What is GitOps, and what does it give you over `helm upgrade` from a pipeline?
- How does a canary release decide to abort?
- How do you roll out a prompt change safely, and how is that different from a code change?
- You need to change the embedding model. Walk through the migration.
- What happens to conversations that are in progress while you deploy a new version of the agent graph?

## Resources

- [Argo CD documentation](https://argo-cd.readthedocs.io/)
- [Argo Rollouts](https://argoproj.github.io/rollouts/)
- [Parallel change (expand and contract)](https://martinfowler.com/bliki/ParallelChange.html) (Martin Fowler)
- [PostgreSQL: explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [Langfuse documentation](https://langfuse.com/docs) (prompt management, labels)
