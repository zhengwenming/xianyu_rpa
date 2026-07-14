"""Ollama Provider - 本地模型"""
from openai import AsyncOpenAI
from app.services.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    OLLAMA_BASE = "http://localhost:11434/v1"

    def __init__(self, config):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key or "ollama",
            base_url=config.api_base or self.OLLAMA_BASE,
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.config.model or "llama3"),
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        return response.choices[0].message.content or ""

    async def generate_image(self, prompt: str, **kwargs) -> bytes:
        raise NotImplementedError("Ollama does not support image generation")

    async def test_connection(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False