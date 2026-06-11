# Version Status

## V1 — MVP support intelligence platform

Status: ready to mark complete after the `complete-v1-validation` pull request CI is green and merged to `main`.

### Scope

V1 covers the original MVP:

- CSV upload
- Ticket validation
- Duplicate tracking
- Chunking
- Embeddings
- RAG answers with citations
- Low-confidence fallback
- Dashboard quality and retrieval metrics
- Eval runs
- React UI
- Docker startup
- Sample data generation
- README setup and demo flow

### Completion checklist

- [x] Required FastAPI routes are mounted.
- [x] CSV upload validates required columns and required fields.
- [x] CSV upload tracks invalid rows, duplicate ticket IDs, valid rows, and embedding failures.
- [x] Ticket text is chunked and embedded on upload.
- [x] Ticket list and ticket detail APIs work, including chunk previews.
- [x] RAG query returns answer, citations, confidence, query ID, latency, estimated cost, retrieved chunks, and quality scores.
- [x] Low-confidence/unrelated questions return the not-enough-context fallback with no citations.
- [x] Dashboard quality metrics report ingestion health.
- [x] Dashboard retrieval metrics report query health.
- [x] Eval runs can be created and listed.
- [x] Docker backend runs Alembic migrations before Uvicorn.
- [x] Sample data generator supports deterministic demo CSVs.
- [x] README includes setup, sample data, demo flow, API reference, and CI badge.
- [x] CI includes backend lint, backend typecheck, backend tests, frontend lint, frontend typecheck, frontend build.
- [x] CI includes clean Docker startup validation.
- [x] CI runs explicit V1 smoke validation from Docker.

### V1 validation command

```bash
docker compose down -v
docker compose up -d --build
python3 scripts/wait_for_api.py
python3 scripts/generate_sample_tickets.py --count 80 --include-invalid
python3 scripts/v1_api_smoke.py --base-url http://localhost:8000 --frontend-url http://localhost:5173 --csv scripts/sample_tickets.csv
```

### Notes

V1 is demo/portfolio complete. Later versions add reliability metrics, workflow integrations, and enterprise governance.
