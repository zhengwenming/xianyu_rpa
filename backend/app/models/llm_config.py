"""LLM 配置模型"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text
from app.database import Base
from app.utils.helpers import generate_uuid, now


class LLMConfig(Base):
    __tablename__ = "llm_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, comment="配置名称")
    provider_type = Column(String(30), nullable=False, comment="openai/anthropic/deepseek/ollama/custom")
    api_key = Column(Text, nullable=True, comment="API密钥（加密存储）")
    api_base = Column(String(500), nullable=True, comment="API端点")
    model = Column(String(100), nullable=False, comment="模型名称")
    temperature = Column(Float, default=0.7, comment="温度参数")
    max_tokens = Column(Integer, default=2048, comment="最大token数")
    image_model = Column(String(100), nullable=True, comment="图片生成模型")
    is_active = Column(Boolean, default=False, comment="是否当前激活")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "provider_type": self.provider_type,
            "api_key": "***" + (self.api_key[-4:] if self.api_key and len(self.api_key) > 4 else ""),
            "api_base": self.api_base,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "image_model": self.image_model,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }