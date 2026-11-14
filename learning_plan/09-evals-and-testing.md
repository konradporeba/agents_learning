# Phase 09: Evals and testing

[← Master plan](README.md) · Previous: [08 Multi-agent, HITL, MCP](08-multi-agent-hitl-mcp.md) · Next: [10 Guardrails and security →](10-guardrails-security.md)

**Estimated effort:** 25–30 hours · **Depends on:** Phase 08

## Outcome

A layered quality system: deterministic tests on every pull request, evaluation datasets with code-based and LLM-judge evaluators, experiments tracked in Langfuse, an eval gate in CI, online evaluation of production traces, and E2E and load tests that run without spending on tokens.

This is the phase where your background is an advantage. Most teams building agents have weak evals, and "how do you know it works?" is the question interviewers ask. Spend the time here.

## Concepts

- **Tests versus evals**: tests assert exact behaviour of deterministic code; evals measure the quality of non-deterministic behaviour over a dataset and report a rate, not pass or fail.
- **Error analysis**: reading real traces, writing free-form notes on what went wrong, then grouping notes into a failure taxonomy. Evals should target failures you have actually observed.
- **Levels**: component (retrieval, router, classifier, single tool choice), trajectory (the sequence of steps), end-to-end (did the user's task get done).
- **Evaluator types**: code assertions, comparison to a reference, LLM-as-judge, human review. Use the cheapest one that measures what you care about.
- **LLM judges**: binary pass or fail criteria work better than 1–5 scales; a judge must be validated against human labels before you trust it.
- **Datasets**: hand-written golden cases, cases mined from production traces, synthetic cases, adversarial cases. Keep a held-out split.
- **Statistics**: repeated runs, variance, confidence intervals, why a 2-point change on 40 cases is noise.
- **Offline versus online**: datasets before release, sampling and scoring live traffic after.
- **RAG metrics**: faithfulness (is the answer supported by the retrieved context), answer relevance, context precision and recall.
- **Agent metrics**: task success, tool selection accuracy, step count, cost, latency.

## Build steps

### Test strategy

- [ ] Write `docs/test-strategy.md`: one table listing each layer, what it covers, where it runs (pull request, merge, nightly), whether it calls a real model, and its time budget.

### Deterministic layer (every pull request, no API key)

- [ ] Consolidate the scripted fake chat model into a shared fixture.
- [ ] Record and replay for provider HTTP calls (VCR-style cassettes) for a few integration tests that need realistic responses.
- [ ] Safety invariants as plain tests: no issue creation without approval, no cross-tenant retrieval or memory, no unbounded tool output.

### Error analysis

- [ ] Use the app for real work for a few sessions. Then review 50–100 traces in Langfuse.
- [ ] For each, write a one-line note on the first thing that went wrong, if anything.
- [ ] Group the notes into 5–10 failure categories and count them. Put the table in the docs. The top categories decide which evals you build next.

### Datasets

Keep them as JSONL in `evals/datasets/` under version control and sync them to Langfuse datasets.

- [ ] `rag_qa`: grow the Phase 06 set to 60 or more.
- [ ] `triage_labeled`: from Phase 08, with true categories.
- [ ] `routing`: user message → expected route.
- [ ] `tool_selection`: request → tools that should and should not be called.
- [ ] `memory`: the multi-conversation cases from Phase 07.
- [ ] Split each into development and held-out test portions.

### Evaluators

- [ ] **Retrieval**: recall@k, MRR (code, from Phase 06).
- [ ] **Citations**: every cited chunk exists and was retrieved (code).
- [ ] **Faithfulness**: an LLM judge with a binary verdict and a reason. Write your own first, then compare with Ragas or DeepEval.
- [ ] **Answer correctness** against the reference answer (LLM judge).
- [ ] **Triage**: accuracy, per-class precision and recall, and a confusion matrix (code). You have true labels, so no judge is needed.
- [ ] **Trajectory**: required tools called, forbidden tools not called, steps and cost under a limit (code).
- [ ] **Refusal**: unanswerable questions get "not found" and answerable ones do not (code plus judge).

### Judge calibration

- [ ] Label 50 answers yourself as pass or fail for faithfulness, without looking at the judge.
- [ ] Compare with the judge: agreement, true positive rate, true negative rate.
- [ ] Improve the judge prompt on the development split until agreement is acceptable, then report the numbers on the held-out split.
- [ ] Record this in the docs. A judge with measured agreement is evidence; a judge without it is an opinion.

### Experiment runner

- [ ] `make eval SUITE=rag` runs a dataset through the real application code, records each item as a trace linked to a Langfuse dataset run, and tags it with git SHA, prompt version and model.
- [ ] Output a markdown report and a JSON summary.
- [ ] Run each suite three times and report the mean and spread.
- [ ] Use it for three real experiments and write up the results: swap the model, change the chunking, change a prompt.

### CI gate

- [ ] On pull requests that touch agents, prompts or retrieval: a smoke eval of about 20 cases on a cheap model, with thresholds, posting a summary comment with the change against `main`.
- [ ] Nightly: the full suite, with results stored and trend visible.
- [ ] Decide thresholds from the measured spread, so the gate does not flake. You know what a flaky gate does to a team.
- [ ] Budget: cap the cost of a CI eval run and fail loudly if it is exceeded.

### Online evaluation

- [ ] Sample a percentage of live traces for automatic judge scoring in Langfuse.
- [ ] Route thumbs-down traces to an annotation queue; review them weekly and promote good cases into datasets.

### E2E and performance

- [ ] Playwright: all four journeys in fake-LLM mode, deterministic and fast. Two or three live-model smoke tests with tolerant assertions, run on merge only.
- [ ] A **mock LLM server**: a small OpenAI-compatible streaming endpoint with configurable latency, token rate and error rate.
- [ ] k6 against the full stack with the mock LLM: ramp concurrent conversations, set thresholds on time to first token p95 and error rate, and find the first bottleneck (connection pool, Redis, event loop, checkpoint writes).
- [ ] Compare with the Phase 03 baseline and explain the difference.

## Break it on purpose

- Degrade the system prompt on a branch and confirm the CI gate fails.
- Introduce a retrieval bug (wrong `k`, missing project filter) and see which layer catches it first.
- Run the same eval five times and look at the spread before you trust a threshold.
- Give the judge an answer that is fluent, confident and wrong.
- In the load test, inject 5% provider errors and 10-second latency spikes into the mock LLM.

## Definition of done

- [ ] `docs/test-strategy.md` exists and matches what CI runs.
- [ ] A failure taxonomy from real traces is documented with counts.
- [ ] At least five datasets, each with a held-out split.
- [ ] The faithfulness judge has measured agreement with your labels.
- [ ] A triage confusion matrix exists, and you can say which category is hardest and why.
- [ ] A deliberately bad prompt change is blocked by CI.
- [ ] Load test results identify a specific bottleneck with evidence.

## Be able to explain

- How do you test a system whose output is different every time?
- How do you decide what to evaluate first?
- Why should you not trust an LLM judge out of the box, and how do you validate one?
- What goes in a pull request gate versus a nightly run, and why?
- An eval score dropped from 86% to 83%. Is that a regression? How do you decide?
- How would you load test an LLM application without a large API bill, and what does that not tell you?

## Resources

- [Your AI product needs evals](https://hamel.dev/blog/posts/evals/) (Hamel Husain)
- [Creating an LLM judge that drives results](https://hamel.dev/blog/posts/llm-judge/) (Hamel Husain)
- [Langfuse documentation](https://langfuse.com/docs) (datasets, experiments, scores, annotation queues)
- [Ragas documentation](https://docs.ragas.io/)
- [DeepEval](https://github.com/confident-ai/deepeval)
