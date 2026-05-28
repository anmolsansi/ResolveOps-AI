from app.services.providers.base import AnswerProvider, EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("OpenAI embedding provider requires openai package and API key")

    def estimated_cost(self, num_tokens: int) -> float:
        return num_tokens * 0.0001 / 1000


class OpenAIAnswerProvider(AnswerProvider):
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def generate_answer(self, question: str, contexts: list[dict[str, str]]) -> str:
        raise NotImplementedError("OpenAI answer provider requires openai package and API key")

    def estimated_cost(self, num_tokens: int) -> float:
        return num_tokens * 0.003 / 1000
