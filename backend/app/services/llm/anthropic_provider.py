"""Anthropic Provider"""
from typing import Optional
from anthropic import AsyncAnthropic
from app.services.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    def __init__(self, config):
        self.config = config
        self.client = AsyncAnthropic(
            api_key=config.api_key,
            base_url=config.api_base or "https://api.anthropic.com",
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        # Anthropic 消息格式转换
        system_msg = None
        converted_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                converted_messages.append({"role": msg["role"], "content": msg["content"]})

        response = await self.client.messages.create(
            model=kwargs.get("model", self.config.model),
            messages=converted_messages,
            system=system_msg,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", self.config.temperature),
        )
        return response.content[0].text if response.content else ""

    async def generate_image(self, prompt: str, **kwargs) -> bytes:
        raise NotImplementedError("Anthropic does not support image generation")

    async def test_connection(self) -> bool:
        try:
            await self.client.messages.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
            )
            return True
        except Exception:
            return False