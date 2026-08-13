# ResolveOps AI — Product Overview in Plain English

## Why this document exists

This document explains ResolveOps AI as if the reader has never built software before.

You should be able to give this file to:

- a new intern;
- a school-going student;
- a small-business owner;
- a customer-support manager;
- a salesperson;
- a designer;
- or an engineer joining the project for the first time.

The reader should finish this document understanding:

1. what ResolveOps AI is;
2. which business problems it is trying to solve;
3. who uses it;
4. how the product behaves from start to finish;
5. what role artificial intelligence plays;
6. where humans stay in control;
7. why evidence, safety, permissions, testing, and monitoring matter;
8. and what ResolveOps is trying to become.

Whenever this document uses a technical term, the term is explained in simple language.

---

# 1. ResolveOps AI in one sentence

**ResolveOps AI is a customer-support platform that helps a company learn from its past support cases, answer new customer questions using evidence, help human support agents work faster, safely automate repetitive support tasks, and measure whether the AI and support operation are actually performing well.**

That sentence contains several ideas. The rest of this document explains them one by one.

---

# 2. The business problem

Imagine a company has been operating for five years.

During those five years, customers have asked thousands of questions:

- “Why was I charged twice?”
- “How do I reset my password?”
- “Why is my order delayed?”
- “How do I change my subscription?”
- “Why does this feature not work?”
- “Can I cancel?”
- “Where is my refund?”
- “How do I invite another team member?”

Human support agents answered those questions. The answers are often stored in old tickets, email threads, help-center articles, internal notes, and support tools.

The company therefore has a lot of useful knowledge.

The problem is that the knowledge is difficult to reuse.

A new support agent cannot read 100,000 old tickets before answering a customer.

A senior agent may remember the answer because they have worked there for three years, but a new employee may not.

A manager may not notice that 200 customers are suddenly reporting the same problem until the support queue becomes very large.

An AI chatbot can answer quickly, but a normal AI system can sometimes produce an answer that sounds convincing even when it is wrong.

ResolveOps AI is designed around these problems.

---

# 3. The central idea

The central idea is:

> **Use the company’s own support history and approved knowledge as evidence before generating an answer. If there is not enough evidence, do not pretend to know.**

This is different from simply asking a general-purpose AI model a question.

A normal flow might look like this:

```text
Customer asks a question
        |
        v
AI model guesses an answer from what it learned during training
        |
        v
Customer receives the answer
```

ResolveOps is designed more like this:

```text
Customer asks a question
        |
        v
ResolveOps searches trusted company knowledge
        |
        v
ResolveOps finds relevant evidence
        |
        v
AI receives the question + the evidence
        |
        v
ResolveOps checks confidence and safety
        |
        +----------------------------+
        |                            |
Enough evidence?                 Not enough evidence?
        |                            |
        v                            v
Answer with sources          Ask for more information
or take safe action          or hand off to a human
```

That difference is the foundation of the product.

---

# 4. Who uses ResolveOps AI?

ResolveOps is not designed for only one type of user.

A complete support operation contains several roles.

## 4.1 Customer

The customer is the person who needs help.

The customer may use:

- a website chat widget;
- a self-service help portal;
- future email support;
- future WhatsApp or messaging support;
- future voice support.

The customer does not need to understand the technology behind ResolveOps.

From the customer’s point of view, the experience should be simple:

1. ask a question;
2. receive a useful answer quickly;
3. see a human when the AI should not continue;
4. avoid repeating the same story again and again.

## 4.2 Customer-support or customer-care agent

A support agent is a human employee who helps customers.

ResolveOps can help the agent:

- find similar historical tickets;
- see suggested replies;
- see evidence supporting a suggestion;
- understand what happened earlier in the conversation;
- see the customer’s previous support history;
- identify when a case is close to missing a service deadline;
- receive a suggested next step;
- use approved pre-written responses;
- review actions the AI performed;
- take over a conversation when the AI escalates it.

## 4.3 Support manager

A manager needs to understand the operation as a whole.

ResolveOps can help a manager answer questions such as:

- How many conversations are open?
- How many were resolved?
- How many were resolved by AI without a human?
- Where is the AI making mistakes?
- Which product areas generate the most failed questions?
- Which tickets are close to missing promised response times?
- Which support agents are overloaded?
- Which knowledge articles are missing?
- Which action tools fail most often?
- How much is the AI costing?

## 4.4 Quality-assurance team

A **quality-assurance team**, often shortened to **QA**, checks whether the product or support process is working correctly.

In ResolveOps, QA can review:

- bad AI answers;
- incorrect citations;
- low-confidence answers;
- failed queries;
- negative customer feedback;
- escalation decisions;
- action-tool outcomes;
- regression tests.

A **regression** means a newer change made something that previously worked become worse.

## 4.5 Product team

The product team decides what the company should improve or build.

Support data is valuable because customers often reveal product problems before dashboards or surveys do.

Future ResolveOps intelligence can help the product team understand:

- repeated feature requests;
- repeated bugs;
- common complaints;
- areas creating customer frustration;
- possible churn risk.

## 4.6 Engineering team

The engineering team builds and fixes the company’s software.

ResolveOps can help engineers see:

- clusters of similar bug reports;
- exact customer examples;
- product areas causing support spikes;
- AI-generated bug summaries;
- evidence linking a support problem to many customers.

## 4.7 Administrator

An administrator controls how ResolveOps itself is configured.

Administrators manage:

- user accounts;
- roles;
- workspaces;
- prompts;
- AI provider settings;
- security settings;
- API keys;
- data-retention settings;
- audit logs;
- integrations.

---

# 5. What happens to historical support tickets?

One of the first things ResolveOps can do is import historical support data.

## 5.1 Uploading a CSV file

ResolveOps can currently accept a CSV file.

**CSV** stands for **comma-separated values**.

A CSV file is essentially a simple spreadsheet stored as text.

For example:

```text
ticket_id,title,status,priority
1001,Charged twice,resolved,high
1002,Cannot reset password,open,medium
```

Each row represents one ticket.

## 5.2 Validation

ResolveOps checks the imported data before trusting it.

It can track:

- valid rows;
- invalid rows;
- duplicate ticket IDs;
- failures that happened while processing the ticket.

This matters because an AI system trained or grounded on bad data can produce bad results.

Garbage in, garbage out is a simple way to describe the problem:

> If the source information is wrong or messy, the result built from that information may also be wrong or messy.

## 5.3 Sensitive information

Support tickets may contain personal information.

Examples:

- email addresses;
- phone numbers;
- payment-card-like numbers;
- Social Security numbers;
- network addresses.

This type of information is often called **PII**, meaning **personally identifiable information**.

ResolveOps has PII detection and redaction capabilities.

**Redaction** means replacing or hiding sensitive information.

For example:

```text
Before:
Please contact me at alice@example.com

After redaction:
Please contact me at [REDACTED]
```

The system can apply this protection during ingestion when configured.

## 5.4 Breaking long tickets into smaller pieces

A long ticket may contain:

- the original complaint;
- troubleshooting;
- several replies;
- resolution steps.

ResolveOps breaks long text into smaller pieces called **chunks**.

A chunk is simply a manageable section of text.

Why do this?

Because when a user asks about a billing error, the system may only need the part of an old ticket that explains the billing resolution rather than the entire conversation.

## 5.5 Embeddings

ResolveOps converts chunks into **embeddings**.

An embedding is a numerical representation of meaning.

The easiest analogy is a map.

Imagine every piece of text is placed on a giant map based on what it means.

Texts about password resets appear near other texts about password resets.

Texts about billing problems appear near other texts about billing problems.

The exact words do not have to match perfectly.

Example:

- “I was charged twice.”
- “There are two identical payments on my card.”

These sentences use different words, but they describe a similar problem.

Embedding-based search tries to recognize that similarity.

---

# 6. How ResolveOps answers a question

Suppose someone asks:

> “How do we fix a duplicate subscription charge?”

ResolveOps follows several steps.

## Step 1: Understand the query

The system receives the question.

## Step 2: Search stored support knowledge

ResolveOps looks for ticket chunks that are similar in meaning.

## Step 3: Retrieve the best evidence

The system selects the most relevant pieces.

This search-and-retrieve process is an important part of a technique called **RAG**.

**RAG** stands for **Retrieval-Augmented Generation**.

The name sounds complicated, but the idea is simple:

> Search trusted information first, then ask the AI to write an answer using that information.

## Step 4: Ask the AI to answer using the evidence

The AI receives:

- the user’s question;
- retrieved support evidence;
- system instructions;
- selected settings.

## Step 5: Attach citations

A **citation** is a reference showing where supporting information came from.

ResolveOps can return cited ticket information with an answer.

This allows a human to verify the result.

## Step 6: Measure confidence and quality

The system also records signals such as:

- confidence;
- citation coverage;
- retrieval precision;
- answer completeness;
- hallucination risk;
- latency;
- estimated cost.

These terms are explained later in this document.

## Step 7: Refuse or escalate when evidence is weak

If the search result is weak, ResolveOps can return a fallback instead of pretending to know.

That fallback behavior is a core safety principle.

---

# 7. What is a hallucination?

In AI systems, a **hallucination** is an answer that contains made-up, unsupported, or incorrect information.

Example:

A customer asks:

> “Can I receive a refund after 90 days?”

The company policy only allows refunds within 30 days.

If the AI invents a 90-day policy because it sounds helpful, that is a serious failure.

ResolveOps reduces this risk by:

- retrieving evidence;
- returning citations;
- calculating quality signals;
- using confidence thresholds;
- tracking failed queries;
- allowing human feedback;
- handing off when necessary.

No AI system should be described as incapable of hallucination.

The correct product goal is to reduce, detect, measure, and safely handle the risk.

---

# 8. Human handoff

One of the most important product ideas is that the AI is not expected to solve everything.

A **handoff** means transferring responsibility from the AI to a human support agent.

A handoff may happen because:

- the AI does not have enough evidence;
- the customer is angry;
- the customer asks for a human;
- the issue is high risk;
- an important action needs approval;
- the system cannot safely identify the correct solution.

A bad handoff would look like this:

> “I cannot help. Contact support.”

Then the customer has to start again.

A good handoff should preserve:

- the conversation transcript;
- the customer identity;
- the customer’s previous support history;
- relevant sources;
- what the AI already tried;
- the reason for escalation;
- any actions already taken.

ResolveOps V6 introduced customer conversations, customer profiles, handoffs, and resolution outcomes so this continuity can exist.

---

# 9. Customer-facing chat widget

ResolveOps includes an embeddable chat widget.

**Embeddable** means another website can include it.

A business could place a small support icon on its website.

When a customer opens it, they can start a support conversation.

The current implementation includes:

- a JavaScript widget;
- a widget page;
- session creation;
- customer messages;
- AI responses;
- feedback;
- conversation records;
- human escalation.

The widget is one of the main changes that transformed ResolveOps from an internal support-analysis tool into a product that can interact directly with customers.

---

# 10. Support-agent assistance

The product can also assist a human support agent rather than speaking directly to the customer.

This is often called a **copilot**.

A copilot is an AI assistant that helps a human worker.

ResolveOps can support concepts such as:

- suggested reply;
- internal note;
- related ticket information;
- recommended escalation;
- suggested canned response;
- customer history;
- knowledge suggestions.

The human can remain responsible for the final decision.

This is especially useful for cases where full automation would be risky.

---

# 11. Action-taking tools

A major step beyond answering questions is taking actions.

Examples of support actions include:

- create a ticket;
- update a ticket status;
- look up a customer;
- search a knowledge base;
- check a service deadline;
- list pending handoffs.

ResolveOps has a **tool registry**.

A tool registry is simply a controlled list of actions that the AI is allowed to request.

The system also records tool executions and action logs.

This is important because giving an AI permission to change real systems increases risk.

A production system must know:

- which tool was used;
- who requested it;
- what input was provided;
- what output came back;
- whether it succeeded;
- how long it took;
- whether approval was required.

The current tools are primarily mock or development-safe tools.

A **mock** is a predictable fake implementation used for development and testing.

For example, a mock refund tool can simulate what a refund flow would look like without moving real money.

That is the correct approach while the safety model is still being built.

---

# 12. Why action safety matters

Answering incorrectly is bad.

Taking the wrong real-world action can be worse.

Imagine an AI mistakenly:

- issues a $5,000 refund;
- cancels the wrong account;
- changes the wrong customer’s address;
- closes an unresolved support case;
- reveals private customer information.

Therefore, real actions should eventually have:

- risk levels;
- permissions;
- amount or impact limits;
- human approval when required;
- simulation mode;
- audit records;
- retry protection;
- reversal plans.

One important technical word is **idempotency**.

Idempotency means repeated copies of the same request should not accidentally repeat the side effect.

Example:

If a refund request is retried because of a network problem, the customer should not receive two refunds.

---

# 13. Workspaces and data separation

ResolveOps supports **workspaces**.

A workspace represents one company, team, or organizational area.

Why is this necessary?

Imagine Company A and Company B use the same ResolveOps installation.

Company A must never see Company B’s tickets.

The system therefore associates important records with a workspace and filters data based on the current workspace.

This concept is also called **multi-tenancy**.

A multi-tenant application serves multiple organizations while keeping their data logically separated.

This was added and strengthened during V5.

---

# 14. Authentication and authorization

These two words are easy to confuse.

## Authentication

Authentication means:

> “Who are you?”

Example:

A user logs in with an email and password.

## Authorization

Authorization means:

> “Now that we know who you are, what are you allowed to do?”

For example:

- an administrator may change user roles;
- a normal member may not;
- a viewer may only read certain information.

ResolveOps supports user accounts and roles.

This kind of design is often called **RBAC**, meaning **role-based access control**.

That simply means permissions are based partly on a person’s role.

---

# 15. Audit logs

An **audit log** is a history of important activity.

A good audit log can help answer:

- Who changed this setting?
- Who changed the user’s role?
- Which prompt was activated?
- When was retention cleanup run?
- Which action tool was executed?

Audit history is important for security, accountability, debugging, and business trust.

---

# 16. Knowledge base

A **knowledge base** is a collection of approved help information.

Examples:

- “How to reset your password”;
- “Refund policy”;
- “How to connect an integration”;
- “Known billing errors.”

ResolveOps can generate knowledge-base drafts from resolved support tickets.

It also has self-service portal articles and later intelligence that can suggest knowledge gaps.

The long-term goal is not only to answer questions from existing knowledge.

It is also to identify where knowledge is missing, stale, duplicated, or contradictory.

---

# 17. Self-service portal

The V9 product includes portal articles.

A self-service portal allows a customer to find an answer without starting a conversation with a human support agent.

This can reduce repetitive ticket volume.

The portal supports concepts such as:

- article title;
- readable URL name;
- category;
- product area;
- tags;
- draft or published state;
- view counts;
- helpfulness counts.

It also includes ticket-status lookup concepts.

---

# 18. Routing rules

A support team often wants different problems to go to different people.

Example:

```text
If product area = Billing
and sentiment = very negative
then set priority = high
and route to senior support
```

ResolveOps V9 includes routing-rule management.

A **routing rule** is a simple “if this, then that” rule.

The current interface uses structured rule definitions that are still somewhat technical.

A future version should provide a visual rule builder so a support manager does not need to understand JSON.

**JSON** is a text format used by software to store structured information. It is useful for engineers, but it should not be required knowledge for a normal support manager.

---

# 19. Canned responses

A canned response is a pre-written answer for a common situation.

Example:

> “Thanks for contacting us. I can see that your refund was processed on Tuesday. Bank processing can take several business days.”

ResolveOps supports canned-response management, search, shortcuts, categories, and usage tracking.

The AI copilot can later recommend an appropriate canned response.

---

# 20. SLA risk

**SLA** means **service-level agreement**.

A service-level agreement is a promised service target.

Example:

> “Critical tickets must receive a first response within one hour.”

ResolveOps can identify open tickets that are at risk of missing those targets.

This gives support managers a chance to act before the deadline is missed.

---

# 21. Reliability measurements

ResolveOps treats AI quality as something that should be measured.

## 21.1 Citation coverage

How much of the answer appears to be supported by cited evidence?

## 21.2 Retrieval precision

Did the search step find information that was actually relevant?

## 21.3 Answer completeness

Did the answer address the user’s main question?

## 21.4 Hallucination risk

Does the answer appear to contain statements not supported by the retrieved evidence?

## 21.5 Latency

**Latency** means how long the system took to respond.

ResolveOps tracks values such as p50, p95, and p99.

A simple explanation:

- p50 is around the normal middle request;
- p95 focuses on slower requests experienced by the slowest 5%;
- p99 focuses on very slow edge cases.

## 21.6 Cost

Real AI models may charge based on usage.

ResolveOps can track estimated provider/model cost so a company can understand whether automation is economically sensible.

---

# 22. Feedback loop

A support AI should not be launched once and forgotten.

It should improve based on real outcomes.

ResolveOps includes feedback and intelligence features that can track:

- helpful answers;
- unhelpful answers;
- wrong citations;
- failed queries;
- customer satisfaction signals;
- handoffs;
- resolution outcomes;
- tool success;
- knowledge suggestions.

A **feedback loop** simply means using the result of past behavior to improve future behavior.

---

# 23. Containment rate

A common AI-support metric is **containment rate**.

Containment rate means:

> What percentage of conversations did the automated system resolve without requiring a human takeover?

Example:

- 100 total conversations;
- 70 resolved by AI;
- 30 handed to humans.

Containment rate = 70%.

However, a high containment rate is not automatically good.

An AI could “contain” many conversations by giving poor answers and closing them too early.

Therefore containment should be considered together with:

- customer satisfaction;
- reopen rate;
- correctness;
- escalation accuracy;
- quality measurements.

---

# 24. Analytics and reports

ResolveOps V10a includes analytics and reporting features.

Managers can examine values such as:

- conversation volume;
- resolved conversations;
- containment;
- confidence;
- open conversations;
- AI queries;
- tool executions;
- SLA problems;
- agent performance;
- trends over time.

Reports can be saved and exported.

The purpose is to turn support activity into something a manager can inspect and improve.

---

# 25. API keys

An **API key** is a secret credential used by software rather than a human logging in manually.

For example, another internal application may need permission to call ResolveOps.

ResolveOps V10a supports API-key concepts such as:

- workspace ownership;
- scopes;
- expiration;
- last-used tracking;
- revocation;
- hashed storage.

A **scope** means the specific permission assigned to the key.

A key should not receive unlimited access when it only needs one small operation.

---

# 26. Rate limiting

**Rate limiting** means controlling how many requests a client can make during a period of time.

Why?

Without limits, someone could:

- accidentally send millions of requests;
- intentionally attack the system;
- create very high AI costs;
- slow the service for everyone else.

V10a includes rate-limiting controls.

A future production deployment should make sure rate-limit state is shared correctly when multiple backend servers are running.

---

# 27. Login protection

Attackers sometimes try many passwords until one works.

This is called a **brute-force attack**.

ResolveOps tracks login attempts and includes lockout-related security settings.

Future production hardening should add things such as:

- multi-factor authentication;
- password reset;
- email verification;
- enterprise single sign-on;
- device/session management.

**Multi-factor authentication**, or MFA, means requiring more than one proof of identity.

**Single sign-on**, or SSO, means letting employees sign in through the identity system their company already uses.

---

# 28. Why the project uses mock AI and mock integrations

ResolveOps intentionally supports predictable mock behavior.

There are two reasons.

## Reason 1: Cost

A developer should be able to run tests without paying an AI provider every time.

## Reason 2: Repeatability

An automated test should produce predictable results.

A real generative AI model can produce slightly different wording across runs.

A deterministic mock produces the same result for the same input.

**Deterministic** means predictable and repeatable.

Mock implementations are valuable for development.

But a feature using mocks should not be described to a paying client as a complete real integration.

For example, the current Zendesk/Freshdesk/Intercom connector architecture is useful, but real vendor connectivity still has to be built and hardened.

---

# 29. How the product is tested

ResolveOps contains automated tests.

## Unit test

A unit test checks one small behavior.

Example:

> Does the PII scanner recognize an email address?

## Integration test

An integration test checks several pieces working together.

Example:

> Can an authenticated user create and retrieve a support conversation?

## Frontend test

A frontend test checks visible web behavior.

## Smoke test

A smoke test checks whether the main product flow works after the system starts.

ResolveOps currently contains versioned smoke scripts through V4.

The code has since moved through V10a, so later-version end-to-end smoke tests are an important missing piece.

## CI

**CI** means **continuous integration**.

CI automatically checks code changes.

The current project runs checks such as:

- backend linting;
- backend type checking;
- backend tests;
- frontend linting;
- frontend type checking;
- frontend tests;
- frontend build;
- Docker smoke validation.

A **linter** is an automated code-quality checker.

A **type checker** catches certain mismatches before the application runs.

---

# 30. Docker and deployment

ResolveOps uses Docker.

**Docker** packages software together with the environment it needs to run.

This makes development more consistent across different computers.

ResolveOps also uses Docker Compose.

**Docker Compose** starts multiple related services together.

In ResolveOps those services include:

- frontend;
- backend;
- database.

The repository also contains a Render deployment blueprint.

That means the project has a path toward cloud deployment, but a configuration file alone is not the same as proving a production deployment is healthy under real use.

---

# 31. What ResolveOps is today

ResolveOps is no longer only a ticket-search demo.

The current repository includes product capabilities across:

- data ingestion;
- semantic search;
- cited AI answers;
- AI-quality measurement;
- evaluation;
- support workflows;
- customer conversations;
- human handoff;
- action tools;
- knowledge generation;
- customer self-service;
- support-agent assistance;
- workflow routing;
- analytics;
- reports;
- authentication;
- permissions;
- data isolation;
- security controls;
- auditing.

That makes it a broad full-stack support platform prototype.

---

# 32. What ResolveOps is not today

It is important not to oversell the current state.

ResolveOps is **not yet a fully production-proven replacement** for a mature enterprise support platform.

Important gaps include:

- live vendor connectors;
- production-grade background workers;
- end-to-end smoke coverage for later versions;
- real high-impact action integrations;
- approval policies for high-risk actions;
- deeper prompt-injection defenses;
- full production observability;
- proven backups and disaster recovery;
- omnichannel email/voice/WhatsApp support;
- enterprise SSO/MFA;
- full browser-level end-to-end test coverage.

Those gaps do not make the current project worthless.

They tell us what type of customer we can responsibly sell to first.

The strongest immediate commercial position is a **controlled paid pilot**, not an enterprise replacement promise.

---

# 33. What should a first paid client buy?

A first client should not be sold the entire future vision.

A practical first paid offer is:

> **ResolveOps Support Intelligence Pilot**

The pilot can focus on lower-risk value:

1. import historical support tickets;
2. build searchable support knowledge;
3. answer internal support-agent questions with citations;
4. provide suggested replies;
5. identify failed queries and knowledge gaps;
6. provide support analytics;
7. run a controlled customer widget on a small audience if quality targets are met.

Avoid beginning with:

- automatic real refunds;
- automatic subscription cancellation;
- unrestricted account changes;
- medical/legal/financial decisions;
- replacing the existing helpdesk overnight.

This approach allows ResolveOps to earn trust before receiving more power.

---

# 34. Long-term vision

The strongest long-term vision is:

> ResolveOps becomes a trusted support operations layer that understands customer history, searches company knowledge, answers with evidence, knows when to involve a human, safely performs approved actions, learns from outcomes, identifies support and product problems, and connects with other business systems and AI agents.

The important word is **trusted**.

The project should not compete only on how many things the AI can do.

It should compete on:

- how safely it acts;
- how clearly it shows evidence;
- how well it hands off to people;
- how measurable its quality is;
- how quickly a team can learn from failures;
- how easily it fits into existing support work.

---

# 35. Product principles

## 35.1 Evidence over confidence

A confident answer without evidence is not enough.

## 35.2 “I do not know” is an acceptable result

Refusing safely is better than inventing confidently.

## 35.3 Human handoff is part of the design

Escalation is not automatically a failure.

## 35.4 More power requires more controls

A system that can perform real actions needs stronger authorization, approval, and audit controls than a system that only drafts text.

## 35.5 Quality must be measured continuously

Do not judge AI quality from one impressive demo.

## 35.6 The client should understand what the AI did

Important answers and actions should be inspectable.

## 35.7 Build a repeatable low-cost development path

Mock providers and deterministic tests keep the development process affordable and reliable.

## 35.8 Do not call something production ready before proving it

Production readiness is an operational claim, not a feature-count claim.

---

# 36. Simple end-to-end example

A customer writes:

> “I was charged twice for my subscription.”

A mature ResolveOps flow should eventually do the following:

1. Create or identify the customer conversation.
2. Detect that the topic is billing.
3. Search approved billing knowledge and similar solved tickets.
4. Retrieve evidence explaining duplicate-charge cases.
5. Check customer history.
6. Calculate whether the evidence is strong enough.
7. If it is an informational question, produce an evidence-backed response.
8. If a refund is required, select a refund tool.
9. Check whether the requested refund is allowed by policy.
10. Check whether the AI is allowed to perform the action automatically.
11. If human approval is required, create an approval request.
12. A human sees the requested action, amount, evidence, and customer context.
13. After approval, the action is performed exactly once.
14. The action is recorded in the audit log.
15. The customer receives the result.
16. The conversation is marked resolved or remains open.
17. ResolveOps records whether the customer was satisfied.
18. The result contributes to future quality measurements.
19. If many customers report the same issue, ResolveOps identifies the pattern.
20. Product or engineering teams receive a meaningful problem signal.

This is the full idea behind the platform: not merely answer text, but connect knowledge, people, actions, quality, and operations.

---

# 37. What to read next

Continue with:

- [`01_WHAT_WE_HAVE_BUILT.md`](./01_WHAT_WE_HAVE_BUILT.md) for the exact built feature inventory;
- [`02_WHAT_IS_MISSING.md`](./02_WHAT_IS_MISSING.md) for the gap list;
- [`03_HOW_SUPPORT_TEAMS_USE_RESOLVEOPS.md`](./03_HOW_SUPPORT_TEAMS_USE_RESOLVEOPS.md) for real team workflows;
- [`07_FROM_CURRENT_STATE_TO_FIRST_PAID_CLIENT.md`](./07_FROM_CURRENT_STATE_TO_FIRST_PAID_CLIENT.md) for the path to revenue;
- [`09_GLOSSARY_FOR_NON_TECHNICAL_READERS.md`](./09_GLOSSARY_FOR_NON_TECHNICAL_READERS.md) whenever a technical term is unfamiliar.
