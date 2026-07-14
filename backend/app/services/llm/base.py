"""LLM Provider 抽象基类"""
from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """大模型提供商抽象基类"""

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        """对话接口"""
        ...

    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> bytes:
        """图片生成接口（如提供商不支持，抛出 NotImplementedError）"""
        ...

    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接是否正常"""
        ...