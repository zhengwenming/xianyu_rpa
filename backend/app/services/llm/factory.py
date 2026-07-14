"""LLM 工厂模式"""
from app.services.llm.base import LLMProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.anthropic_provider import AnthropicProvider
from app.services.llm.deepseek_provider import DeepSeekProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.models.llm_config import LLMConfig


class CustomProvider(OpenAIProvider):
    """自定义 OpenAI 兼容端点"""
    pass


class LLMFactory:
    """大模型工厂"""

    @staticmethod
    def create(config: LLMConfig) -> LLMProvider:
        providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "deepseek": DeepSeekProvider,
            "ollama": OllamaProvider,
            "custom": CustomProvider,
        }
        provider_class = providers.get(config.provider_type)
        if not provider_class:
            raise ValueError(f"不支持的提供商: {config.provider_type}")
        return provider_class(config)


# 全局 LLM 实例缓存
_llm_instance: LLMProvider = None


def get_llm() -> LLMProvider:
    """获取当前激活的 LLM 实例"""
    global _llm_instance
    if _llm_instance is None:
        raise RuntimeError("LLM 未配置，请先在设置中配置并激活一个 LLM")
    return _llm_instance


def set_llm(config: LLMConfig):
    """设置 LLM 实例"""
    global _llm_instance
    _llm_instance = LLMFactory.create(config)