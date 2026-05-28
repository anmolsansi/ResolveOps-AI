# ResolveOps AI — Demo Flow

This document walks through the full demo flow: sample CSV upload, RAG query with citations, low-confidence fallback, eval run, and dashboard metrics.

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

## Step 3: RAG Query

```bash
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I fix login issues?", "top_k": 3}'
```

**Result**: The mock provider retrieves relevant chunks (tickets about login/password issues) but confidence stays below the 0.3 threshold (mock embeddings produce scores ~0.15–0.25), so the fallback answer is returned. With a real OpenAI provider, the confidence would be higher and cited answers would be generated.

```json
{
  "confidence": 0.1967,
  "answer": "I don't have enough context to answer this question...",
  "citations": [],
  "retrieved_chunks": [
    {"ticket_id": "TICKET-0028", "score": 0.2533, "preview": "...password reset...login still fails..."},
    {"ticket_id": "TICKET-0050", "score": 0.1801, "preview": "...login fails with Invalid credentials..."},
    {"ticket_id": "TICKET-0001", "score": 0.1568, "preview": "...password reset...login..."}
  ],
  "latency_ms": 4,
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
  "latency_ms": 3
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

**Result**: 3 questions evaluated. All fail the confidence threshold with mock embeddings (avg confidence 0.1554, avg latency 3ms). Each question still retrieves relevant chunks — the mock provider just produces numerically low similarity scores.

```json
{
  "name": "demo-eval",
  "total_questions": 3,
  "passed_count": 0,
  "failed_count": 3,
  "average_confidence": 0.1554,
  "average_latency_ms": 3.0
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

**Result**: 5 total queries tracked, average confidence 0.1636, all queries below confidence threshold, 0% citation rate (expected with mock provider), $0.00 estimated cost.

```json
{
  "total_queries": 5,
  "average_confidence": 0.1636,
  "low_confidence_query_count": 5,
  "average_latency_ms": 3.2,
  "total_estimated_cost_usd": 0.0,
  "citation_rate": 0.0
}
```

## Notes on Mock vs OpenAI Provider

The mock provider uses deterministic MD5-based embeddings that produce numerically low cosine similarity scores (~0.15–0.25). This means:

- **All queries fall below the confidence threshold** (0.3) and return the fallback answer
- **Chunk retrieval still works** — relevant tickets are found and ranked
- **Citations are empty** because the confidence threshold gates citation generation

To get real AI-generated answers with citations:

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
export MOCK_PROVIDERS=false
export LLM_PROVIDER=openai
export EMBEDDING_PROVIDER=openai
```

Then re-upload tickets (they'll get real OpenAI embeddings) and query again.
