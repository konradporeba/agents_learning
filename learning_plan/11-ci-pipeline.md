# Phase 11: CI pipeline

[← Master plan](README.md) · Previous: [10 Guardrails and security](10-guardrails-security.md) · Next: [12 Kubernetes locally →](12-kubernetes-local.md)

**Estimated effort:** 10–12 hours · **Depends on:** Phase 09 (Phase 10 recommended)

## Outcome

The CI you have grown since Phase 01 becomes a designed pipeline: fast feedback on pull requests, immutable scanned and signed images on merge, no long-lived cloud credentials, and a release flow that Phase 14 can deploy from.

You know GitHub Actions already. The goal here is design: what runs when, what blocks a merge, and what an artifact is.

## Concepts

- **Pipeline stages and feedback time**: cheap checks first, a target time for the pull request pipeline, parallelism, caching.
- **Build once, deploy many**: one image per commit, identified by digest, promoted unchanged through environments. Configuration is injected at deploy time.
- **Trunk-based development**: short-lived branches, small pull requests, `main` always releasable, feature flags for unfinished work.
- **Supply chain security**: dependency and image scanning, software bill of materials, image signing, pinned action versions.
- **Keyless authentication**: GitHub OIDC federation to the cloud, so no stored cloud secrets.
- **Monorepo CI**: path filters, reusable workflows, a required "gate" job.
- **CI for LLM applications**: which jobs need a model key, cost control, what happens on pull requests from forks.

## Build steps

### Pipeline design

- [ ] Draw the pipeline in `docs/ci-cd.md`: stages, triggers, what is required for merge, expected duration of each stage.
- [ ] Set a target: pull request feedback in under 10 minutes. Measure where you are now.

### Pull request pipeline

- [ ] Path filters so backend, web, Helm and Terraform changes trigger only their own jobs.
- [ ] One required aggregate job that passes only if every triggered job passed, so branch protection stays simple.
- [ ] Order: lint and type check → unit → integration with service containers → build image → E2E on Compose in fake-LLM mode → eval smoke (only when agent, prompt or retrieval paths change).
- [ ] Caching for `uv`, `pnpm` and Docker layers. Measure before and after.
- [ ] Concurrency groups that cancel superseded runs on the same branch.
- [ ] Upload JUnit XML, Playwright traces and eval reports as artifacts; publish a test summary on the run.
- [ ] Reusable workflows for anything used more than once.

### Images

- [ ] Multi-stage builds for `backend` and `web`, non-root, minimal base, a `.dockerignore`.
- [ ] Tag with the git SHA. Never deploy `latest`.
- [ ] Scan images and dependencies with Trivy; fail on high and critical findings with a documented exception list.
- [ ] Generate an SBOM and attach it to the image.
- [ ] Sign images with cosign using keyless signing.
- [ ] Push to GitHub Container Registry for now; Phase 13 adds the cloud registry.

### Merge to `main`

- [ ] Build, scan, sign and push; run the live-model smoke tests; then hand off to deployment (a placeholder job until Phase 14).
- [ ] Record the image digest as an output. Deployment in Phase 14 uses digests, not tags.

### Security and hygiene

- [ ] Pin third-party actions to commit SHAs.
- [ ] Default workflow permissions to read-only; grant more per job.
- [ ] LLM keys available only to jobs that need them, never to pull requests from forks.
- [ ] Renovate or Dependabot, with grouped updates and automerge for patch versions that pass CI.
- [ ] Secret scanning and push protection enabled on the repository.

### Releases

- [ ] Conventional commits, and automated versioning and changelog (for example release-please).
- [ ] A scheduled nightly workflow: full eval suite, adversarial suite, load test on Compose. Failures open an issue.

### Flaky test policy

- [ ] Write a short policy: how a flaky test is detected, quarantined, tracked and fixed. Apply it to evals too, using the variance you measured in Phase 09.

## Break it on purpose

- Add a dependency with a known critical CVE and confirm the pipeline blocks it.
- Open a pull request from a fork (a second account) and confirm no secrets are exposed and the right jobs are skipped.
- Change only a markdown file and confirm almost nothing runs but the required check still reports.
- Break one Playwright test and check that the artifacts are enough to diagnose it without rerunning locally.
- Push two commits in quick succession and confirm the first run is cancelled.

## Definition of done

- [ ] `docs/ci-cd.md` matches the workflows.
- [ ] Pull request pipeline meets the time target, with numbers before and after.
- [ ] Every merge to `main` produces images that are scanned, signed, have an SBOM, and are referenced by digest.
- [ ] No long-lived registry credential is stored in GitHub (the registry push uses the workflow token). Cloud OIDC federation is set up in Phase 13.
- [ ] Nightly evals, adversarial tests and load tests run on a schedule and alert on failure.
- [ ] A flaky test policy is written down.

## Be able to explain

- What does "build once, deploy many" mean, and what breaks if you rebuild per environment?
- Why deploy by image digest and not by tag?
- How does OIDC federation remove the need for stored cloud secrets?
- How do you keep a pull request pipeline fast as the project grows?
- Where do LLM evals belong in a pipeline, and how do you keep them from being slow, costly or flaky?
- What do image signing and an SBOM protect you against?

## Resources

- [GitHub Actions documentation](https://docs.github.com/en/actions) (reusable workflows, OIDC, security hardening)
- [Trivy](https://trivy.dev/)
- [Sigstore cosign](https://docs.sigstore.dev/)
- [Trunk-based development](https://trunkbaseddevelopment.com/)
