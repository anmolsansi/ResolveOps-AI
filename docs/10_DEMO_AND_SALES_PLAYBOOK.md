# ResolveOps AI — Demo and Sales Playbook

## Purpose of this document

This file explains how to show ResolveOps AI to a potential client without confusing them with technical details or overselling unfinished capabilities.

The goal of a demo is not to prove that ResolveOps has many pages.

The goal is to make the prospect understand:

1. the support problem;
2. how ResolveOps helps;
3. why the AI is safer than a generic chatbot;
4. what the human support team remains responsible for;
5. what a paid pilot would look like;
6. what measurable business outcome the client can expect to test.

A good demo tells one story from beginning to end.

---

# 1. The main sales message

Use language a support manager understands.

Recommended positioning:

> **ResolveOps helps support teams reuse what they already know. It turns historical support conversations into searchable evidence, drafts cited answers, identifies weak AI responses, and hands uncertain cases to humans instead of pretending to know. As quality is proven, the same platform can safely automate more support work.**

Avoid opening with:

- RAG;
- vector embeddings;
- pgvector;
- autonomous agent architecture;
- FastAPI;
- multi-tenant middleware.

Those details can be explained if the prospect asks.

---

# 2. Who should see the demo

Different people care about different parts.

## Support leader

Cares about:

- response time;
- resolution time;
- agent productivity;
- quality;
- customer satisfaction;
- backlog;
- staffing pressure.

## Support agent

Cares about:

- faster search;
- less repetitive writing;
- better context;
- fewer manual steps.

## Founder/CEO

Cares about:

- cost;
- customer experience;
- growth without equal headcount growth;
- differentiation;
- implementation risk.

## CTO/engineering leader

Cares about:

- integration;
- security;
- architecture;
- data isolation;
- reliability;
- maintenance.

## Security/IT

Cares about:

- identity;
- permissions;
- sensitive data;
- audit;
- API keys;
- network restrictions;
- incident handling.

Do not give exactly the same demo to every audience.

---

# 3. Five-minute demo structure

A short demo should tell one complete story.

## Minute 0–1: problem

Say:

> “Your support team already solved many of the questions customers will ask tomorrow, but those answers are buried across old tickets and help content. ResolveOps helps the team reuse that knowledge and measure whether AI answers are actually supported.”

## Minute 1–2: ask a known question

Open RAG/search experience.

Ask a realistic question such as:

> “How should we handle a duplicate billing charge?”

Show:

- answer;
- supporting citations;
- confidence/quality.

Do not spend time explaining the mathematics of embeddings.

Say:

> “The important part is that the answer is based on your support knowledge and shows the evidence.”

## Minute 2–3: ask an unknown question

Ask something outside the support knowledge.

Show fallback.

Say:

> “A useful support AI should know when the evidence is not strong enough. ResolveOps is designed to fall back rather than invent an answer.”

## Minute 3–4: show human handoff

Open customer conversation/handoff flow.

Explain:

> “When the AI should not continue, the human receives the transcript, customer context, evidence, and reason for escalation.”

## Minute 4–5: show reliability

Open Reliability/Analytics.

Show:

- failed queries;
- feedback;
- quality trends;
- containment or handoff;
- cost.

Finish:

> “The goal is not just to automate. The goal is to know what is working, what is failing, and where humans should stay involved.”

---

# 4. Fifteen-minute demo structure

## Scene 1 — Data ingestion

Show sample support data import.

Explain:

- validation;
- invalid rows;
- duplicates;
- PII redaction setting.

Say:

> “We do not blindly feed everything to the AI. Data quality is checked first.”

## Scene 2 — Evidence-backed answer

Ask a known support question.

Show citations.

## Scene 3 — Safe failure

Ask an unsupported question.

Show fallback.

## Scene 4 — Support-agent assist

Show a live ticket/conversation and AI suggested response.

Explain difference between:

- customer-facing response;
- internal note.

## Scene 5 — Customer widget

Open the embeddable widget.

Start a conversation.

## Scene 6 — Handoff

Trigger a case where the AI should escalate.

Open the internal Handoffs page.

Show that the human sees the conversation history.

## Scene 7 — Tool/action

Use a safe mock action such as creating a ticket or checking SLA status.

Show action log.

Say clearly:

> “For production, high-impact actions such as refunds would have separate permissions and approval gates. We do not recommend turning them on autonomously in an early pilot.”

## Scene 8 — Intelligence

Show:

- conversation summary;
- performance;
- knowledge suggestion;
- copilot suggestion.

## Scene 9 — Workflow

Show:

- routing rule;
- canned response;
- self-service portal.

## Scene 10 — Analytics/security

Show:

- analytics;
- reports;
- API keys;
- rate limiting;
- login security;
- IP allowlist;
- audit.

Finish with paid-pilot scope rather than another feature page.

---

# 5. The best demo story

Use one fictional but realistic customer journey consistently.

Example company: a SaaS subscription business.

Customer:

> “I upgraded yesterday but I still cannot access Pro features.”

Then demonstrate:

1. customer sends message;
2. ResolveOps retrieves previous upgrade cases;
3. answer is drafted with evidence;
4. confidence is insufficient for account-changing action;
5. human handoff occurs;
6. agent sees customer history;
7. agent uses safe lookup/create-ticket tool;
8. resolution is recorded;
9. analytics updates;
10. repeated similar cases become a knowledge/product signal.

One story is easier to understand than 30 unrelated screenshots.

---

# 6. Questions to ask before showing the product

A demo is more effective when tied to the prospect’s real pain.

Ask:

- How many support agents do you have?
- What helpdesk do you use?
- How many conversations per month?
- What are the top five repeated questions?
- Where do agents search for answers today?
- How long does it take a new agent to become productive?
- Which support work requires senior people?
- Which actions should never be automated?
- What is your biggest support bottleneck?

Then shape the demo around the answers.

---

# 7. What not to say

Do not say:

> “ResolveOps never hallucinates.”

Say:

> “ResolveOps is designed to reduce and detect unsupported answers using company knowledge, citations, confidence, failed-query review, and human handoff.”

---

Do not say:

> “It is fully enterprise ready.”

Say:

> “The platform has enterprise-style foundations such as workspaces, roles, auditing, PII redaction, API keys, rate limits, and IP controls. We still complete a client-specific production-readiness checklist before live deployment.”

---

Do not say:

> “We integrate with Zendesk, Freshdesk, and Intercom today.”

if the live production connectors are not built.

Say:

> “The connector architecture and simulated providers exist. For a paid pilot, we either start from an export or implement and validate the specific live connector the client actually uses.”

---

Do not say:

> “We can automate all your support.”

Say:

> “We start with the categories where automation can be measured safely, keep humans involved for uncertainty and high-impact actions, and expand based on real results.”

---

# 8. Explain RAG without using the term first

Say:

> “Before the AI writes an answer, ResolveOps searches the company’s own support knowledge and gives the AI the most relevant evidence. The answer then includes references so the team can check where it came from.”

If the prospect is technical, add:

> “That pattern is commonly called Retrieval-Augmented Generation, or RAG.”

This order helps non-technical buyers understand the value before hearing the acronym.

---

# 9. Explain embeddings without mathematics

Say:

> “Instead of only matching exact words, ResolveOps can search for similar meaning. For example, ‘charged twice’ and ‘duplicate payment’ can be recognized as related even though the wording is different.”

If the technical buyer asks how:

> “The text is converted into numerical meaning representations called embeddings and compared for similarity.”

---

# 10. Explain human handoff as a positive feature

Do not apologize for handoff.

Say:

> “We intentionally design a human route for uncertain or high-risk situations. The goal is correct resolution, not maximum automation at any cost.”

This is a trust message.

---

# 11. Explain action tools carefully

Say:

> “ResolveOps has a controlled tool framework. The AI can request approved operations, and the system records executions. For a client deployment, every real tool receives a risk level, permission rules, and approval requirements.”

Do not demonstrate a fake refund and imply real payments are already integrated.

---

# 12. Common objection: “We already have Zendesk/Intercom/Freshdesk”

Recommended answer:

> “That is fine. Our initial goal is not to force a helpdesk migration. ResolveOps can begin as an intelligence and AI-quality layer beside your existing support workflow. We start with your historical support knowledge and agent assistance, then connect more deeply where the business case is proven.”

This avoids competing on every mature helpdesk feature.

---

# 13. Common objection: “We can just use ChatGPT”

Answer:

> “A general AI chat tool can be useful, but ResolveOps is designed around support operations: workspace-specific knowledge, citations, failed-query review, customer conversations, handoff, action logs, SLA risk, knowledge suggestions, support analytics, and administrative controls. The value is the support workflow and measurement around the model, not only access to a model.”

---

# 14. Common objection: “How accurate is it?”

Do not give a universal percentage without evidence.

Answer:

> “Accuracy depends on your support knowledge and question mix. That is why our pilot begins by building an evaluation set from your real support questions. We measure answer quality, citations, fallback, and escalation before wider rollout.”

This converts the objection into part of the pilot methodology.

---

# 15. Common objection: “What if the AI says something wrong?”

Answer:

> “We assume mistakes are possible. ResolveOps is built around evidence retrieval, citations, confidence/fallback, failed-answer review, human handoff, and audit. During an early pilot, customer replies can remain human-reviewed until the measured quality is strong enough for selected categories.”

---

# 16. Common objection: “What about our sensitive customer data?”

Answer:

> “ResolveOps has workspace isolation, roles, PII detection/redaction, retention controls, audit logs, API-key controls, rate limiting, and IP allowlisting foundations. Before accepting production data we agree the exact fields, minimize what is imported, configure retention/redaction, validate isolation, and complete the deployment security checklist.”

Do not claim industry-specific compliance unless it has been formally addressed.

---

# 17. Common objection: “Can you support healthcare?”

Recommended answer:

> “ResolveOps is currently a general customer-support platform. If the use case includes regulated health information or medical decision support, we would perform a separate healthcare-readiness review before accepting that data or making compliance claims.”

This is safer than pretending generic PII controls equal healthcare compliance.

---

# 18. Common objection: “How much does it cost?”

Do not begin with a giant enterprise price sheet.

Say:

> “We start with a paid pilot because the first goal is to prove value on your data. Pricing depends on team size, data volume, integration work, and how much managed implementation is required. For a small support team, the pilot is normally structured as a one-time setup plus a monthly managed fee.”

Then provide the relevant range from the commercial plan.

---

# 19. Recommended pilot proposal structure

## Section 1 — Current problem

Write the client’s own problem.

Example:

> Agents spend too much time searching historical tickets and escalating common questions to senior support.

## Section 2 — Pilot objective

> Reduce time spent searching and improve consistency of support drafts using evidence from historical tickets.

## Section 3 — Scope

- ticket import;
- internal AI search;
- cited drafts;
- quality monitoring;
- weekly review.

## Section 4 — Exclusions

- high-risk autonomous actions;
- unsupported channels;
- unbuilt integrations;
- regulated use cases.

## Section 5 — Success metrics

Example:

- 50%+ draft acceptance;
- measurable reduction in search time;
- no critical data-isolation failure;
- agreed quality threshold on evaluation set.

Do not choose arbitrary thresholds without client agreement.

## Section 6 — Timeline

Use phases and quality gates.

## Section 7 — Price

Setup + recurring pilot fee.

## Section 8 — Next step

If successful, convert into recurring deployment and expand scope.

---

# 20. Demo preparation checklist

Before every client demo:

- [ ] Start from a clean known-good environment.
- [ ] Confirm backend health.
- [ ] Confirm frontend loads.
- [ ] Confirm sample login works.
- [ ] Confirm sample data exists.
- [ ] Test known RAG question.
- [ ] Test fallback question.
- [ ] Test widget.
- [ ] Test handoff.
- [ ] Test safe tool.
- [ ] Test analytics pages.
- [ ] Remove real customer secrets from demo environment.
- [ ] Disable any unfinished risky action.
- [ ] Prepare backup screenshots/video in case internet/demo environment fails.

Never discover a broken migration during the sales call.

---

# 21. Technical-buyer appendix for the demo

If a CTO asks, be ready to explain:

## Backend

- Python/FastAPI;
- SQLAlchemy/PostgreSQL;
- Alembic migrations;
- provider abstraction;
- RAG/retrieval services;
- workspace-scoped queries.

## Frontend

- React/TypeScript;
- routed administration/support pages;
- widget delivery.

## Testing

- backend unit/integration tests;
- frontend unit tests;
- CI;
- Docker smoke tests through V4;
- planned later-version E2E hardening.

Be transparent that later-version smoke expansion is in the immediate roadmap.

---

# 22. Security-buyer appendix

Be ready to show:

- user roles;
- workspace isolation model;
- PII redaction;
- retention;
- audit;
- API keys;
- rate limits;
- login protection;
- IP allowlist.

Also be ready to say what is not yet complete:

- SSO/MFA;
- formal certification;
- advanced prompt-injection layer;
- full production DR proof until V10b is complete.

A security buyer respects a clear gap list more than vague confidence.

---

# 23. After the demo

Send a short follow-up containing:

1. the support problem you heard;
2. proposed pilot scope;
3. data required;
4. success metrics;
5. timeline/phases;
6. price;
7. exclusions;
8. next meeting.

Do not send 40 pages of architecture unless requested.

The long documentation is available for due diligence, but the sales next step should be easy to understand.

---

# 24. Demo metrics that create credibility

Once real pilots exist, include measured examples such as:

- average agent search time before/after;
- draft acceptance rate;
- number of repeated questions identified;
- knowledge gaps found;
- handoff rate;
- customer satisfaction;
- AI cost per resolved conversation.

Use actual measured client-approved values.

Do not manufacture marketing numbers.

---

# 25. First sales case study format

## Client

Describe company anonymously if needed.

## Problem

Example:

> Eight support agents spent significant time searching old tickets for repeated technical issues.

## Pilot

- historical ticket import;
- internal cited search;
- draft assistance;
- weekly quality review.

## Result

Use measured data.

## What changed

Explain what support agents did differently.

## Expansion

Describe next feature added after proof.

---

# 26. The close

The best close is not:

> “Do you want to buy ResolveOps?”

It is:

> “Based on what you described, the best first use case is reducing the time your agents spend searching past tickets. We can run a controlled pilot on an export of your historical cases, keep all customer replies human-reviewed initially, and measure whether it improves response time and agent efficiency. If the results are strong, we expand from there. Would you like to scope that pilot?”

That gives the prospect a small, concrete next step.

---

# 27. Final sales principle

A good ResolveOps demo should make the prospect think:

> “This team understands that support AI can fail, has designed ways to measure and contain that failure, and can start without forcing us to replace everything.”

That is a stronger reason to buy than simply showing more AI features.
