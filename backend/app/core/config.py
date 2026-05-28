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

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
