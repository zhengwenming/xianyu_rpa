"""OpenAI Provider"""
from typing import Optional
from openai import AsyncOpenAI
from app.services.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self, config):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base or "https://api.openai.com/v1",
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.config.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        return response.choices[0].message.content or ""

    async def generate_image(self, prompt: str, **kwargs) -> bytes:
        response = await self.client.images.generate(
            model=kwargs.get("model", self.config.image_model or "dall-e-3"),
            prompt=prompt,
            size=kwargs.get("size", "1024x1024"),
            response_format="b64_json",
        )
        import base64
        return base64.b64decode(response.data[0].b64_json)

    async def test_connection(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False