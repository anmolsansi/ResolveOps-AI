from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    name: str = "unknown"
    model: str = "unknown"

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        ...

    @abstractmethod
    def estimated_cost(self, num_tokens: int) -> float:
        ...


class AnswerProvider(ABC):
    name: str = "unknown"
    model: str = "unknown"

    @abstractmethod
    def generate_answer(self, question: str, contexts: list[dict[str, str]]) -> str:
        ...

    @abstractmethod
    def estimated_cost(self, num_tokens: int) -> float:
        ...
