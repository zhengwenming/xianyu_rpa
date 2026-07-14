"""DeepSeek Provider - 使用 OpenAI SDK 配兼容端点"""
from openai import AsyncOpenAI
from app.services.llm.base import LLMProvider


class DeepSeekProvider(LLMProvider):
    DEEPSEEK_BASE = "https://api.deepseek.com"

    def __init__(self, config):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base or self.DEEPSEEK_BASE,
        )

    async def chat(self, messages: list[dict], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.config.model or "deepseek-chat"),
            messages=messages,
            temperature=kwargs.get("temperature", self.config.temperature),
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
        )
        return response.choices[0].message.content or ""

    async def generate_image(self, prompt: str, **kwargs) -> bytes:
        raise NotImplementedError("DeepSeek does not support image generation")

    async def test_connection(self) -> bool:
        try:
            await self.chat([{"role": "user", "content": "test"}])
            return True
        except Exception:
            return False