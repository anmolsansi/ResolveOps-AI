# ResolveOps AI — Product Roadmap from V10a to Production

## Purpose of this document

This file plans the next stages of ResolveOps AI from the current codebase through a product that can support real paying customers and, later, larger organizations.

The current repository has already reached **V10a: Analytics & Reporting + Advanced Security**.

That means the next roadmap should not restart old version names or pretend earlier work is still unbuilt.

The roadmap below continues from the actual repository state.

It deliberately prioritizes reliability, operations, safety, and real integrations before adding many new visual features.

---

# 1. Roadmap philosophy

The project has reached the point where adding another 20 pages creates less value than making the existing 30+ pages dependable.

Therefore the next sequence is:

```text
V10a current product
      |
      v
V10b prove and harden what exists
      |
      v
V11 connect to real systems and run jobs reliably
      |
      v
V12 test AI and actions like a serious production system
      |
      v
V13 add channels and preserve customer context
      |
      v
V14 turn support into product intelligence
      |
      v
V15 expose ResolveOps safely to other applications/AI agents
      |
      v
V16 optional self-service SaaS productization
```

---

# 2. V10b — Documentation, Validation, and Release Hardening

## Goal

Turn V1–V10a from “many implemented features” into “one product we can prove works together.”

This is the immediate next milestone.

## Why V10b comes before new features

Current problems:

- root documentation is behind the code;
- smoke validation stops at V4;
- later frontend pages need more tests;
- production deployment and recovery need proof.

If we skip this and add V11 immediately, the uncertainty grows.

---

## V10b.1 Documentation alignment

### Build/update

- root README covering V1–V10a;
- root version-status document covering V1–V10a;
- architecture overview;
- data model overview;
- security model;
- deployment/operations runbook;
- API overview;
- release history;
- these client-readiness documents.

### Acceptance criteria

A new engineer can explain:

- how data enters ResolveOps;
- how RAG answers are created;
- how workspaces isolate clients;
- how the widget works;
- how tools work;
- how routing works;
- how analytics/security work;
- which parts are mocks;
- what is production-ready versus not.

---

## V10b.2 V5 smoke test

Create `scripts/v5_api_smoke.py`.

Test:

- registration;
- login;
- unauthorized rejection;
- workspace creation/resolution;
- workspace isolation;
- PII scan/redaction;
- settings;
- prompts;
- retention preview;
- background jobs;
- audit events.

---

## V10b.3 V6 smoke test

Create `scripts/v6_api_smoke.py`.

Test:

- widget health;
- session start;
- customer message;
- AI answer;
- stored conversation;
- customer profile;
- handoff;
- agent reply;
- resolution;
- feedback.

---

## V10b.4 V7 smoke test

Create `scripts/v7_api_smoke.py`.

Test:

- tools list;
- tool enable/disable;
- invalid parameter rejection;
- execution;
- execution log;
- action audit;
- widget tool triggering.

---

## V10b.5 V8 smoke test

Create `scripts/v8_api_smoke.py`.

Test:

- conversation summaries;
- performance metrics;
- KB suggestion generation;
- suggestion accept/dismiss;
- copilot suggestion generation;
- feedback summary.

---

## V10b.6 V9 smoke test

Create `scripts/v9_api_smoke.py`.

Test:

- routing rule create/update/delete;
- rule execution;
- canned response create/search/use;
- portal article create/publish;
- public retrieval;
- ticket status lookup.

---

## V10b.7 V10a smoke test

Create `scripts/v10a_api_smoke.py`.

Test:

- analytics time range;
- agent performance;
- saved report;
- CSV export;
- API-key lifecycle;
- key expiration/scope behavior;
- rate-limit behavior;
- login-attempt behavior;
- IP allowlist behavior in controlled test mode.

---

## V10b.8 CI integration

Update GitHub Actions so the later smoke tests run automatically.

To keep runtime manageable, organize them into logical stages rather than repeatedly rebuilding the entire stack when unnecessary.

### Acceptance criteria

A pull request cannot merge if a critical later-version smoke flow fails.

---

## V10b.9 Frontend testing

Add tests for major later pages.

Priority:

- Conversations;
- Conversation Detail;
- Handoffs;
- Tools;
- Intelligence;
- Copilot;
- Routing;
- Portal;
- Analytics;
- Reports;
- Security.

Test:

- loading;
- success;
- empty state;
- error state;
- permission state;
- important forms.

---

## V10b.10 Browser E2E

Add at least one browser-level end-to-end test.

A real browser test should:

1. login;
2. upload sample tickets;
3. ask cited RAG question;
4. open customer widget;
5. create conversation;
6. trigger handoff;
7. resolve in agent console;
8. inspect analytics/audit.

**E2E** means **end to end** — testing the full workflow as a user experiences it.

---

## V10b.11 Staging environment

Create a staging deployment.

A **staging environment** is a safe production-like environment where a release can be tested before real customers use it.

Add:

- staging database;
- staging secrets;
- staging domain;
- deployment verification;
- health check.

---

## V10b.12 Backup and restore proof

Configure automatic backups.

Perform at least one restore test.

Document:

- backup frequency;
- restore command/process;
- expected recovery time.

---

## V10b.13 Monitoring and alerting

Add:

- server error monitoring;
- uptime check;
- database health;
- important job failures;
- AI provider failures;
- connector failures;
- unusual cost/quality alerts.

---

## V10b definition of done

V10b is complete when:

- docs match V10a;
- clean deployment works;
- V1–V10a critical workflows have automated proof;
- staging exists;
- monitoring exists;
- backup is configured and restore tested;
- one full browser path is tested;
- a client-ready demo can be reproduced without manual guesswork.

---

# 3. V11 — Real Integrations and Production Background Processing

## Goal

Connect ResolveOps to real client support systems and process work reliably without manual endpoint triggering.

---

## V11.1 Choose the first real helpdesk connector

Do not implement all vendors at once.

Build whichever connector a paying/design-partner client actually needs.

Possible order:

1. Zendesk;
2. Intercom;
3. Freshdesk.

But client demand should decide.

---

## V11.2 Real connector requirements

For each provider implement:

- authentication;
- secure credential storage;
- ticket listing;
- pagination;
- incremental updates;
- rate-limit handling;
- retry;
- timeout;
- backoff;
- deletion/update behavior;
- customer mapping;
- attachment policy;
- sync health;
- error visibility.

---

## V11.3 OAuth where appropriate

**OAuth** is a standard way to let a user authorize one application to access another service without giving away the user’s password.

Use vendor-supported authorization patterns rather than asking clients to paste long-lived secrets when a safer mechanism exists.

---

## V11.4 Webhooks

Add webhook listeners for important source-system changes.

A **webhook** is an automatic notification from another service when something changes.

Use webhooks for faster updates and polling as fallback/reconciliation.

---

## V11.5 Production worker

Replace manual/in-process job processing with a dedicated worker model.

Requirements:

- multiple workers safe;
- job lock;
- retry;
- exponential backoff;
- timeout;
- progress;
- dead-letter queue;
- idempotency;
- observability.

---

## V11.6 Scheduler

Create an always-running scheduler for:

- connector sync;
- retention;
- quality jobs;
- scheduled reports;
- maintenance.

---

## V11.7 Real-time sync dashboard

Show:

- connector status;
- last successful sync;
- last attempted sync;
- records imported;
- failed records;
- current delay;
- credential state.

---

## V11.8 Client onboarding UI

Add a non-technical setup wizard:

1. select helpdesk;
2. authorize;
3. choose data range;
4. map fields;
5. preview;
6. import;
7. see errors;
8. run evaluation.

---

## V11 definition of done

At least one real support platform can be connected by a client without source-code edits, and sync failures are visible/recoverable.

---

# 4. V12 — AI Safety and Evaluation Laboratory

## Goal

Make AI changes testable before they reach customers.

This should become one of ResolveOps’ strongest differentiators.

---

## V12.1 Golden test sets

Store client/workspace-specific expected cases.

Each case can define:

- question;
- expected answer facts;
- required source;
- expected handoff;
- expected tool;
- forbidden behavior.

---

## V12.2 Synthetic conversation simulator

Generate test conversations for personas/scenarios such as:

- normal customer;
- angry customer;
- confused customer;
- enterprise customer;
- billing dispute;
- cancellation;
- security problem;
- ambiguous request;
- malicious prompt injection.

**Synthetic** means generated for testing rather than created by a real customer.

---

## V12.3 Prompt comparison

Compare Prompt A and Prompt B on the same test set.

Measure:

- answer correctness;
- citations;
- fallback;
- escalation;
- latency;
- cost;
- safety.

---

## V12.4 Model comparison

Compare providers/models under identical conditions.

Do not select a model based only on one impressive answer.

---

## V12.5 LLM-as-judge with human calibration

**LLM-as-judge** means using an AI model to score another AI answer.

Useful for scale, but not perfect.

Store human corrections so automated grading can be compared with people.

---

## V12.6 Action simulation

For every new real tool:

> Run historical cases and show what actions the AI would have requested without actually performing them.

Measure:

- correct tool;
- correct parameters;
- approval correctness;
- unsafe action rate.

---

## V12.7 Prompt-injection suite

Create malicious tests for:

- direct prompt injection;
- indirect injection inside knowledge;
- attempt to reveal system prompt;
- cross-workspace data requests;
- tool manipulation;
- sensitive-data extraction.

---

## V12.8 Policy engine

Move important business safety rules out of natural-language prompts into enforceable application policy.

Example:

```text
Refund > $20 -> human approval required
Account deletion -> admin approval required
Password-reset identity failure -> mandatory handoff
```

---

## V12.9 Release gates

Do not activate a new prompt/model/tool policy if:

- critical golden tests fail;
- safety violations increase;
- wrong-tool rate exceeds threshold;
- cross-tenant tests fail.

---

## V12 definition of done

AI behavior can be tested, compared, simulated, and blocked from release when critical quality/safety requirements fail.

---

# 5. V13 — Omnichannel Support and Real-Time Agent Experience

## Goal

Allow customers to move between support channels without losing context.

**Omnichannel** means serving a customer across multiple communication channels while preserving one connected support history.

---

## V13.1 Email

Add:

- inbound email ingestion;
- threaded conversation mapping;
- AI draft;
- human reply;
- attachment policy;
- email identity rules.

---

## V13.2 WhatsApp/SMS

Integrate through an appropriate messaging provider.

Preserve consent and template requirements where applicable.

---

## V13.3 Slack/Teams/community support

Support customer communities where appropriate.

---

## V13.4 Voice

Add:

- speech to text;
- knowledge retrieval;
- AI response planning;
- human transfer;
- transcript;
- summary;
- action history.

Start with transcript/post-call intelligence before attempting fully autonomous real-time voice.

---

## V13.5 Unified customer timeline

All channels should feed one customer history.

Example:

```text
Monday: Website chat
Tuesday: Email
Wednesday: Phone
```

The customer should not restart from zero each time.

---

## V13.6 Real-time internal console

Use WebSockets or server-sent events so:

- new message appears immediately;
- handoff appears immediately;
- action completion appears immediately;
- agent ownership updates immediately.

---

## V13 definition of done

At least two meaningful customer channels share one conversation/customer context and the human-agent console updates in real time.

---

# 6. V14 — Knowledge and Product Intelligence

## Goal

Use support conversations to improve not only support, but the product itself.

---

## V14.1 Knowledge-gap detector

Group repeated questions that ResolveOps cannot answer confidently.

Example:

> “42 customers asked about SSO invite expiration. No approved article exists.”

---

## V14.2 Article freshness

Score whether knowledge may be outdated based on:

- age;
- new product releases;
- failed answers;
- contradictory newer sources.

---

## V14.3 Contradiction detection

Identify when two approved sources disagree.

Example:

- Article A says refund window is 30 days.
- Article B says 60 days.

Do not let the AI silently choose one.

---

## V14.4 Bug clustering

Group support conversations that likely share the same underlying software defect.

---

## V14.5 Engineering brief

Automatically prepare:

- issue title;
- symptoms;
- affected users;
- example conversations;
- frequency;
- severity;
- product area;
- possible reproduction clues.

---

## V14.6 Feature-request mining

Identify repeated customer requests and rank by:

- count;
- customer tier;
- revenue importance if available;
- urgency;
- sentiment.

---

## V14.7 Churn-risk signal

Detect language indicating the customer may leave.

This should be a prioritization signal, not an unquestioned prediction.

---

## V14.8 Release impact

Compare support volume before/after product releases.

Example:

> “Authentication tickets increased 170% after release 4.2.”

---

## V14 definition of done

Support data can produce validated knowledge and product-insight workflows, not merely dashboards.

---

# 7. V15 — MCP and Developer Platform

## Goal

Allow other applications and AI agents to use ResolveOps safely.

---

## V15.1 MCP server

**MCP** means **Model Context Protocol**.

It is an open protocol for connecting AI applications to external tools and data.

Potential ResolveOps tools:

- search tickets;
- query knowledge;
- get customer timeline;
- get SLA risks;
- draft support reply;
- run evaluation;
- get failed queries;
- create knowledge suggestion;
- create engineering brief.

---

## V15.2 MCP authorization

Do not expose all tools to every client.

Implement:

- OAuth-style authorization where appropriate;
- workspace binding;
- scopes;
- consent;
- tool allowlists;
- audit;
- short-lived tokens.

---

## V15.3 Public developer API

Publish stable versioned APIs.

Add:

- API docs;
- key rotation;
- usage limits;
- examples;
- error codes;
- webhook subscriptions.

---

## V15.4 SDKs

An **SDK**, or **software development kit**, is a helper package that makes it easier for developers to use an API.

Possible first SDK:

- Python;
- TypeScript.

---

## V15.5 Developer sandbox

Allow safe testing without production customer data/actions.

---

## V15 definition of done

External applications can use ResolveOps through a documented, scoped, audited integration without receiving excessive permissions.

---

# 8. V16 — Optional SaaS Productization

## Goal

Make ResolveOps self-service enough that customers can sign up and manage most of the product without a custom implementation engagement.

Do this only after repeated paid pilots prove the product is repeatable.

---

## V16.1 Organization signup

- create organization;
- verify domain/email;
- invite team;
- choose plan.

## V16.2 Billing

- subscription;
- invoices;
- payment method;
- usage charges;
- trial.

## V16.3 Usage limits

Limit:

- agents;
- conversations;
- AI usage;
- storage;
- integrations;
- exports.

## V16.4 Feature entitlements

An **entitlement** means which features a plan includes.

## V16.5 Self-service onboarding

Client can:

- create workspace;
- connect helpdesk;
- map data;
- configure AI;
- test;
- deploy widget.

## V16.6 Trust center

Publish:

- security overview;
- privacy information;
- subprocessor list;
- status page;
- incident history where appropriate;
- compliance evidence as it becomes real.

---

# 9. Cross-version work that should continue continuously

Some work should never wait for one version.

## Security

Every new feature gets a threat review.

## Documentation

Every feature PR updates docs.

## Testing

Every bug becomes a regression test where practical.

## Observability

Every important background operation exposes health/metrics.

## Accessibility

Customer and agent UI should remain keyboard/screen-reader friendly.

## Performance

Track latency and database behavior as data grows.

## Cost

Track model/infrastructure cost per useful outcome.

---

# 10. Roadmap priority by business value

## Must do before first paid production pilot

- V10b core hardening;
- backup/restore;
- monitoring;
- client evaluation set;
- safe handoff;
- clear tool restrictions;
- staging/rollback.

## Must do when first client needs live helpdesk sync

- relevant V11 connector;
- worker/scheduler;
- secure credentials;
- sync monitoring.

## Must do before scaling customer-facing AI

- V12 evaluation lab;
- prompt-injection defenses;
- release gates;
- action simulation.

## Add after repeatable revenue/use case

- omnichannel;
- product intelligence;
- MCP;
- self-service SaaS billing.

---

# 11. What should stop a roadmap item from shipping

Do not ship if:

- critical tests fail;
- another workspace’s data can be accessed;
- no rollback exists for dangerous change;
- monitoring cannot detect failure;
- high-risk action lacks approval/policy;
- documentation does not explain the feature;
- no owner exists for incidents.

---

# 12. Final roadmap principle

The project has already proven that it can add features quickly.

The next stage must prove something harder:

> **ResolveOps can operate safely, predictably, and measurably for real teams.**

That is what turns the project from impressive code into a durable product.
