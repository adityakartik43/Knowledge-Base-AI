import math
from unittest.mock import MagicMock

from app.config import Settings
from app.embeddings.service import EmbeddingService


def _vector(*values: float, dimension: int = 1536) -> list[float]:
    if values:
        return list(values) + [0.0] * (dimension - len(values))
    return [0.0] * dimension


def test_create_embeddings_batches_requests_and_requests_dimensions() -> None:
    settings = Settings(
        database_url="postgresql://localhost/test",
        service_api_key="secret",
        gemini_api_key="test-key",
        embedding_batch_size=2,
        embedding_dimension=1536,
    )
    service = EmbeddingService(settings=settings)

    first_response = MagicMock()
    first_response.data = [
        MagicMock(embedding=_vector(3.0, 4.0)),
        MagicMock(embedding=_vector(1.0, 0.0)),
    ]
    second_response = MagicMock()
    second_response.data = [MagicMock(embedding=_vector(0.0, 2.0))]

    service.client = MagicMock()
    service.client.embeddings.create.side_effect = [first_response, second_response]

    embeddings = service.create_embeddings(["a", "b", "c"])

    assert len(embeddings) == 3
    assert all(len(embedding) == 1536 for embedding in embeddings)
    assert service.client.embeddings.create.call_count == 2

    for call in service.client.embeddings.create.call_args_list:
        assert call.kwargs["dimensions"] == 1536
        assert call.kwargs["model"] == "gemini-embedding-001"


def test_create_embeddings_normalizes_truncated_vectors() -> None:
    settings = Settings(
        database_url="postgresql://localhost/test",
        service_api_key="secret",
        gemini_api_key="test-key",
        embedding_dimension=1536,
    )
    service = EmbeddingService(settings=settings)

    response = MagicMock()
    response.data = [MagicMock(embedding=_vector(3.0, 4.0))]
    service.client = MagicMock()
    service.client.embeddings.create.return_value = response

    embedding = service.create_embeddings(["hello"])[0]
    magnitude = math.sqrt(sum(value * value for value in embedding))

    assert len(embedding) == 1536
    assert abs(magnitude - 1.0) < 1e-6
