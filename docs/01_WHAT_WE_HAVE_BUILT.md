# ResolveOps AI — What We Have Already Built

## Purpose of this document

This file is the detailed inventory of what already exists in the ResolveOps AI repository.

The goal is to answer a simple question:

> **If somebody opens the code today, what can ResolveOps already do?**

This document does not assume that the reader knows software engineering. Technical words are explained as they appear.

It is also intentionally careful about the word **built**.

A feature can exist in code and still need more work before a paying client should depend on it.

For that reason, this document uses three levels:

- **Built for demo/portfolio use** — the feature exists, can be shown, and has automated checks.
- **Built enough for a controlled pilot** — a client could potentially use it in a limited environment after the missing operational work is completed.
- **Enterprise production complete** — a much higher bar that requires mature operations, security, recovery, monitoring, and proven real-world behavior.

Most of the items below are at the first level, and several are approaching the second.

---

# 1. Current codebase position

The current `main` branch has evolved through **V10a: Analytics & Reporting + Advanced Security**.

The project has database changes numbered `001` through `011`.

A **database migration** is a controlled change to the structure of the database.

For example:

- an early migration created ticket tables;
- later migrations added quality information;
- V5 migrations added enterprise/governance information;
- V6 added customer conversations;
- V7 added action tools;
- V8 added intelligence;
- V9 added workflow automation;
- V10a added analytics and security tables.

This progression is useful because it shows that the project was not built as one giant experiment. Each stage added a new layer.

---

# 2. V1 — Core Support Intelligence MVP

## What V1 was trying to prove

The first version asked:

> Can ResolveOps learn from old support tickets and produce evidence-backed answers instead of generic AI guesses?

This was the correct first problem to solve because every later feature depends on trustworthy support knowledge.

## 2.1 CSV ticket upload

ResolveOps can accept support-ticket data through CSV upload.

A **CSV file** is a spreadsheet-like text file.

The upload flow gives the project a simple, low-cost way to work with historical support data without requiring a live Zendesk or Intercom account.

### Built behavior

The ingestion flow can:

- receive a CSV file;
- inspect rows;
- validate required information;
- store valid tickets;
- report invalid rows;
- track duplicate ticket IDs;
- create chunks;
- generate embeddings;
- record ingestion statistics.

## 2.2 Ticket validation

The application does not assume every uploaded row is correct.

It checks whether required information is present and records errors.

Why this matters:

If a row is missing the actual support message, the AI should not silently treat it as high-quality knowledge.

## 2.3 Duplicate tracking

The system tracks duplicate ticket IDs during ingestion.

Later versions also added meaning-based duplicate detection.

These are different concepts.

### Exact duplicate

Two records have the same ticket ID or identical identity.

### Semantic duplicate

Two records use different words but describe essentially the same problem.

**Semantic** means “related to meaning.”

## 2.4 Chunking

Long ticket text is broken into smaller pieces called **chunks**.

This allows the retrieval system to find the most relevant part of a long support conversation rather than treating the whole conversation as one block.

## 2.5 Embeddings

The system creates **embeddings** for searchable text.

An embedding is a numerical representation of meaning.

It helps the system recognize that:

- “charged twice”;
- “duplicate payment”;
- “two identical card transactions”

may describe similar situations even though the wording is different.

## 2.6 Ticket list and ticket detail

The application provides APIs and frontend pages for viewing tickets.

A user can browse tickets and inspect individual ticket details.

This is important because users should be able to inspect the information that the AI is using.

## 2.7 RAG question answering

V1 implemented the core RAG flow.

**RAG** means **Retrieval-Augmented Generation**.

Plain-English meaning:

1. search company knowledge;
2. retrieve relevant evidence;
3. give that evidence to the AI;
4. ask the AI to answer using it.

The query result includes information such as:

- answer;
- citations;
- confidence;
- query ID;
- latency;
- estimated cost;
- retrieved chunks;
- quality signals.

## 2.8 Citations

ResolveOps can return references showing which support records contributed to an answer.

This is a major product decision.

Instead of saying:

> “Trust the AI because it sounds confident,”

ResolveOps is designed to say:

> “Here is the answer, and here is the support evidence behind it.”

## 2.9 Low-confidence fallback

If the retrieval result is too weak, the system can return a fallback instead of inventing an answer.

Example:

If the ticket database only contains software-support information and somebody asks:

> “What caused the French Revolution?”

the correct product behavior is not to become a history chatbot.

It should say that the available support knowledge does not contain enough information.

## 2.10 Basic dashboard

V1 includes quality/retrieval dashboard concepts that allow a user to inspect ingestion and AI-query behavior.

## 2.11 Evaluation runs

The project can create and list evaluation runs.

An **evaluation** is a structured test of how well the AI system performs on a set of questions.

This was the beginning of the reliability work expanded in V3.

## 2.12 Docker startup

The project includes Docker support.

**Docker** packages an application with the environment it needs.

The backend runs database migrations before starting the API server.

That reduces the chance of running new code against an outdated database structure.

## 2.13 Sample-data generator

The repository includes a script that generates sample support tickets.

This makes the demo repeatable without requiring real customer data.

## 2.14 V1 automated validation

The repository includes `scripts/v1_api_smoke.py`.

A **smoke test** is a broad test that checks whether the main application path works after startup.

The current CI runs this V1 smoke flow inside Docker.

### V1 assessment

**Status: built and demo complete.**

---

# 3. V2 — Portfolio Polish and Validation

V2 focused less on new customer-facing features and more on proving that the project can be reliably built and checked.

## 3.1 Stronger CI

**CI** means **continuous integration**.

It is an automated process that checks code after changes are pushed.

The current project runs backend and frontend validation through GitHub Actions.

## 3.2 Backend linting

The backend uses Ruff.

A **linter** checks code for suspicious patterns, common mistakes, and consistency problems.

## 3.3 Backend type checking

The backend uses Mypy.

A **type checker** tries to catch mismatched data before the program runs.

Example:

If a function expects a number but another part of the program sends a list of text values, a type checker may catch that earlier.

## 3.4 Backend automated tests

Pytest is used for Python tests.

## 3.5 Frontend linting and type checking

The frontend uses ESLint and TypeScript checks.

## 3.6 Frontend unit-testing setup

The project added Vitest and Testing Library.

These tools make it possible to test React components and frontend behavior automatically.

## 3.7 Optional OpenAI provider dependency

The default project can run without paying for AI requests.

A real OpenAI package can be installed as an optional dependency.

This preserves two modes:

- predictable free mock mode;
- real model mode when intentionally configured.

## 3.8 V2 smoke script

The repository includes `scripts/v2_api_smoke.py` and runs it in CI.

### V2 assessment

**Status: built and demo complete.**

---

# 4. V3 — Reliability Platform

V3 asked:

> How do we know whether the AI answer was actually good?

This is one of the most important stages of the project.

A support AI should not be judged only on whether it responds quickly or sounds natural.

## 4.1 Hallucination-risk measurement

A **hallucination** is unsupported or invented AI content.

ResolveOps computes a deterministic quality signal intended to indicate hallucination risk.

The current approach is useful for predictable testing, but it should not be confused with a perfect truth detector.

## 4.2 Citation coverage

Citation coverage measures how much of the generated answer appears connected to supporting evidence.

## 4.3 Retrieval precision

Retrieval precision asks whether the search stage retrieved material that was actually relevant.

## 4.4 Answer completeness

Answer completeness estimates whether the answer addressed the important parts of the question.

## 4.5 Latency percentiles

ResolveOps tracks p50, p95, and p99 latency.

**Latency** means response time.

Simple explanation:

- p50 tells us about the middle request;
- p95 highlights slow requests experienced by roughly the slowest 5%;
- p99 highlights very slow edge cases.

## 4.6 Cost tracking

The system tracks estimated AI cost by provider/model.

This becomes important if a support operation processes many conversations.

A technically impressive AI feature can still be a bad product if it costs more than the human work it is supposed to save.

## 4.7 Quality by product area

ResolveOps can compare quality across areas such as billing, authentication, or another product category.

That helps answer questions like:

> “Why is the AI strong on account setup but weak on billing?”

## 4.8 Failed-query review queue

Queries with low confidence, poor citations, or negative feedback can be surfaced for review.

This creates an operational process for learning from failures.

## 4.9 Human feedback

Users can label answers with feedback such as:

- helpful;
- not helpful;
- wrong citation.

## 4.10 Failed-query actions

The system supports actions such as marking failed queries reviewed/ignored and promoting a failed query into an evaluation set.

That is an important feedback-loop capability.

## 4.11 Regression comparison

ResolveOps can compare configurations.

A **regression** means a change caused something to become worse.

This allows a team to ask:

> “Did the new retrieval settings actually improve quality?”

rather than relying on intuition.

## 4.12 Reliability frontend

The frontend contains a dedicated Reliability page.

It includes metric explanations so users do not have to know the technical meaning of every quality score.

## 4.13 V3 automated validation

The repository includes `scripts/v3_api_smoke.py` and runs it in CI.

### V3 assessment

**Status: built and demo complete.**

The next step is a richer evaluation laboratory with more realistic scenarios and human-calibrated scoring.

---

# 5. V4 — Workflow Integration

V4 moved the project toward how a real support organization operates.

## 5.1 Connector abstraction

A **connector** is a component that imports or exchanges data with another service.

ResolveOps contains connector support for:

- Zendesk;
- Freshdesk;
- Intercom.

The current provider sources are deterministic mocks.

That means the software architecture for connectors is built, but the project is not yet authenticating to real client Zendesk/Freshdesk/Intercom accounts.

## 5.2 Incremental synchronization

The system tracks a cursor so a later sync can import only new information.

A **cursor** is a marker showing where the previous synchronization stopped.

## 5.3 Scheduled ingestion jobs

The system can record recurring ingestion jobs and run jobs that are due.

The scheduling model exists, but the project does not yet have a full always-running production worker/scheduler process.

## 5.4 Semantic duplicate detection

ResolveOps can identify tickets that appear to represent the same issue based on meaning rather than exact text.

## 5.5 Live ticket assist

The Assist feature can produce:

- suggested response;
- escalation recommendation;
- customer-facing text;
- internal note;
- citations;
- customer-tier guidance.

The decision can include:

- answer;
- ask clarification;
- route to human.

## 5.6 Knowledge-base generation

Resolved tickets can be used to create knowledge-base material.

A **knowledge base** is a collection of help information such as troubleshooting steps, policies, and common resolutions.

## 5.7 SLA risk

**SLA** stands for **service-level agreement**.

It represents promised service targets such as response or resolution times.

ResolveOps can identify open tickets that are at risk of missing those targets.

## 5.8 V4 frontend pages

The product includes pages for:

- Connectors;
- Assist;
- Knowledge Base;
- SLA Risk.

## 5.9 V4 automated validation

The repository includes `scripts/v4_api_smoke.py` and runs it in CI.

### V4 assessment

**Status: built for demo use.**

**Not complete as a real integration product until live vendor APIs, credentials, retries, webhooks, and production scheduling are implemented.**

---

# 6. V5 — Enterprise Governance and Data Isolation

V5 introduced user identity, organizational boundaries, auditing, settings, and security-related controls.

## 6.1 User registration and login

The application supports user registration and login.

The first user can become an administrator.

## 6.2 Access tokens

After login, the system issues a signed access token.

An **access token** is a temporary digital credential used to prove that a request belongs to an authenticated user.

## 6.3 Roles

ResolveOps has role concepts such as:

- admin;
- member;
- viewer.

This is a form of **role-based access control**, often shortened to **RBAC**.

Plain-English meaning:

Different categories of users receive different permissions.

## 6.4 Workspaces

A workspace separates organizational data.

The later V5 completion work added workspace references to major product records and filtered queries by workspace.

This is one of the most important security changes in the codebase.

## 6.5 Workspace membership

The application stores which users belong to which workspaces and supports workspace-level roles.

## 6.6 Core endpoint authentication

The V5 completion work added authentication dependencies across core routes including tickets, RAG, dashboards, evaluation, connectors, knowledge, SLA, assistance, PII, and reliability.

This is important because older README wording describing some demo endpoints as open became stale after this work.

## 6.7 Audit logs

The system records important governance events.

An **audit log** is a history that helps answer who changed what and when.

## 6.8 PII detection

The system can identify common forms of personally identifiable information such as:

- email;
- phone;
- Social Security number patterns;
- payment-card-like number patterns;
- IP address.

## 6.9 PII redaction during CSV upload

The V5 completion work connected PII redaction to ingestion when the setting is enabled.

This is better than storing raw sensitive information first and attempting to clean it later.

## 6.10 Data retention

ResolveOps supports retention settings.

A **retention policy** determines how long information should be stored.

The application can preview and execute retention cleanup.

## 6.11 pgvector support

The system can use PostgreSQL plus the `pgvector` extension for embedding similarity search.

If that setup is unavailable, it can fall back to in-memory similarity calculation.

## 6.12 Background job records

ResolveOps supports a background job queue model with handlers for operations such as:

- embedding backfill;
- retention;
- PII redaction;
- connector synchronization.

The important limitation is that this is still application-managed processing rather than a mature external worker system.

## 6.13 Runtime model/provider settings

The product has settings for changing AI-provider/model behavior without rewriting application code.

## 6.14 Prompt versioning

A **prompt** is the instruction text supplied to an AI model.

ResolveOps can store prompt versions and activate one version.

This matters because prompt changes can change AI behavior.

## 6.15 Cloud deployment configuration

The repository contains a Render blueprint that can provision the backend, frontend, and database.

### V5 assessment

**Status: application-level enterprise foundations are built.**

**Not equivalent to a fully audited enterprise deployment.**

Missing production items still include SSO, MFA, backup/restore proof, production monitoring, security testing, secrets management, and high-availability operations.

---

# 7. V6 — Customer-Facing AI Support Agent

V6 was a major product expansion.

Before V6, much of ResolveOps focused on internal support intelligence.

V6 allowed the customer to interact with ResolveOps directly.

## 7.1 Customer profile model

The backend stores customer profiles.

A profile can be associated with conversations and customer-related support history.

## 7.2 Conversation model

The product stores customer conversations rather than treating every question as an isolated request.

## 7.3 Conversation messages

Individual customer, AI, and human messages can be stored in the conversation history.

## 7.4 Human handoff model

The product records when a conversation needs a human.

A handoff can be acknowledged and resolved.

## 7.5 Resolution outcome

The system records how a conversation ended.

This matters because product success should be measured by resolution, not merely by number of AI replies.

## 7.6 Widget API

The customer-facing widget has endpoints for:

- health;
- session start;
- chat;
- feedback.

## 7.7 Widget authentication key

The public widget uses an `X-Widget-Key` mechanism.

This provides a basic boundary between public widget traffic and authenticated internal APIs.

## 7.8 RAG inside the widget

The widget integrates with the evidence-backed answer pipeline rather than acting as an unrelated chatbot.

## 7.9 Sentiment detection

The widget service includes sentiment-related logic.

**Sentiment** means an estimate of the emotional tone of a message.

It can help identify cases where escalation may be appropriate.

## 7.10 Escalation logic

The system can use conversation signals to decide when a human should become involved.

## 7.11 Conversation administration APIs

Authenticated support users can:

- list conversations;
- inspect conversation detail;
- reply;
- resolve;
- manage handoffs;
- inspect customers.

## 7.12 Embeddable frontend widget

The repository contains:

- `widget.js`;
- `widget.html`;
- a React host page.

The JavaScript implementation uses browser isolation techniques so the widget can be embedded without depending completely on the host website’s styles.

## 7.13 V6 support frontend

The frontend includes:

- Conversations page;
- Conversation Detail page;
- Customers page;
- Customer Profile page;
- Handoffs page;
- Widget Host.

## 7.14 V6 test evidence

The V6 merged work reported 29 new tests and 165 total backend tests at that point.

### V6 assessment

**Status: built for demo and controlled internal testing.**

Before broad public use, add stronger widget abuse protection, real-time updates, domain restrictions, accessibility validation, and production monitoring.

---

# 8. V7 — Action-Taking Agent Workflows

V7 gave the AI a controlled way to request actions.

This changed the product from:

> “Here is what I think you should do.”

into something closer to:

> “I can perform this approved action through a registered tool.”

## 8.1 Tool model

The database stores tools.

A tool represents an operation the agent may use.

## 8.2 Tool execution model

The system stores each execution attempt.

## 8.3 Action log

Actions are recorded for review and auditing.

## 8.4 Built-in mock tools

The current registry includes six development-safe tools:

1. create ticket;
2. update ticket status;
3. look up customer;
4. search knowledge base;
5. check SLA status;
6. list handoffs.

These are intentionally mock-oriented rather than unrestricted production actions.

## 8.5 Parameter validation

Before execution, tool input is checked against the expected structure.

This reduces accidental malformed actions.

## 8.6 Sandboxed handler design

Tool logic is routed through controlled handlers rather than allowing the model to execute arbitrary code.

This is an important safety direction.

## 8.7 Latency tracking

Tool execution time is recorded.

## 8.8 Tool APIs

The application supports:

- list tools;
- get tool detail;
- enable/disable tool;
- execute tool;
- list executions;
- list action logs.

## 8.9 Widget tool intent

The widget can recognize some action-oriented language and map it to a registered tool.

Example:

> “Create a ticket for this problem.”

## 8.10 V7 frontend

The frontend includes:

- Tools page;
- Tool Detail page;
- Action Logs page.

## 8.11 V7 test evidence

The merged V7 work reported 15 new tests and 180 total tests at that stage.

### V7 assessment

**Status: built as an action-framework demo.**

Before real refunds, account changes, cancellations, or other high-impact operations, the project still needs approval gates, per-tool authorization, risk classification, idempotency, dry-run mode, rollback strategy, and real external connectors.

---

# 9. V8 — Agent Intelligence and Feedback Loop

V8 added analysis based on what happened in customer conversations.

## 9.1 Conversation summaries

The system can store summaries of completed conversations.

This helps a human understand a long interaction quickly.

## 9.2 Performance metrics

The intelligence service tracks concepts such as:

- containment rate;
- resolution time;
- tool success rate;
- sentiment distribution;
- escalation reasons.

**Containment rate** means the percentage of conversations resolved without a human taking over.

## 9.3 Knowledge-base suggestions

The system can detect conversation patterns and create suggestions for new knowledge content.

This begins moving ResolveOps from reactive answering toward knowledge improvement.

## 9.4 Copilot suggestions

The system can suggest helpful information to human support agents.

Examples include:

- pending handoff guidance;
- canned response opportunities;
- related tickets;
- escalation tips.

## 9.5 Feedback summaries

ResolveOps can aggregate support feedback and surface areas that need improvement.

## 9.6 Intelligence API

The backend exposes intelligence endpoints for:

- performance;
- summaries;
- knowledge suggestions;
- copilot;
- feedback summaries.

## 9.7 V8 frontend

The frontend includes:

- Intelligence page;
- dedicated Copilot page.

## 9.8 V8 test evidence

The merged work reported 191 total backend tests passing at that stage.

### V8 assessment

**Status: built for demo/portfolio use.**

The next maturity step is a formal AI evaluation laboratory and deeper product intelligence.

---

# 10. V9 — Workflow Automation and Self-Service Portal

V9 added tools that support teams use repeatedly.

## 10.1 Routing rules

A routing rule is an “if this, then that” instruction.

Examples:

```text
If product area is Billing -> set priority to High
```

or

```text
If sentiment is strongly negative -> send to senior support
```

The current system supports conditions based on information such as:

- product area;
- sentiment;
- channel;
- status.

Actions can change values such as:

- priority;
- product area;
- status.

## 10.2 Rule priority

Rules can be ordered by priority.

## 10.3 Enable/disable rules

A rule can be turned off without deleting it.

## 10.4 Canned responses

ResolveOps supports pre-written responses for common situations.

The system includes:

- categories;
- shortcuts;
- search;
- usage tracking;
- create/read/update/delete management.

## 10.5 Portal articles

ResolveOps includes self-service article records.

The portal supports:

- readable URL slug;
- draft/published state;
- category;
- product area;
- tags;
- view count;
- helpful count.

A **slug** is a readable piece of a web address, for example:

```text
/help/reset-your-password
```

## 10.6 Ticket status lookup

The portal service includes ticket status lookup using ticket ID and customer email.

## 10.7 V9 frontend

The frontend contains:

- Routing page;
- Canned Responses page;
- Portal page.

## 10.8 V9 test evidence

The merged V9 implementation reported 207 total tests passing.

### V9 assessment

**Status: built for demo/portfolio use.**

A production support team would benefit from a visual rule builder, workflow versioning, conflict detection, simulation, and stronger customer-facing portal hardening.

---

# 11. V10a — Analytics & Reporting + Advanced Security

V10a added two important groups of capabilities:

1. management visibility;
2. stronger access/security controls.

---

## 11.1 Analytics time ranges

The analytics dashboard supports periods such as:

- 7 days;
- 30 days;
- 90 days;
- all time.

## 11.2 Analytics metrics

The system can report values such as:

- conversation count;
- resolved count;
- containment rate;
- average confidence;
- open conversations;
- RAG query volume;
- tool executions;
- SLA breaches.

## 11.3 Trend visualization

The frontend can show daily conversation trend data.

## 11.4 Agent performance

The analytics service includes per-agent measures such as:

- conversations handled;
- resolutions;
- average resolution time;
- satisfaction.

These measures should be interpreted carefully.

A support agent handling complex escalations may have slower resolution time than someone handling simple questions. The product should not encourage simplistic employee ranking without context.

## 11.5 Saved reports

Users can create saved report configurations.

Report types include areas such as:

- quality;
- retrieval;
- cost;
- agent performance;
- SLA.

## 11.6 Export jobs

The system can create CSV exports and track export history.

## 11.7 API-key management

ResolveOps supports software credentials called API keys.

The implementation includes:

- user/workspace ownership;
- scopes;
- expiration;
- last-used tracking;
- disable/revoke;
- hashed storage.

## 11.8 Rate limiting

The application includes request-rate controls.

A **rate limit** restricts how many requests are allowed during a period.

This helps reduce abuse and accidental overload.

## 11.9 Rate-limit logging

Rate-limit events can be recorded in the database.

## 11.10 Login-attempt tracking

The application records login attempts.

This is a foundation for detecting password guessing.

## 11.11 Brute-force protection settings

**Brute force** means repeatedly trying passwords in the hope that one works.

ResolveOps includes configurable maximum attempts and lockout duration.

## 11.12 IP allowlisting

A workspace can define approved IP addresses and enable enforcement.

An **IP address** identifies a network location.

An **allowlist** is a list of values that are permitted.

## 11.13 Security middleware

The application adds request-level middleware for:

- rate limiting;
- IP allowlisting.

**Middleware** is code that checks a request before it reaches the main business operation.

## 11.14 Security frontend

The frontend has a Security page with areas for:

- API keys;
- rate limits;
- login security;
- IP allowlist.

## 11.15 Analytics and reports frontend

The frontend includes:

- Analytics page;
- Reports page.

## 11.16 V10a test evidence

The merged V10a implementation reported:

- 22 new tests;
- 229 total backend tests passing;
- TypeScript checks passing;
- ESLint clean.

### V10a assessment

**Status: built for demo/portfolio use with useful paid-pilot foundations.**

Production hardening is still required, especially for distributed rate limiting, stronger identity management, end-to-end validation, secrets, monitoring, and recovery.

---

# 12. Current frontend surface

The application currently exposes a broad set of pages.

These include:

- Dashboard;
- Upload;
- Tickets;
- Ticket Detail;
- RAG Playground;
- Reliability;
- Evaluation;
- Connectors;
- Assist;
- Knowledge Base;
- SLA Risk;
- Conversations;
- Conversation Detail;
- Customers;
- Customer Profile;
- Handoffs;
- Tools;
- Tool Detail;
- Action Logs;
- Intelligence;
- Copilot;
- Routing;
- Canned Responses;
- Portal;
- Analytics;
- Reports;
- Security;
- Widget;
- Account;
- Workspaces;
- Prompts;
- Jobs;
- PII;
- Settings;
- Audit.

This page list is important because it shows how much broader the current product is than the older README description.

---

# 13. Current backend capability areas

The FastAPI application currently mounts route groups for:

- health;
- tickets;
- RAG;
- dashboard;
- evaluation;
- reliability;
- connectors;
- assist;
- knowledge base;
- SLA;
- authentication;
- workspaces;
- audit;
- settings;
- retention;
- PII;
- prompts;
- jobs;
- widget;
- conversations;
- tools;
- intelligence;
- workflow;
- analytics;
- security.

An **API route** is an operation the frontend or another application can call.

---

# 14. Current database capability groups

The database stores information across several domains.

## Support knowledge

- tickets;
- chunks;
- ingestion batches.

## AI and evaluation

- RAG queries;
- saved evaluation questions;
- evaluation runs;
- quality information.

## Workflow integration

- connectors;
- ingestion jobs;
- knowledge-base articles.

## Enterprise/governance

- users;
- workspaces;
- memberships;
- audit logs;
- settings;
- prompt templates;
- background jobs.

## Customer support

- customer profiles;
- conversations;
- messages;
- handoffs;
- resolution outcomes.

## Agent actions

- tools;
- tool executions;
- action logs.

## Intelligence

- conversation summaries;
- knowledge suggestions;
- copilot suggestions.

## Workflow automation

- routing rules;
- canned responses;
- portal articles.

## Analytics and security

- saved reports;
- export jobs;
- API keys;
- login attempts;
- IP allowlists;
- security settings;
- rate-limit logs.

---

# 15. Current technology stack

## Backend

- Python 3.11+;
- FastAPI;
- Uvicorn;
- Pydantic;
- SQLAlchemy;
- PostgreSQL;
- Psycopg;
- Alembic;
- optional OpenAI package;
- Pytest;
- Ruff;
- Mypy.

## Frontend

- React;
- TypeScript;
- React Router;
- Recharts;
- Vite;
- Vitest;
- Testing Library;
- ESLint.

## Local/deployment

- Docker;
- Docker Compose;
- GitHub Actions;
- Render blueprint.

---

# 16. What is well designed in the current system

## 16.1 The project started with evidence, not automation power

This was a strong decision.

Before giving the AI tools, the project first built retrieval, citations, fallback, and quality tracking.

## 16.2 Mock-first development

The project can run with predictable mock providers.

This keeps testing inexpensive and repeatable.

## 16.3 Quality is first-class

The project has a dedicated reliability layer rather than treating AI correctness as a vague feeling.

## 16.4 Human handoff is built into the product

The project does not assume 100% automation is always desirable.

## 16.5 Actions are logged

The action framework includes execution records.

## 16.6 Workspace isolation exists

The code recognizes that different companies must not share data accidentally.

## 16.7 Security evolved with product power

Later versions added authentication, roles, PII handling, rate limiting, login protection, and API-key management.

---

# 17. What “built” does not mean

The following statement would be inaccurate:

> “ResolveOps has 229 tests and V10a, therefore it is ready to replace an enterprise support platform tomorrow.”

Why?

Because production software needs more than features and unit tests.

A real client also needs:

- real integrations;
- verified deployment;
- backups;
- recovery;
- monitoring;
- incident response;
- strong identity/security;
- end-to-end tests;
- support procedures;
- safe action approvals;
- data handling agreements;
- predictable operations.

That missing work is documented separately in [`02_WHAT_IS_MISSING.md`](./02_WHAT_IS_MISSING.md).

---

# 18. Summary

ResolveOps has already built the foundations of a broad AI support platform.

The project can currently demonstrate the following complete story:

1. ingest support history;
2. validate and structure it;
3. search it by meaning;
4. answer questions with citations;
5. refuse unsupported answers;
6. measure AI reliability;
7. review failed answers;
8. draft responses for support agents;
9. generate knowledge articles;
10. monitor SLA risk;
11. authenticate users;
12. separate workspace data;
13. protect personal data;
14. record audits;
15. manage prompts/settings;
16. talk directly to customers through a widget;
17. preserve conversation history;
18. escalate to humans;
19. execute controlled mock tools;
20. record tool actions;
21. generate intelligence and copilot suggestions;
22. route work;
23. manage canned responses;
24. publish self-service content;
25. show analytics;
26. save/export reports;
27. manage API keys;
28. rate-limit requests;
29. track suspicious login activity;
30. restrict access by IP when configured.

That is significant progress.

The next job is not to pretend every item above is production complete. The next job is to close the gap between **built** and **dependable**.

Read [`02_WHAT_IS_MISSING.md`](./02_WHAT_IS_MISSING.md) next.
