# V2 Completion Checklist

V2 turns the original vertical slice into a portfolio-ready demo. It focuses on validation, demo reliability, provider setup, retrieval transparency, and UI polish.

## Completion criteria

- CI runs backend lint, backend typecheck, backend tests, frontend lint, frontend typecheck, frontend build, and Docker smoke validation.
- Backend typecheck is blocking in CI.
- Docker startup runs migrations before serving traffic.
- A generated CSV can be uploaded through the API and frontend.
- A support question returns cited source ticket IDs.
- An unrelated question returns the insufficient-context fallback.
- Retrieval debug details are visible for each returned chunk.
- Eval runs can be created and exported.
- Dashboard chart data is available after ingestion and RAG queries.
- OpenAI provider setup is documented, while mock mode remains the default free local path.
- The demo path can be run without paid services.

## CI coverage

The GitHub Actions workflow includes three jobs:

1. `backend`
   - Installs backend dev dependencies.
   - Runs Ruff.
   - Runs mypy as a blocking check.
   - Runs pytest.

2. `frontend`
   - Installs frontend dependencies with `npm ci`.
   - Runs lint.
   - Runs TypeScript typecheck.
   - Builds the production frontend bundle.

3. `docker-smoke`
   - Builds and starts Docker Compose.
   - Waits for backend readiness.
   - Generates sample support tickets.
   - Uploads the sample CSV.
   - Runs a cited RAG query.
   - Runs a low-confidence fallback query.
   - Creates and exports an eval run.
   - Verifies dashboard quality, retrieval, and chart endpoints.

## Manual V2 demo path

Run the app:

```bash
docker compose up -d --build
```

Generate tickets:

```bash
python3 scripts/generate_sample_tickets.py --count 80
```

Run the API smoke path:

```bash
python3 scripts/v2_api_smoke.py --base-url http://localhost:8000 --csv scripts/sample_tickets.csv
```

Open the frontend:

```text
http://localhost:5173
```

Recommended UI demo order:

1. Upload `scripts/sample_tickets.csv` on the Upload page.
2. Review ingestion counts and invalid-row export behavior.
3. Browse uploaded tickets and open one ticket detail page.
4. Ask a billing-support question in the RAG Playground.
5. Click a cited ticket ID to verify the source ticket.
6. Expand Retrieval Debug and show cosine score, keyword boost, hits, and matched tokens.
7. Submit feedback on the answer.
8. Ask an unrelated question to show the fallback answer.
9. Run an eval and export the result.
10. Open Dashboard and Reliability pages to show charts, quality scores, cost, and failed-query review data.

## OpenAI provider setup

Mock mode is the default and requires no API key. To test real provider mode locally:

```bash
cd backend
pip install -e ".[dev,openai]"
export MOCK_PROVIDERS=false
export LLM_PROVIDER=openai
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY="your-key"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

The OpenAI provider uses:

- Embeddings: `text-embedding-3-small`
- Answer generation: `gpt-4o-mini`

Do not commit API keys. Keep `.env` local.

## V2 boundaries

V2 does not include enterprise auth, real support-tool API credentials, background workers, cloud deployment, or pgvector. Those belong to later phases.
