# ResolveOps AI Demo

This demo proves the V2 path: local startup, CSV ingestion, cited RAG, low-confidence fallback, eval export, dashboard metrics, retrieval debug, and optional real-provider configuration.

## Fast path with Docker

```bash
cp .env.example .env
docker compose up -d --build
```

Wait for the backend health check:

```bash
curl -sf http://localhost:8000/health
```

Expected response:

```json
{"status":"ok","service":"resolveops-api"}
```

Generate sample tickets:

```bash
python3 scripts/generate_sample_tickets.py --count 80
```

Run the V2 smoke validation:

```bash
python3 scripts/v2_api_smoke.py --base-url http://localhost:8000 --csv scripts/sample_tickets.csv
```

Expected final line:

```text
V2 smoke validation passed
```

## Manual API demo

Upload sample tickets:

```bash
curl -sf -X POST http://localhost:8000/tickets/upload -F "file=@scripts/sample_tickets.csv"
```

The response should include a positive `valid_count`, zero mock-mode embedding failures, and one ingestion batch ID.

Ask a cited support question:

```bash
curl -sf -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Customer has a duplicate invoice charge and needs a billing refund. What fixed this before?","top_k":5}'
```

The response should include:

- `citations` with at least one ticket ID.
- `confidence` at or above the fallback threshold.
- `retrieved_chunks` with debug details.
- `quality` scores.

Ask a low-confidence question:

```bash
curl -sf -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Give me a chocolate cake frosting recipe with bananas and cinnamon.","top_k":3}'
```

The response should include:

- `is_fallback: true`
- empty `citations`
- an answer that says there is not enough context

Run an eval:

```bash
curl -sf -X POST http://localhost:8000/eval/run \
  -H "Content-Type: application/json" \
  -d '{"name":"manual-v2-demo"}'
```

Export an eval run by replacing `<run_id>` with the returned ID:

```bash
curl -sf "http://localhost:8000/eval/runs/<run_id>/export?format=json"
curl -sf "http://localhost:8000/eval/runs/<run_id>/export?format=csv"
```

Verify dashboard data:

```bash
curl -sf http://localhost:8000/dashboard/quality
curl -sf http://localhost:8000/dashboard/retrieval
curl -sf http://localhost:8000/dashboard/charts
curl -sf http://localhost:8000/dashboard/cost
curl -sf http://localhost:8000/dashboard/failed-queries
```

## Frontend demo order

Open:

```text
http://localhost:5173
```

Then demo these pages in order:

1. Upload: upload `scripts/sample_tickets.csv`, review counts, and download invalid rows when using `--include-invalid`.
2. Tickets: browse tickets and open a ticket detail page.
3. RAG Playground: ask the billing question, show cited ticket IDs, and open a cited source ticket.
4. RAG Playground: expand Retrieval Debug and explain cosine score, keyword boost, keyword hits, and matched tokens.
5. RAG Playground: send feedback using Helpful, Not helpful, or Wrong citation.
6. RAG Playground: ask the unrelated cake question and show the insufficient-context fallback.
7. Eval Runs: run an eval and export JSON or CSV.
8. Dashboard: review ingestion quality, retrieval metrics, and charts.
9. Reliability: review quality metrics, cost, failed queries, and regression comparison.

## Real provider demo

Mock mode is default and free. To run with a real provider locally:

```bash
cd backend
pip install -e ".[dev,openai]"
export MOCK_PROVIDERS=false
export LLM_PROVIDER=openai
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY=<set-this-in-your-shell>
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Keep provider credentials in your local shell or `.env`. Do not commit them.

## Cleanup

```bash
docker compose down -v
```
