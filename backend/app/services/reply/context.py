"""会话上下文管理器"""
import json
from datetime import datetime, timedelta
from typing import Optional
from app.database import async_session
from app.models.conversation import Conversation
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationContext:
    """单店铺单用户的会话上下文（内存中）"""

    MAX_HISTORY = 20  # 最多保留最近 20 轮对话
    MAX_IDLE_MINUTES = 120  # 超过 2 小时无消息自动清理

    def __init__(self, shop_id: str, user_id: str):
        self.shop_id = shop_id
        self.user_id = user_id
        self.history: list[dict] = []
        self.product_id: Optional[str] = None
        self.product_info: Optional[dict] = None
        self.human_takeover: bool = False
        self.last_message_time: datetime = datetime.now()

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        self.last_message_time = datetime.now()
        if len(self.history) > self.MAX_HISTORY:
            self.history = self.history[-self.MAX_HISTORY:]

    def get_recent_history(self, count: int = 6) -> str:
        """获取最近 N 轮对话的文本表示"""
        recent = self.history[-count:]
        lines = []
        for msg in recent:
            role = "买家" if msg["role"] == "user" else "卖家"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def is_idle(self) -> bool:
        """检查是否空闲超时"""
        return (datetime.now() - self.last_message_time) > timedelta(minutes=self.MAX_IDLE_MINUTES)

    def to_dict(self) -> dict:
        return {
            "shop_id": self.shop_id,
            "user_id": self.user_id,
            "history": self.history[-10:],  # 只返回最近 10 条
            "product_id": self.product_id,
            "human_takeover": self.human_takeover,
            "last_message_time": self.last_message_time.isoformat(),
        }


class ContextManager:
    """会话上下文管理器 — 管理所有店铺所有用户的会话"""

    def __init__(self):
        self._contexts: dict[str, ConversationContext] = {}

    def _key(self, shop_id: str, user_id: str) -> str:
        return f"{shop_id}:{user_id}"

    def get_or_create(self, shop_id: str, user_id: str) -> ConversationContext:
        key = self._key(shop_id, user_id)
        if key not in self._contexts:
            self._contexts[key] = ConversationContext(shop_id, user_id)
        return self._contexts[key]

    def get(self, shop_id: str, user_id: str) -> Optional[ConversationContext]:
        key = self._key(shop_id, user_id)
        return self._contexts.get(key)

    def add_message(self, shop_id: str, user_id: str, role: str, content: str):
        ctx = self.get_or_create(shop_id, user_id)
        ctx.add_message(role, content)

    def get_all_sessions(self, shop_id: str = None) -> list[dict]:
        """获取所有会话列表"""
        sessions = []
        for key, ctx in self._contexts.items():
            if shop_id and ctx.shop_id != shop_id:
                continue
            sessions.append(ctx.to_dict())
        # 按最后消息时间排序
        sessions.sort(key=lambda x: x["last_message_time"], reverse=True)
        return sessions

    def cleanup_idle(self):
        """清理空闲超时的会话"""
        idle_keys = []
        for key, ctx in self._contexts.items():
            if ctx.is_idle():
                idle_keys.append(key)
        for key in idle_keys:
            del self._contexts[key]
        if idle_keys:
            logger.info(f"清理了 {len(idle_keys)} 个空闲会话")


# 全局实例
context_manager = ContextManager()