# V3 Reliability Completion Guide

V3 turns ResolveOps AI from a cited RAG demo into a reliability-focused support intelligence platform.

## Completed V3 capabilities

- Deterministic answer-quality scoring in mock mode.
- Hallucination risk, citation coverage, retrieval precision, and answer completeness per query.
- Provider/model attribution and estimated cost tracking.
- Latency averages and percentiles.
- Product-area quality breakdown.
- Failed-query review queue.
- Human feedback analytics.
- Failed-query actions to mark items reviewed or ignored.
- Failed-query promotion into saved eval questions.
- Stored regression comparisons through reliability comparison runs.

## Quality metric definitions

Confidence is derived from retrieval scores. It is not randomly assigned.

Retrieval precision is the share of retrieved chunks that overlap with the user question after tokenization and stopword removal.

Citation coverage measures how much of the generated answer is supported by tokens from cited ticket contexts.

Hallucination risk measures how much of the generated answer is not supported by any retrieved context.

Answer completeness measures how much of the user question is addressed by the answer tokens.

When retrieval confidence is below the configured threshold, the answer must say that there is not enough context. Fallback answers should not include citations.

## Reliability API surface

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/reliability/feedback` | Feedback analytics across RAG queries |
| `POST` | `/reliability/failed-queries/{query_id}/review` | Mark a failed query reviewed or ignored |
| `POST` | `/reliability/failed-queries/{query_id}/add-to-eval` | Save a failed query as an eval question |
| `POST` | `/reliability/compare` | Run and persist a regression comparison |
| `GET` | `/reliability/comparisons` | List stored regression comparisons |

## Required validation

Run backend tests, backend lint, backend typecheck, frontend lint, frontend typecheck, frontend build, Docker startup, sample CSV upload, a cited RAG query, a low-confidence fallback query, a feedback analytics check, a stored reliability comparison, and a failed-query review action.

## V3 boundaries

V3 does not add enterprise authentication, real support-tool credentials, background workers, or cloud deployment. Those belong to later phases.
