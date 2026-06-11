import hashlib
import math

from app.services.providers.base import AnswerProvider, EmbeddingProvider

MOCK_EMBEDDING_DIM = 128


class MockEmbeddingProvider(EmbeddingProvider):
    name = "mock"
    model = "mock-embedding-v1"

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._deterministic_embedding(t) for t in texts]

    def estimated_cost(self, num_tokens: int) -> float:
        return 0.0

    @staticmethod
    def _deterministic_embedding(text: str) -> list[float]:
        values: list[float] = []
        seed = text.encode("utf-8")
        for i in range(MOCK_EMBEDDING_DIM):
            h = hashlib.md5(seed + i.to_bytes(4, "little")).hexdigest()
            val = (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1
            values.append(val)
        norm = math.sqrt(sum(v * v for v in values))
        if norm < 1e-10:
            return values
        return [v / norm for v in values]


class MockAnswerProvider(AnswerProvider):
    name = "mock"
    model = "mock-answer-v1"

    def generate_answer(
        self,
        question: str,
        contexts: list[dict[str, str]],
        system_prompt: str | None = None,
    ) -> str:
        if not contexts:
            return (
                "I don't have enough context to answer this question. "
                "Please upload more support tickets or try a different query."
            )
        ticket_ids = [ctx.get("ticket_id", "unknown") for ctx in contexts]
        unique_ids = list(dict.fromkeys(ticket_ids))
        citations = ", ".join(f"[{tid}]" for tid in unique_ids[:5])
        summaries = []
        for ctx in contexts[:3]:
            preview = ctx.get("text", "")[:200]
            summaries.append(preview)
        summary_text = " | ".join(summaries)
        return (
            f"Based on historical support tickets, here is a summary: {summary_text}. "
            f"Sources: {citations}"
        )

    def estimated_cost(self, num_tokens: int) -> float:
        return 0.0
