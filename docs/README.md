# ResolveOps AI Documentation Map

This `docs/` folder is the plain-English source of truth for ResolveOps AI.

The documentation is written so that a new intern, a school-going student, a non-technical business owner, a support manager, or an engineer joining the project can understand what ResolveOps is, what has already been built, what remains incomplete, and what must happen before the product is sold to paying clients.

The current repository contains product work through **V10a: Analytics & Reporting + Advanced Security**. The commercial plan now follows a strict **complete-before-charge** rule:

> **Define the exact paid package, complete every capability promised inside that package, validate the complete user journey, deploy and operate it properly, and only then sell that completed package.**

If a package promises ten capabilities, all ten must be complete before that ten-capability package is sold as complete. ResolveOps will not treat “eight out of ten finished” as acceptable delivery simply by reducing the price.

At the same time, this does not mean every idea on the long-term roadmap must be built before revenue. Future capabilities can remain outside the first commercial package as long as they are clearly identified as excluded rather than implied to be included.

---

## Recommended reading order

### 1. [`00_PRODUCT_OVERVIEW_PLAIN_ENGLISH.md`](./00_PRODUCT_OVERVIEW_PLAIN_ENGLISH.md)
Start here. It explains what ResolveOps AI is, the problem it solves, who uses it, and how the product works without assuming a technical background.

### 2. [`01_WHAT_WE_HAVE_BUILT.md`](./01_WHAT_WE_HAVE_BUILT.md)
A detailed inventory of what is already in the repository, including V1 through V10a.

### 3. [`02_WHAT_IS_MISSING.md`](./02_WHAT_IS_MISSING.md)
A detailed gap register showing what exists, what still requires production hardening, and what remains future work.

### 4. [`03_HOW_SUPPORT_TEAMS_USE_RESOLVEOPS.md`](./03_HOW_SUPPORT_TEAMS_USE_RESOLVEOPS.md)
Explains how customer-care agents, support leads, quality-assurance teams, product teams, engineers, operations teams, administrators, and customers would use ResolveOps.

### 5. [`04_CLIENT_ONBOARDING_AND_DAILY_OPERATIONS.md`](./04_CLIENT_ONBOARDING_AND_DAILY_OPERATIONS.md)
Explains client onboarding, data import, configuration, daily operations, human escalation, incidents, change management, and offboarding.

### 6. [`05_SECURITY_RELIABILITY_AND_TRUST.md`](./05_SECURITY_RELIABILITY_AND_TRUST.md)
Explains identity, permissions, workspace isolation, personal-information protection, audit logs, request limiting, login protection, prompt injection, safe tool use, backups, monitoring, recovery, and AI evaluation.

### 7. [`06_CLIENT_READY_GAP_ANALYSIS_DEVILS_ADVOCATE.md`](./06_CLIENT_READY_GAP_ANALYSIS_DEVILS_ADVOCATE.md)
The deliberately skeptical review. It asks what would break, embarrass us, or create client risk if we declared the product ready too early.

### 8. [`07_FROM_CURRENT_STATE_TO_FIRST_PAID_CLIENT.md`](./07_FROM_CURRENT_STATE_TO_FIRST_PAID_CLIENT.md)
The main commercial execution plan. It defines the shortest path from the current repository to a **fully completed first sellable package**, not a partially finished paid delivery.

### 9. [`08_PRODUCT_ROADMAP_TO_PRODUCTION.md`](./08_PRODUCT_ROADMAP_TO_PRODUCTION.md)
The engineering and product roadmap beyond the current V10a state.

### 10. [`09_GLOSSARY_FOR_NON_TECHNICAL_READERS.md`](./09_GLOSSARY_FOR_NON_TECHNICAL_READERS.md)
Plain-English definitions for technical terms used throughout the project.

### 11. [`10_DEMO_AND_SALES_PLAYBOOK.md`](./10_DEMO_AND_SALES_PLAYBOOK.md)
Explains how to demonstrate only the completed product, distinguish included capabilities from future work, handle prospect requests, and keep sales claims aligned with actual behavior.

### 12. [`11_COMPLETE_BEFORE_CHARGE_COMMERCIAL_POLICY.md`](./11_COMPLETE_BEFORE_CHARGE_COMMERCIAL_POLICY.md)
The detailed commercial rule: a promised feature is a launch blocker until it is complete; a future feature is not a blocker only when it is clearly outside the paid package.

### 13. [`12_SELLABLE_PACKAGE_COMPLETION_GATE.md`](./12_SELLABLE_PACKAGE_COMPLETION_GATE.md)
The launch checklist used to decide whether the first commercial package is genuinely ready to sell. It covers product behavior, testing, permissions, isolation, security, deployment, monitoring, backups, restore, onboarding, and commercial clarity.

### 14. [`14_FIRST_COMMERCIAL_PACKAGE_SCOPE.md`](./14_FIRST_COMMERCIAL_PACKAGE_SCOPE.md)
Defines the proposed first complete package: **ResolveOps AI Support Intelligence and Agent Assistance**, including its promised outcome, included capabilities, and explicitly excluded future capabilities.

---

## Three different meanings of “complete”

### Portfolio/demo complete
The feature exists, works in the repository, has reasonable automated checks, and can be demonstrated with sample or controlled data.

### Complete and sellable for a defined package
Every capability promised in the paid package works end to end and has the required permissions, data isolation, testing, security, deployment, monitoring, recovery, onboarding, documentation, and support ownership.

This is the level ResolveOps must reach before charging for the first commercial package.

### Enterprise production ready
The product additionally satisfies the more demanding requirements of large organizations, which may include enterprise identity, formal compliance work, regional data controls, contractual availability targets, advanced disaster recovery, high availability, procurement requirements, and deeper operational controls.

ResolveOps has many features that are portfolio/demo complete. That does not automatically make every V1–V10a capability enterprise-production ready.

---

## Proposed first complete commercial package

The recommended first package is:

# ResolveOps AI Support Intelligence and Agent Assistance

Its purpose is to let a support team:

- securely use approved historical support knowledge;
- find relevant previous solutions;
- receive AI answer drafts backed by evidence;
- see citations showing where answers came from;
- fail safely when evidence is insufficient;
- preserve customer and conversation context;
- escalate uncertain cases to humans;
- and give managers clear visibility into quality and operational performance.

The package also requires the production operating foundation around those capabilities: tested deployment, monitoring, backups, tested restore, security checks, end-to-end tests, onboarding instructions, administrator documentation, and incident/support procedures.

---

## What does not need to block the first sale

Capabilities such as live Zendesk/Freshdesk/Intercom synchronization, voice, WhatsApp, SMS, high-impact autonomous actions, MCP, enterprise SSO, and other later roadmap items do not have to delay the first package **unless they are included in the promise to that client**.

If one of those capabilities is promised as part of the package, it must be completed before that revised package is sold.

This is how ResolveOps can move quickly without accepting partial delivery.

---

## Immediate milestone

The recommended immediate milestone is **V10b: Complete First Commercial Package**.

V10b should prioritize:

- freezing the exact paid scope;
- closing every included feature gap;
- adding commercial end-to-end validation for V5+ capabilities;
- strengthening frontend critical-flow tests;
- proving production deployment;
- configuring a real supported AI provider/model;
- adding monitoring and alerts;
- enabling backups and proving restore;
- completing security acceptance checks;
- documenting onboarding, administration, incidents, rollback, and support ownership.

During this release, unrelated optional feature expansion should stop.

The goal is not the largest possible product. The goal is:

> **the smallest valuable ResolveOps package that is 100% complete inside its promise.**
