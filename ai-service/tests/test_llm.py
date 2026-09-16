from unittest.mock import MagicMock

from app.config import Settings
from app.llm.service import LlmService


def test_llm_service_uses_gemini_chat_model() -> None:
    settings = Settings(
        database_url="postgresql://localhost/test",
        service_api_key="secret",
        gemini_api_key="test-key",
        gemini_chat_model="gemini-2.5-flash",
    )
    service = LlmService(settings=settings)

    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content="Answer text"))]
    service.client = MagicMock()
    service.client.chat.completions.create.return_value = response

    answer = service.generate_chat_completion(
        messages=[{"role": "user", "content": "Hello"}]
    )

    assert answer == "Answer text"
    assert service.model_name == "gemini-2.5-flash"
    service.client.chat.completions.create.assert_called_once_with(
        model="gemini-2.5-flash",
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.2,
    )
