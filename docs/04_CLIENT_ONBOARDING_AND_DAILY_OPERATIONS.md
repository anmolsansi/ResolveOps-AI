# ResolveOps AI — Client Onboarding and Daily Operations Guide

## Purpose of this document

This file explains what should happen after a real company agrees to try ResolveOps AI.

The code alone does not onboard a customer.

A real client needs:

- a safe way to give ResolveOps data;
- a clear understanding of what the AI is allowed to do;
- testing before customers are exposed;
- people responsible for failures;
- a daily operating routine;
- a way to improve quality over time;
- a way to leave the product and retrieve/delete data if the relationship ends.

This document is written for both technical and non-technical readers.

---

# 1. The onboarding principle

The first rule is:

> **Do not connect everything, import everything, automate everything, and turn the AI on for every customer on day one.**

A safer onboarding process is gradual.

The recommended sequence is:

```text
Understand the client
        |
        v
Choose a narrow use case
        |
        v
Import limited historical knowledge
        |
        v
Test internally
        |
        v
Human-reviewed draft mode
        |
        v
Small customer audience
        |
        v
Measure quality
        |
        v
Expand only when evidence supports expansion
```

---

# 2. Step 1 — Discovery before any data is imported

The first client meeting should not begin with API keys.

It should begin with understanding how the support team works.

## Questions to ask

### Business

- What does the company sell?
- Who are its customers?
- What are the highest-value customer groups?
- How many support conversations happen per day/week/month?
- How many support agents are there?
- What does an average support case cost in staff time?
- Which problems are most repetitive?

### Current systems

- Which helpdesk is used?
- Zendesk?
- Freshdesk?
- Intercom?
- Email?
- A custom system?
- Where is the knowledge base?
- Where are policies stored?
- Does the support team use Slack, Teams, Jira, Linear, Salesforce, HubSpot, or another system?

### Current workflow

- How does a customer ask for help?
- How is work assigned?
- What creates an urgent ticket?
- When does an agent escalate to a senior person?
- When does support involve engineering?

### Risk

- Which actions may never be automated?
- Which topics must always be handled by a person?
- Does support data contain personal or regulated information?
- Are there contractual data-residency requirements?

### Success

- What would make the pilot clearly valuable?
- Faster first response?
- Lower average resolution time?
- Fewer repetitive tickets?
- Better support-agent search?
- Better self-service?
- Better knowledge quality?

Do not begin implementation until the success measure is clear.

---

# 3. Step 2 — Choose one narrow first use case

A first pilot should solve one or two expensive repetitive problems.

Good examples:

- help support agents find historical solutions;
- draft answers to common product questions;
- answer a limited group of website FAQs;
- identify SLA risk;
- summarize long conversations;
- identify knowledge gaps.

Bad first-pilot scope:

> “Replace the entire support organization with autonomous AI.”

That scope is too broad, too difficult to measure, and too risky.

---

# 4. Step 3 — Decide what data ResolveOps is allowed to receive

Create a data inventory.

A **data inventory** is a simple list of the information entering the system.

Examples:

- support ticket title;
- support ticket body;
- status;
- product area;
- priority;
- customer tier;
- resolution text;
- knowledge articles.

For each field answer:

1. Do we need this field?
2. Is it sensitive?
3. How long should we keep it?
4. Who may access it?

The safest data is data you never collect.

If ResolveOps does not need a customer’s payment-card details to answer a support question, do not import them.

---

# 5. Step 4 — Create the client workspace

A workspace represents the client’s isolated area inside ResolveOps.

For onboarding:

1. create workspace;
2. assign an administrator;
3. add pilot users;
4. verify roles;
5. verify that users cannot access another workspace;
6. configure retention;
7. configure PII redaction;
8. configure provider/model settings;
9. configure prompt version;
10. configure security settings.

Before client data is added, run a basic tenant-isolation test.

**Tenant isolation** means one customer organization cannot access another organization’s data.

---

# 6. Step 5 — Import data safely

For the first client, CSV import may be more practical than immediately building a real helpdesk connector.

That can be sold honestly as a managed onboarding process.

## Recommended import process

### Phase A — Sample

Ask for a small sample, such as 50–200 resolved tickets.

Do not begin with the full history.

### Phase B — Field mapping

Map the client’s fields into ResolveOps fields.

Example:

```text
Client column: issue_category
ResolveOps field: product_area
```

### Phase C — Validation report

Show:

- total rows;
- accepted rows;
- rejected rows;
- duplicates;
- missing required fields;
- PII findings.

### Phase D — Client review

The client confirms the sample is correct.

### Phase E — Larger import

Only after the sample is validated, import the broader historical set.

---

# 7. Step 6 — Build a client-specific evaluation set

Before the AI is used, create a test set from real support questions.

This is one of the most important onboarding activities.

## Select questions from several categories

- easy common question;
- difficult common question;
- ambiguous question;
- question with missing knowledge;
- angry customer wording;
- question that must escalate;
- policy-sensitive question;
- known historical failure.

For each question, have the client define:

- acceptable answer;
- required source/policy;
- whether a human should handle it;
- prohibited content.

This becomes the beginning of a **golden test set**.

A golden test set is a carefully reviewed set of important examples used repeatedly to check quality.

---

# 8. Step 7 — Configure prompts and policies

A **prompt** is the instruction text sent to the AI.

A client-specific prompt may define:

- company tone;
- response style;
- what sources may be used;
- when to refuse;
- when to escalate;
- whether the AI should ask follow-up questions;
- prohibited topics.

Do not hide business policy only inside a prompt.

Important rules should also exist in application logic or a policy layer.

Example:

> “Never issue a refund above $20 without human approval.”

That should not depend solely on the AI remembering a sentence in a prompt.

---

# 9. Step 8 — Internal-only testing

Before any customer sees the AI, support employees should use it.

## Internal test mode

The support team can ask real questions.

Review:

- answer correctness;
- citations;
- fallback behavior;
- tone;
- latency;
- cost;
- incorrect escalation;
- missing knowledge.

Every important failure should become a test case or knowledge task.

This “test before wide deployment” pattern is used by mature AI-support products because it gives the team a chance to find obvious failures before customers do.

---

# 10. Step 9 — Human-reviewed draft mode

This should usually be the first production mode.

Flow:

```text
Customer asks question
       |
       v
ResolveOps finds evidence
       |
       v
ResolveOps drafts answer
       |
       v
Human reviews/edit
       |
       v
Human sends
```

Measure:

- percentage of drafts accepted without change;
- percentage lightly edited;
- percentage rejected;
- most common rejection reason;
- average time saved;
- citation errors.

This creates real evidence about whether ResolveOps is helping.

---

# 11. Step 10 — Small customer-facing rollout

If draft quality is consistently strong, expose ResolveOps directly to a narrow audience.

Examples:

- employees only;
- beta customers;
- 5% of website users;
- only one product category;
- only simple how-to topics.

Do not begin with every customer and every support topic.

## Watch closely

During early rollout, monitor:

- conversation count;
- fallback rate;
- handoff rate;
- customer feedback;
- wrong answers;
- wrong citations;
- unsupported answers;
- unusual costs;
- latency.

---

# 12. Step 11 — Human handoff process

Every client needs an explicit handoff policy.

## Questions to define

- When must the AI hand off?
- Which team receives the handoff?
- What happens outside business hours?
- What if no agent accepts the handoff?
- What customer message is shown while waiting?
- What information does the human receive?

## Recommended handoff package

The agent should receive:

- customer identity;
- conversation transcript;
- AI summary;
- customer sentiment;
- retrieved sources;
- reason for escalation;
- tools/actions already attempted;
- important prior conversations.

A handoff should save the human time, not create more work.

---

# 13. Step 12 — Introduce low-risk tools

After conversational quality is stable, enable tools gradually.

Good first tools:

- search knowledge;
- create ticket;
- check status;
- check SLA;
- look up customer.

Avoid high-impact tools at first.

For every tool define:

- allowed role;
- allowed use case;
- input fields;
- maximum impact;
- approval requirement;
- audit information.

---

# 14. Step 13 — Daily operating routine

A paid pilot should have a daily routine.

## Morning check

Review:

- service health;
- failed jobs;
- connector status;
- pending handoffs;
- SLA risk;
- high error rate;
- unusual AI cost;
- security alerts.

## During the day

Support agents:

- handle handoffs;
- review suggestions;
- flag bad answers;
- use actions;
- resolve conversations.

## End-of-day review

Check:

- failed queries;
- negative feedback;
- high-risk cases;
- unresolved urgent conversations;
- job failures;
- tool failures;
- potential security incidents.

During the first pilot, daily review should be mandatory.

---

# 15. Weekly client review

Schedule a short recurring meeting with the client.

## Agenda

### Outcomes

- conversations handled;
- agent time saved;
- resolution rate;
- handoff rate;
- customer feedback;
- cost.

### Failures

- incorrect answers;
- wrong citations;
- bad routing;
- tool failures;
- knowledge gaps.

### Improvements

- new article needed;
- prompt change;
- workflow change;
- additional category ready for automation.

### Expansion decision

Ask:

> Is there enough evidence to expand the rollout?

Do not expand simply because a calendar week passed.

---

# 16. Monthly business review

For a recurring paid relationship, provide a monthly report.

Include:

- volume trend;
- AI-contained cases;
- human handoffs;
- satisfaction;
- support-agent usage;
- time saved estimate;
- common problems;
- knowledge gaps;
- product issue patterns;
- AI cost;
- incidents;
- changes made;
- next-month plan.

Do not exaggerate ROI.

If the product does not yet have enough evidence to calculate exact money saved, say so.

---

# 17. Incident handling

An **incident** is an event where the product behaves in a way that may harm service, security, data, or customer trust.

Examples:

- wrong workspace data appears;
- AI gives dangerous answer;
- refund executes incorrectly;
- connector imports duplicates;
- data export leaks information;
- service becomes unavailable;
- login attack succeeds.

## Incident process

1. detect;
2. stop/contain;
3. preserve evidence/logs;
4. inform responsible people;
5. restore safe operation;
6. investigate cause;
7. fix;
8. add test preventing repeat;
9. document outcome.

For early pilots, maintain a clear emergency switch that disables customer-facing automation while preserving the human support channel.

---

# 18. Change management

Do not change AI behavior directly in production without testing.

Changes include:

- new prompt;
- new AI model;
- new retrieval threshold;
- new tool;
- new routing rule;
- new knowledge source.

Recommended process:

```text
Draft change
    |
    v
Test against evaluation set
    |
    v
Review failures
    |
    v
Internal/staging test
    |
    v
Small production audience
    |
    v
Measure
    |
    v
Full rollout or rollback
```

---

# 19. Knowledge maintenance

A knowledge base is not a one-time import.

Every week/month review:

- repeated failed questions;
- new product changes;
- outdated policies;
- knowledge suggestions;
- articles with poor outcomes;
- contradictory answers.

Assign an owner to important knowledge.

Example:

```text
Refund policy
Owner: Support Operations
Review date: every 90 days
```

---

# 20. Security administration routine

At a minimum:

## Weekly

- review suspicious login activity;
- review failed API-key usage;
- review administrator changes;
- inspect high-risk action logs.

## Monthly

- review workspace users;
- remove users who no longer need access;
- review API keys;
- rotate credentials where appropriate;
- review retention settings;
- verify backups.

## After staff departure

- disable account;
- revoke sessions;
- revoke personal API keys;
- transfer ownership of critical settings.

---

# 21. Offboarding a client

A sellable product needs a clean exit process.

If a client leaves:

1. disable external integrations;
2. revoke API keys;
3. disable client users;
4. provide agreed data export;
5. confirm retention/deletion schedule;
6. delete data according to contract/policy;
7. preserve only legally/contractually required records;
8. provide deletion confirmation where appropriate.

Do not make client data difficult to retrieve merely to prevent churn.

---

# 22. Roles required for the first paid pilot

A small pilot does not need a large company, but responsibilities must be clear.

## Product/implementation owner

Responsible for:

- client requirements;
- scope;
- weekly review;
- acceptance criteria.

## Technical owner

Responsible for:

- deployment;
- integrations;
- incidents;
- data;
- backups.

## AI quality owner

Responsible for:

- evaluation set;
- failed answers;
- prompts;
- knowledge quality.

## Client support lead

Responsible for:

- human handoff;
- business policy;
- support-agent feedback;
- rollout decision.

One person may fill several roles during an early pilot, but the responsibilities should still be named.

---

# 23. Minimum onboarding checklist for first paid client

- [ ] Signed pilot scope.
- [ ] Named client owner.
- [ ] Named ResolveOps owner.
- [ ] Defined pilot use case.
- [ ] Defined excluded use cases.
- [ ] Data inventory completed.
- [ ] Workspace created.
- [ ] Access roles reviewed.
- [ ] Retention setting agreed.
- [ ] PII handling agreed.
- [ ] Sample data imported.
- [ ] Field mapping reviewed.
- [ ] Import errors reviewed.
- [ ] Golden evaluation set created.
- [ ] Prompt/policies configured.
- [ ] Internal quality test passed.
- [ ] Human handoff workflow tested.
- [ ] Monitoring enabled.
- [ ] Backup configured and restore tested.
- [ ] Incident contact agreed.
- [ ] Initial rollout audience agreed.
- [ ] High-risk autonomous tools disabled.
- [ ] Daily review scheduled.
- [ ] Weekly client review scheduled.

---

# 24. What “successful onboarding” means

Onboarding is not complete because data uploaded successfully.

Onboarding is complete when:

- the client understands what ResolveOps can and cannot do;
- the correct people can access it;
- other people cannot access it;
- source data is accurate enough;
- AI answers pass agreed tests;
- handoff works;
- monitoring works;
- recovery exists;
- the client knows whom to contact;
- the first rollout is intentionally limited.

That is the difference between installing software and delivering a usable service.
