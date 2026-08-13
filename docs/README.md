# ResolveOps AI Documentation Map

This `docs/` folder is the plain-English source of truth for ResolveOps AI.

The goal of this documentation set is simple: a new intern, a school-going student, a non-technical business owner, a support manager, or an engineer joining the project should be able to understand what ResolveOps AI is, what has already been built, what is still missing, and what needs to happen before the product can be sold responsibly to paying clients.

The code has grown faster than the older project documentation. The current `main` branch contains product work through **V10a: Analytics & Reporting + Advanced Security**, while older files such as the original `VERSION_STATUS.md` do not yet describe that full state. The files below correct that problem.

## Recommended reading order

### 1. [`00_PRODUCT_OVERVIEW_PLAIN_ENGLISH.md`](./00_PRODUCT_OVERVIEW_PLAIN_ENGLISH.md)
Start here. It explains what ResolveOps AI is, the problem it solves, who uses it, and how the product works without assuming a technical background.

### 2. [`01_WHAT_WE_HAVE_BUILT.md`](./01_WHAT_WE_HAVE_BUILT.md)
A detailed inventory of what is already in the repository, including V1 through V10a.

### 3. [`02_WHAT_IS_MISSING.md`](./02_WHAT_IS_MISSING.md)
A detailed gap register separating demo-complete work from paid-pilot and enterprise-production gaps.

### 4. [`03_HOW_SUPPORT_TEAMS_USE_RESOLVEOPS.md`](./03_HOW_SUPPORT_TEAMS_USE_RESOLVEOPS.md)
Explains how customer-care agents, support leads, quality-assurance teams, product teams, engineers, operations teams, administrators, and customers would use ResolveOps.

### 5. [`04_CLIENT_ONBOARDING_AND_DAILY_OPERATIONS.md`](./04_CLIENT_ONBOARDING_AND_DAILY_OPERATIONS.md)
Explains what happens after a client says yes: onboarding, importing knowledge, testing, gradual rollout, daily operations, human escalation, incident handling, and offboarding.

### 6. [`05_SECURITY_RELIABILITY_AND_TRUST.md`](./05_SECURITY_RELIABILITY_AND_TRUST.md)
Explains identity, permissions, workspace isolation, personal-information protection, audit logs, rate limiting, login protection, prompt injection, safe tool use, human approval, backups, monitoring, and AI evaluation.

### 7. [`06_CLIENT_READY_GAP_ANALYSIS_DEVILS_ADVOCATE.md`](./06_CLIENT_READY_GAP_ANALYSIS_DEVILS_ADVOCATE.md)
The deliberately skeptical review. It asks: **If a client paid us tomorrow, what could go wrong?**

### 8. [`07_FROM_CURRENT_STATE_TO_FIRST_PAID_CLIENT.md`](./07_FROM_CURRENT_STATE_TO_FIRST_PAID_CLIENT.md)
The commercial execution plan from the current codebase to a sellable paid pilot and then repeatable monthly revenue.

### 9. [`08_PRODUCT_ROADMAP_TO_PRODUCTION.md`](./08_PRODUCT_ROADMAP_TO_PRODUCTION.md)
The engineering and product roadmap beyond V10a.

### 10. [`09_GLOSSARY_FOR_NON_TECHNICAL_READERS.md`](./09_GLOSSARY_FOR_NON_TECHNICAL_READERS.md)
Definitions for technical terms used throughout the project.

### 11. [`10_DEMO_AND_SALES_PLAYBOOK.md`](./10_DEMO_AND_SALES_PLAYBOOK.md)
A practical guide for showing the product to a prospect, handling objections, and proposing a paid pilot without overselling unfinished capabilities.

---

## Three different meanings of “complete”

### Portfolio/demo complete
The feature exists, works in the repository, has reasonable automated checks, and can be demonstrated with sample or controlled data.

### Paid-pilot ready
A real client can use the feature in a limited, controlled environment with clear support, monitoring, recovery, permissions, and boundaries.

### Enterprise production ready
A larger organization can depend on the feature for business-critical work with mature identity, security, backup/recovery, compliance, high availability, monitoring, change control, and operational support.

ResolveOps has many features that are portfolio/demo complete. It is **not correct to assume that every feature is enterprise production ready** simply because the code exists.

---

## Current high-level assessment

ResolveOps AI is already much more than a simple chatbot. The current repository includes the major building blocks of a modern customer-support platform: historical support knowledge, cited AI answers, quality measurement, customer conversations, human handoff, controlled action tools, workflow automation, analytics, reporting, and security controls.

The most important next step is not adding another large collection of features. The most important next step is proving, hardening, documenting, and operating what already exists.

The recommended immediate milestone is **V10b: Documentation, Validation, and Release Hardening**.

After that, the strongest path to revenue is a controlled paid pilot for a small support team, not an unsupported claim that ResolveOps can immediately replace Zendesk, Intercom, Freshdesk, or Salesforce for an enterprise customer.
