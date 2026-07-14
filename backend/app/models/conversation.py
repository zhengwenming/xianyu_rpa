"""会话上下文模型"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from app.database import Base
from app.utils.helpers import generate_uuid, now


class Conversation(Base):
    """会话上下文 - 持久化到数据库"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    user_nickname = Column(String(100), nullable=True)
    history = Column(Text, nullable=True, comment="对话历史（JSON数组）")
    product_id = Column(String(100), nullable=True, comment="当前讨论的商品ID")
    product_info = Column(Text, nullable=True, comment="商品信息缓存（JSON）")
    human_takeover = Column(Boolean, default=False, comment="人工接管模式")
    last_message_time = Column(DateTime, nullable=True, comment="最后消息时间")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    def to_dict(self):
        return {
            "id": self.id,
            "shop_id": self.shop_id,
            "user_id": self.user_id,
            "user_nickname": self.user_nickname,
            "human_takeover": self.human_takeover,
            "last_message_time": self.last_message_time.isoformat() if self.last_message_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }