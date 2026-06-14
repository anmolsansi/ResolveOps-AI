from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://resolveops:resolveops@localhost:5432/resolveops"
    backend_port: int = 8000
    openai_api_key: str = ""
    llm_provider: str = "mock"
    embedding_provider: str = "mock"
    mock_providers: bool = True
    low_confidence_threshold: float = 0.3
    default_top_k: int = 5

    # V5 — security & governance
    secret_key: str = "dev-insecure-change-me"
    access_token_expire_minutes: int = 720
    auth_required: bool = False
    # V5 — retrieval backend: "auto" (pgvector on Postgres, else memory),
    # "pgvector", or "memory"
    vector_backend: str = "auto"
    # V5 — PII redaction on ingestion (can be overridden at runtime via settings)
    pii_redaction_enabled: bool = False
    # V5 — retention policy defaults (days; 0 disables purge for that resource)
    retention_rag_query_days: int = 0
    retention_audit_log_days: int = 0

    # V6 — customer-facing widget
    widget_api_key: str = "dev-widget-key"
    escalation_confidence_threshold: float = 0.3
    escalation_sentiment_keywords: list[str] = [
        "angry", "furious", "unacceptable", "lawsuit", "cancel",
        "refund", "terrible", "worst", "disgusted", "outraged",
    ]
    policy_sensitive_keywords: list[str] = [
        "legal", "attorney", "sue", "regulatory", "compliance", "lawyer",
    ]

    # V7 — action-taking agent workflows
    tool_auto_register: bool = True
    tool_max_executions_per_conversation: int = 5

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
