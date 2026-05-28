from app.services.providers.mock import MockAnswerProvider, MockEmbeddingProvider


def test_mock_embedding_deterministic():
    provider = MockEmbeddingProvider()
    emb1 = provider.embed_texts(["hello world"])
    emb2 = provider.embed_texts(["hello world"])
    assert emb1 == emb2


def test_mock_embedding_different_inputs():
    provider = MockEmbeddingProvider()
    emb1 = provider.embed_texts(["hello"])
    emb2 = provider.embed_texts(["world"])
    assert emb1 != emb2


def test_mock_answer_with_contexts():
    provider = MockAnswerProvider()
    contexts = [
        {"ticket_id": "T-1", "text": "Login failed for user"},
        {"ticket_id": "T-2", "text": "Password reset not working"},
    ]
    answer = provider.generate_answer("How to fix login?", contexts)
    assert "[T-1]" in answer
    assert "[T-2]" in answer


def test_mock_answer_no_context():
    provider = MockAnswerProvider()
    answer = provider.generate_answer("How to fix login?", [])
    assert "enough context" in answer.lower()


def test_mock_embedding_cost_zero():
    provider = MockEmbeddingProvider()
    assert provider.estimated_cost(1000) == 0.0


def test_mock_answer_cost_zero():
    provider = MockAnswerProvider()
    assert provider.estimated_cost(1000) == 0.0
