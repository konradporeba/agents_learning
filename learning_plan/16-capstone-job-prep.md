# Phase 16: Capstone and job preparation

[← Master plan](README.md) · Previous: [15 Monitoring and operations](15-monitoring-operations.md)

**Estimated effort:** 10–12 hours · **Depends on:** as many earlier phases as you have finished

## Outcome

The repository is something a hiring manager can assess in ten minutes, you have written evidence for the claims on your CV, and you can answer the common interview questions from your own experience.

You do not need to wait until Phase 15 is finished. Do a first pass of this phase after Phase 09 and refresh it as you go.

## Positioning

You are not starting again as a junior. You are a senior engineer with 8 years in quality, automation, performance and CI/CD, who can now also build agentic systems. Roles where that combination is the point:

- **AI or agent engineer** on a product team: building what you built here.
- **AI quality or evals engineer**: designing eval systems, judges, datasets and release gates. Few candidates have real test-engineering depth, and Phase 09 is your evidence.
- **LLMOps or AI platform engineer**: deployment, observability, cost and reliability of LLM systems. Phases 11–15 are your evidence.

Lead with the eval and reliability work. "I built a RAG chatbot" is common. "I built an eval gate that blocks regressions, validated my LLM judge against human labels, and can show the confusion matrix" is not.

## Build steps

### Repository polish

- [ ] Root `README.md`: what it does in two sentences, a short demo recording, the architecture diagram, how to run it locally with one command, and links into the docs.
- [ ] A one-command local demo in fake-LLM mode, so a reviewer needs no API key.
- [ ] `docs/` index: ADRs, test strategy, eval report, threat model, red-team report, CI/CD design, SLOs, runbooks, postmortem.
- [ ] A "limitations and what I would do differently" section. Honest self-assessment reads as seniority.
- [ ] Remove dead code and secrets from history, and check the repository with fresh eyes on a clean clone.
- [ ] Decide what stays running. A live demo is nice but costs money; a recording plus a reproducible local setup is enough.

### Evidence pack

Each of these is one page with numbers. They are your answers to "tell me about a time".

- [ ] **Eval report**: datasets, metrics, judge agreement, results across three experiments.
- [ ] **Retrieval comparison**: vector, lexical, hybrid, reranked, with the metrics table.
- [ ] **Load test report**: baseline, bottleneck found, fix, result.
- [ ] **Zero-downtime migration write-up**: the steps and the zero-error graph.
- [ ] **Rollback drill write-up**: three methods with timings.
- [ ] **Security write-up**: an injection that worked, and how the architecture limited it.
- [ ] **Postmortem** from the game day.

### Writing

- [ ] Two or three short posts on LinkedIn, dev.to or a personal blog. Topics where your perspective is unusual:
  - "What a test engineer notices when testing LLM agents"
  - "Validating an LLM judge against human labels"
  - "Shipping a prompt change like a code change: gates, canaries, rollbacks"

### CV and profile

- [ ] Rewrite your summary around the combination, not the switch.
- [ ] One project entry with three or four bullet points, each stating an outcome with a number.
- [ ] Reframe past roles in terms that carry over: test strategy for non-deterministic systems, CI gates, performance engineering, observability.
- [ ] Use the vocabulary of the job descriptions you collected since Phase 05, where you can back each term with something you built.

### Interview preparation

- [ ] Collect every "Be able to explain" question from the phase files into `docs/interview-bank.md` and answer each in your own words, citing your project.
- [ ] Practise three system design prompts aloud, 35 minutes each:
  - Design a customer-support agent that can issue refunds.
  - Design a RAG system over 10 million documents with per-user permissions.
  - Design an evaluation and release process for an agent used by 50 engineers.
- [ ] Prepare a 5-minute and a 20-minute walkthrough of your project: problem, architecture, hardest decision, what failed, what you measured.
- [ ] Prepare stories for: a bug the evals caught, a design you changed after seeing traces, a trade-off you made for cost, something you got wrong.
- [ ] Do at least two mock interviews, one of them with a person.

## Stretch topics

Pick by what the job descriptions you want ask for. Each is 5–15 hours.

- **A second framework**: rebuild the triage agent in one alternative (for example the OpenAI Agents SDK, Pydantic AI, or Google's Agent Development Kit) and write a comparison. Job postings vary, and this shows your knowledge is not tied to one library.
- **Self-host Langfuse on AKS** with its Helm chart, including ClickHouse.
- **LLM gateway**: put a proxy such as LiteLLM in front of the providers for central keys, budgets, fallbacks and caching.
- **Self-hosted model**: serve an open-weight model with vLLM or Ollama and run your evals against it.
- **Dedicated vector database**: swap pgvector for Qdrant behind your retrieval interface and compare.
- **Semantic caching** in Redis, with an eval of how often it returns a wrong cached answer.
- **Agent-to-agent protocol (A2A)**: expose the triage agent to another agent.
- **Queue-based autoscaling** with KEDA on run queue depth or active connections.
- **Graph-based or structured retrieval** for questions that need joins across documents.
- **Second cloud**: port the Terraform to GCP using the mapping in [Phase 13](13-cloud-terraform.md#if-you-prefer-gcp).

## Definition of done

- [ ] A stranger can understand the project from the README in ten minutes and run it locally with one command.
- [ ] The evidence pack has at least five write-ups with real numbers.
- [ ] `docs/interview-bank.md` is complete.
- [ ] At least one post is published.
- [ ] CV and profile are updated, and you have applied to your first five roles.

## Final self-check

You should be able to answer each of these without notes, with an example from your own project:

1. How does an agent decide what to do next, and how do you stop it?
2. How do you know your RAG answers are correct?
3. What does the model see on turn 40 of a conversation, and why?
4. How does your system remember a user across conversations, and how does it forget?
5. What happens when an agent with write access reads malicious text?
6. A prompt change made things worse in production. How did you find out, and how fast can you undo it?
7. How do you deploy while users are mid-conversation?
8. What does one conversation cost, and what would you change to halve it?
