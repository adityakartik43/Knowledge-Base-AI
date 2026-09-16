from openai import OpenAI

from app.config import Settings, get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class LlmService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.client = OpenAI(
            api_key=self.settings.gemini_api_key,
            base_url=self.settings.gemini_base_url,
        )

    @property
    def model_name(self) -> str:
        return self.settings.gemini_chat_model

    def generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.gemini_chat_model,
            messages=messages,
            temperature=temperature,
        )

        content = response.choices[0].message.content or ""
        logger.info("[LLM] Generated response (%s chars)", len(content))
        return content.strip()
