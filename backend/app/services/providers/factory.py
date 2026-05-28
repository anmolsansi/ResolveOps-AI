from app.core.config import settings
from app.services.providers.base import AnswerProvider, EmbeddingProvider
from app.services.providers.mock import MockAnswerProvider, MockEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    if settings.mock_providers or settings.embedding_provider == "mock":
        return MockEmbeddingProvider()
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        from app.services.providers.openai_provider import OpenAIEmbeddingProvider

        return OpenAIEmbeddingProvider(settings.openai_api_key)
    return MockEmbeddingProvider()


def get_answer_provider() -> AnswerProvider:
    if settings.mock_providers or settings.llm_provider == "mock":
        return MockAnswerProvider()
    if settings.llm_provider == "openai" and settings.openai_api_key:
        from app.services.providers.openai_provider import OpenAIAnswerProvider

        return OpenAIAnswerProvider(settings.openai_api_key)
    return MockAnswerProvider()
