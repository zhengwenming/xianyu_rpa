"""消息路由处理器"""
from app.services.xianyu_ws.message import XianyuMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MessageHandler:
    """消息处理器 - 路由到对应的回复引擎"""

    def __init__(self):
        self._reply_engine = None

    def set_reply_engine(self, reply_engine):
        self._reply_engine = reply_engine

    async def handle(self, message: XianyuMessage):
        """处理收到的消息"""
        # 过滤系统消息
        if message.message_type == "system_card":
            logger.debug(f"忽略系统卡片消息: {message.content[:50]}")
            return

        if not message.sender_id:
            logger.debug("忽略无发送者消息")
            return

        # 路由到回复引擎
        if self._reply_engine:
            await self._reply_engine.handle(message.shop_id, message)
        else:
            logger.warning(f"回复引擎未设置，消息未处理: {message.content[:50]}")


# 全局实例
message_handler = MessageHandler()