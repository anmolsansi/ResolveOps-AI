# ResolveOps AI — Sellable Package Completion Gate

## Governing rule

Every capability advertised inside a paid ResolveOps package must be finished, tested, documented, deployed, and supported before that package is sold as complete.

Future features that are clearly outside the package do not block launch. Promised features do.

## Proposed first complete package

**ResolveOps AI Support Intelligence and Agent Assistance**

The package is intended to let a support team securely bring approved historical support knowledge into ResolveOps, find and draft evidence-backed answers, preserve customer and conversation context, escalate uncertain cases to humans, and measure quality and operational performance.

## Completion gate

Before launch, verify all of the following.

### Identity and data separation

- User login works in the deployed environment.
- Role restrictions are tested.
- Workspace isolation is tested using multiple workspaces.
- Production secrets are configured safely.

### Knowledge ingestion

- The supported import path works end to end.
- Invalid rows and duplicates are handled clearly.
- Sensitive-data behavior is tested.
- Failure recovery and limits are documented.

A live Zendesk, Freshdesk, or Intercom connection is a launch blocker only if that connector is included in the paid package.

### AI assistance

- Retrieval quality is tested on realistic support data.
- A supported production model/provider is configured.
- Citations identify supporting sources clearly.
- Low-confidence questions fail safely.
- Model failures have a usable fallback.

### Human support workflow

- Suggested replies are reviewable.
- Internal-only information is protected from customer-facing output.
- Human handoff preserves conversation context.
- Handoff acknowledgement and resolution work end to end.

### Manager visibility

- Reliability metrics reflect real data correctly.
- Analytics definitions are agreed and explained.
- Reports and exports obey workspace permissions.

### Security and privacy

- Access control is enforced.
- Sensitive-data handling is documented.
- API key permissions and revocation work if API keys are included.
- Production request limits are configured.
- Login-abuse protection is configured.
- Network allowlisting is tested if included.

### Deployment and operations

- The exact release candidate is deployed successfully.
- HTTPS and environment configuration are verified.
- Database migration is verified.
- Monitoring is active.
- Backups are active.
- A restore has been tested.
- Incident response is documented.
- Rollback is documented.

### Automatic background work

If the package promises automatic recurring work, the production worker/scheduler, retries, duplicate-execution protection, and failure visibility must be complete before launch.

If it is not part of the package, it must be explicitly excluded rather than partially promised.

### Customer-facing chat

If public customer chat is part of the package, the public widget must have appropriate access controls, abuse protection, request limits, site restrictions, and full human-handoff testing.

If customer-facing chat is outside the package, it should not be advertised as included.

### Automated actions

High-impact external actions should be excluded from the first package unless every promised action has a real integration, permissions, risk limits, approval rules where appropriate, duplicate-action protection, audit logging, and failure handling.

### Testing

- Backend tests pass.
- Frontend tests cover all paid critical flows.
- A release smoke test covers the complete paid workflow.
- At least one browser-level end-to-end test covers the real support-agent journey.
- Security tests cover unauthorized access, workspace isolation, roles, exports, and hostile-input cases.

### Documentation and usability

- Product scope is written in plain language.
- Onboarding is documented and rehearsed.
- Administrator operations are documented.
- Included and excluded features are explicit.
- Known limitations do not contradict sales claims.

### Commercial clarity

- The exact paid package is frozen.
- Every included capability is complete.
- The price is for the complete package, not a discounted incomplete implementation.
- The demonstration uses the same behavior the client will receive.
- The written proposal describes only completed included capabilities.

## Launch decision

ResolveOps should be called ready to sell as this package only when every included capability is complete and every applicable launch blocker above is closed.

> **Finish the promised package first. Prove it works. Then sell the complete result.**
