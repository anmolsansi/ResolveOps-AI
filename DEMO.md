# ResolveOps AI — Demo Flow

This document walks through the full demo flow: sample CSV upload, RAG query with citations, low-confidence fallback, eval run, and dashboard metrics. All output shown was produced using the **free mock provider** (no API key required).

## Prerequisites

```bash
# Generate sample data (50 valid tickets + 2 intentionally invalid)
python scripts/generate_sample_tickets.py --include-invalid

# Start services
docker compose up -d

# Or run locally:
cd backend && pip install -e ".[dev]" && alembic upgrade head
uvicorn app.main:app --port 8000
```

## Step 1: Health Check

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok", "service": "resolveops-api"}
```

## Step 2: Upload Sample CSV

```bash
curl -X POST http://localhost:8000/tickets/upload \
  -F "file=@scripts/sample_tickets.csv"
```

**Result**: 52 rows processed — 50 valid, 2 invalid (1 missing required fields, 1 bad date format), 0 duplicates, 0 embedding failures. Valid rate: 96.15%.

```json
{
  "total_count": 52,
  "valid_count": 50,
  "invalid_count": 2,
  "duplicate_count": 0,
  "embedding_failure_count": 0,
  "errors": [
    {"row": 52, "ticket_id": null, "reason": "Missing required field: id; Missing required field: title; ..."},
    {"row": 53, "ticket_id": "TICKET-BAD-DATE", "reason": "Invalid created_at date format"}
  ]
}
```

## Step 3: RAG Query — Cited Answer

```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I fix login issues?", "top_k": 3}'
```

**Result**: The mock provider retrieves relevant login/password tickets and returns a **cited answer** with confidence 0.5967 (above the 0.3 threshold). Keyword-boosted retrieval ensures topically related tickets rank high even with mock embeddings.

```json
{
  "confidence": 0.5967,
  "answer": "Based on historical support tickets, here is a summary: ... Sources: [TICKET-0028], [TICKET-0050], [TICKET-0001]",
  "citations": ["TICKET-0028", "TICKET-0050", "TICKET-0001"],
  "retrieved_chunks": [
    {"ticket_id": "TICKET-0028", "score": 0.6533, "preview": "...password reset...login still fails..."},
    {"ticket_id": "TICKET-0050", "score": 0.5801, "preview": "...login fails with Invalid credentials..."},
    {"ticket_id": "TICKET-0001", "score": 0.5568, "preview": "...password reset...login..."}
  ],
  "latency_ms": 5,
  "estimated_cost_usd": 0.0
}
```

## Step 4: Low-Confidence Fallback

```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the best recipe for chocolate cake?"}'
```

**Result**: Completely unrelated query. Confidence is 0.155 (well below threshold). System correctly returns fallback answer with no citations.

```json
{
  "confidence": 0.155,
  "answer": "I don't have enough context to answer this question...",
  "citations": [],
  "latency_ms": 4
}
```

## Step 5: Eval Run

```bash
curl -X POST http://localhost:8000/eval/run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo-eval",
    "questions": [
      {"question": "How to resolve billing errors?"},
      {"question": "What causes SSO login failures?"},
      {"question": "How to fix webhook delivery issues?"}
    ]
  }'
```

**Result**: 3 questions evaluated. All pass the confidence threshold with keyword-boosted retrieval (avg confidence 0.6763).

```json
{
  "name": "demo-eval",
  "total_questions": 3,
  "passed_count": 3,
  "failed_count": 0,
  "average_confidence": 0.6763,
  "average_latency_ms": 4.0
}
```

## Step 6: Dashboard — Ingestion Quality

```bash
curl http://localhost:8000/dashboard/quality
```

**Result**: 1 batch, 52 rows seen, 50 valid (96.15%), 2 invalid (3.85%), 0 duplicates.

```json
{
  "total_batches": 1,
  "total_rows_seen": 52,
  "total_valid_rows": 50,
  "total_invalid_rows": 2,
  "valid_rate": 0.9615,
  "invalid_rate": 0.0385
}
```

## Step 7: Dashboard — Retrieval Metrics

```bash
curl http://localhost:8000/dashboard/retrieval
```

**Result**: 5 total queries tracked, average confidence 0.5561, 80% citation rate, $0.00 estimated cost. Only the unrelated "chocolate cake" query falls below the confidence threshold.

```json
{
  "total_queries": 5,
  "average_confidence": 0.5561,
  "low_confidence_query_count": 1,
  "average_latency_ms": 4.2,
  "total_estimated_cost_usd": 0.0,
  "citation_rate": 0.8
}
```

## Notes on Mock vs OpenAI Provider

The mock provider uses deterministic MD5-based embeddings combined with a **lexical keyword boost** for retrieval scoring. This means:

- **Related queries return cited answers** — keyword overlap between query and ticket text pushes confidence above the 0.3 threshold
- **Unrelated queries still return low-confidence fallback** — no keyword overlap keeps scores low
- **No API key required** — everything works out of the box with mock providers

To use real OpenAI embeddings and answer generation:

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
export MOCK_PROVIDERS=false
export LLM_PROVIDER=openai
export EMBEDDING_PROVIDER=openai
```

Then re-upload tickets (they'll get real OpenAI embeddings) and query again.
