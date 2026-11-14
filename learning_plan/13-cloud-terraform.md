# Phase 13: Cloud infrastructure with Terraform

[← Master plan](README.md) · Previous: [12 Kubernetes locally](12-kubernetes-local.md) · Next: [14 CD, rollbacks, migrations →](14-cd-rollbacks-migrations.md)

**Estimated effort:** 18–22 hours · **Depends on:** Phase 12

## Outcome

All cloud infrastructure is defined in Terraform and applied through a pipeline: a Kubernetes cluster, container registry, managed Postgres, secret store, and identity federation so neither GitHub nor your pods hold long-lived credentials. The Helm chart from Phase 12 runs on it at a public HTTPS address.

## Before you create the account

- The Azure free account gives $200 of credit that **expires 30 days after sign-up**. Create the account on the day you start this phase, and plan to do Phases 13–15 in that window if you can.
- After the credit ends you are on pay-as-you-go. Keep the bill small by destroying the environment between sessions. Check current prices in the Azure pricing calculator before choosing sizes; do not rely on numbers from blog posts.
- On day one: create a budget with email alerts, in Terraform.

## Concepts

### Terraform

- Providers, resources, data sources, variables, outputs, locals.
- **State**: what it is, why it is sensitive, remote backends, locking, what drift is.
- **Modules**: when to write one, inputs and outputs, versioning.
- **Environments**: separate state per environment; directory layout versus workspaces.
- **Lifecycle**: `plan` and `apply`, `import`, `moved` blocks, `prevent_destroy`, replacing versus updating in place.
- **Testing and policy**: `terraform validate`, `tflint`, `terraform test`, security scanning of configuration.
- OpenTofu is the open-source fork with the same workflow; know it exists and why.

### Azure

- Subscriptions, resource groups, regions, Entra ID, role-based access control.
- Virtual networks and subnets, private access to managed services.
- **AKS**: control-plane tiers, node pools, the OIDC issuer, **workload identity**.
- Managed identities versus service principals.
- Key Vault, Container Registry, Database for PostgreSQL flexible server, Storage.

## Target infrastructure

| Need | Azure service | Notes |
|------|---------------|-------|
| Kubernetes | AKS, free control-plane tier | One small node pool; enable OIDC issuer and workload identity |
| Images | Azure Container Registry | AKS pulls through a managed identity |
| Postgres | Database for PostgreSQL flexible server, burstable tier | pgvector must be allow-listed in the server's extension settings |
| Redis | In-cluster Valkey or Redis to save cost; or Azure Managed Redis | Azure Cache for Redis is being retired; do not start on it |
| MongoDB | MongoDB Atlas free tier through its Terraform provider; or Azure Cosmos DB for MongoDB | Atlas behaves like real MongoDB; with Cosmos DB, check feature compatibility first |
| Secrets | Key Vault | Synced to pods with External Secrets Operator or the Secrets Store CSI driver |
| Terraform state | Storage account with blob container | Created by a small bootstrap configuration |
| Ingress | Gateway API | Same implementation as on kind for parity, or the AKS application routing Gateway API add-on |
| DNS and TLS | A cheap domain, cert-manager, Let's Encrypt | Makes `wss` and OAuth callbacks simple |
| Langfuse | Langfuse Cloud free tier | Self-hosting on AKS with the Helm chart is a stretch task; it needs ClickHouse |
| LLM | Your current provider; optionally Azure OpenAI through Foundry | A good provider-swap experiment for your evals |

### If you prefer GCP

The concepts are the same. Check current free-trial terms before signing up.

| Azure | GCP equivalent |
|-------|----------------|
| AKS | GKE (Autopilot is the low-effort option) |
| Container Registry | Artifact Registry |
| Database for PostgreSQL flexible server | Cloud SQL for PostgreSQL |
| Azure Managed Redis | Memorystore |
| Key Vault | Secret Manager |
| Workload identity with Entra ID | Workload Identity Federation for GKE |
| Storage account | Cloud Storage |
| Azure OpenAI | Vertex AI |
| Azure Monitor | Cloud Monitoring and Cloud Logging |

## Build steps

### Bootstrap

- [ ] Install the Azure CLI and Terraform; pin the Terraform and provider versions.
- [ ] A `bootstrap` configuration that creates the resource group, storage account and container for remote state. This one uses local state; commit nothing sensitive.
- [ ] Configure the remote backend with locking for everything else.

### Layout

- [ ] `deploy/terraform/modules/` for `network`, `aks`, `postgres`, `registry`, `keyvault`, `identity`.
- [ ] `deploy/terraform/envs/dev/` composing the modules. One cloud environment is enough; staging and prod are namespaces.
- [ ] Consistent naming and tags on every resource (owner, environment, cost centre).

### Core infrastructure

- [ ] Virtual network with subnets for AKS and for private database access.
- [ ] AKS: free tier, small burstable nodes, autoscaling 1–3, OIDC issuer and workload identity enabled, Entra ID integration for cluster access.
- [ ] Container Registry, with pull rights granted to the cluster's kubelet identity.
- [ ] Postgres flexible server reachable only from the virtual network, pgvector allow-listed, automated backups on.
- [ ] Key Vault holding database credentials and LLM API keys.
- [ ] Budget and cost alerts.

### Identity, with no stored secrets

- [ ] GitHub Actions → Azure through OIDC federation: one identity for Terraform, a narrower one for pushing images.
- [ ] Pods → Azure through workload identity: a managed identity per workload, federated to its Kubernetes ServiceAccount, with access only to its own Key Vault secrets.
- [ ] External Secrets Operator (or the CSI driver) syncing Key Vault secrets into the namespace.

### Terraform in CI

- [ ] On pull requests touching `deploy/terraform/`: `fmt -check`, `validate`, `tflint`, a configuration security scan, and `plan` posted as a comment.
- [ ] On merge: `apply` of the reviewed plan, behind a GitHub environment with manual approval.
- [ ] A scheduled `plan` that reports drift.
- [ ] At least one `terraform test` for a module.

### Deploy

- [ ] Update CI to push images to the cloud registry.
- [ ] Install the Gateway implementation, cert-manager and External Secrets.
- [ ] Install your application chart by hand with Helm into a `staging` namespace. Phase 14 automates this.
- [ ] Run migrations through the Helm hook against managed Postgres.
- [ ] Run the E2E smoke tests against the public URL.

### Cost discipline

- [ ] `make cloud-up` and `make cloud-down`. Time a full destroy and recreate. If it is not reliable, fix it; this is your disaster recovery rehearsal.
- [ ] Review cost analysis after the first three days and find the top three line items.

## Break it on purpose

- Change a resource in the portal by hand, then run `plan`. Decide whether to revert or adopt the change.
- Run two applies at once and observe state locking.
- Rename a resource in code without a `moved` block and read the plan carefully before cancelling.
- `import` a resource you created by hand.
- Remove a pod's Key Vault role assignment and trace the failure from the pod to the cause.
- Make a change that forces Postgres to be replaced and catch it in the plan. Then add `prevent_destroy`.

## Definition of done

- [ ] `terraform apply` from an empty subscription produces a working environment; `destroy` removes it cleanly.
- [ ] No cloud credential is stored in GitHub secrets or in the cluster; all access is federated.
- [ ] Terraform changes go through plan-on-pull-request and approved apply.
- [ ] The application runs on AKS at an HTTPS URL with streaming chat working over `wss`.
- [ ] Postgres is not reachable from the public internet.
- [ ] A budget alert exists, and you know your daily cost.

## Be able to explain

- What is Terraform state, why must it be remote and locked, and what do you do when it is wrong?
- How do you structure Terraform for several environments?
- How does a pod get access to Key Vault with no secret stored anywhere?
- How does GitHub Actions authenticate to Azure without a stored credential?
- You see a plan that wants to destroy and recreate the database. What do you do?
- What is drift, how do you detect it, and how do you resolve it?

## Resources

- [Terraform documentation](https://developer.hashicorp.com/terraform/docs)
- [AzureRM provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure free account terms](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account)
- [AKS documentation](https://learn.microsoft.com/en-us/azure/aks/)
- [AKS application routing with Gateway API](https://learn.microsoft.com/en-us/azure/aks/app-routing-gateway-api)
- [Azure Cache for Redis retirement FAQ](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/retirement-faq)
- [External Secrets Operator](https://external-secrets.io/)
