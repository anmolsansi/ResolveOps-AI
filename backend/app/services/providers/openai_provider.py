"""OpenAI provider implementation.

Requires the `openai` package: pip install openai
Set OPENAI_API_KEY, EMBEDDING_PROVIDER=openai, LLM_PROVIDER=openai, MOCK_PROVIDERS=false
to activate.

NOTE: This provider is functional but not included in the default dependency set.
To use it, install the openai package and configure the environment variables above.
"""

from __future__ import annotations

from app.services.providers.base import AnswerProvider, EmbeddingProvider

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
CHAT_MODEL = "gpt-4o-mini"


class OpenAIEmbeddingProvider(EmbeddingProvider):
    name = "openai"
    model = EMBEDDING_MODEL

    def __init__(self, api_key: str) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package is required for OpenAI provider. "
                "Install it with: pip install openai"
            ) from exc
        self._client = OpenAI(api_key=api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def estimated_cost(self, num_tokens: int) -> float:
        return num_tokens * 0.00002 / 1000


class OpenAIAnswerProvider(AnswerProvider):
    name = "openai"
    model = CHAT_MODEL

    def __init__(self, api_key: str) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package is required for OpenAI provider. "
                "Install it with: pip install openai"
            ) from exc
        self._client = OpenAI(api_key=api_key)

    def generate_answer(self, question: str, contexts: list[dict[str, str]]) -> str:
        if not contexts:
            return (
                "I don't have enough context to answer this question. "
                "Please upload more support tickets or try a different query."
            )

        context_block = "\n\n".join(
            f"[{ctx.get('ticket_id', 'unknown')}]: {ctx.get('text', '')}"
            for ctx in contexts
        )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a support intelligence assistant. Answer questions using "
                    "ONLY the provided ticket context. Always cite source ticket IDs "
                    "in square brackets like [TICKET-123]. If the context doesn't "
                    "contain enough information, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context from support tickets:\n{context_block}\n\n"
                    f"Question: {question}"
                ),
            },
        ]

        response = self._client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.2,
            max_tokens=512,
        )
        return response.choices[0].message.content or ""

    def estimated_cost(self, num_tokens: int) -> float:
        return num_tokens * 0.00015 / 1000
