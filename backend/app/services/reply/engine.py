"""自动回复引擎主逻辑"""
import asyncio
from typing import Optional
from app.services.reply.context import context_manager, ConversationContext
from app.services.reply.classifier import intent_classifier
from app.services.reply.experts import expert_router
from app.services.xianyu_ws.connection_manager import connection_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReplyEngine:
    """自动回复引擎"""

    # 人工接管切换关键词
    TAKEOVER_KEYWORDS = ["。", "."]

    def __init__(self):
        self.settings = type("Settings", (), {"simulate_human_typing": True})()

    async def handle(self, shop_id: str, message):
        """处理收到的消息"""
        user_id = message.sender_id
        user_message = message.content
        product_id = message.product_id

        if not user_id or not user_message:
            return

        # 1. 获取/创建会话上下文
        ctx = context_manager.get_or_create(shop_id, user_id)

        # 2. 人工接管检查
        if ctx.human_takeover:
            logger.info(f"人工接管模式，不自动回复: {user_id}")
            return

        # 3. 接管切换关键词检测
        if user_message.strip() in self.TAKEOVER_KEYWORDS:
            ctx.human_takeover = not ctx.human_takeover
            status = "开启" if ctx.human_takeover else "关闭"
            await self._send(shop_id, user_id, f"已{status}人工接管模式")
            return

        # 4. 过滤系统消息
        if message.message_type == "system_card":
            return

        # 5. 加载商品信息
        if product_id and product_id != ctx.product_id:
            ctx.product_id = product_id
            ctx.product_info = {"product_id": product_id, "title": "商品", "price": "面议"}

        # 6. 记录用户消息
        context_manager.add_message(shop_id, user_id, "user", user_message)

        # 7. 意图分类
        intent = await intent_classifier.classify(ctx, user_message)
        logger.info(f"意图分类: {intent} (用户: {user_id})")

        # 8. 路由到对应专家生成回复
        expert_name = expert_router.EXPERTS.get(intent, "default_expert")
        reply = await expert_router.generate_reply(expert_name, ctx, user_message)

        # 9. 模拟人工回复延迟
        if self.settings.simulate_human_typing:
            delay = min(len(reply) * 0.1, 5)
            await asyncio.sleep(delay)

        # 10. 发送回复
        await self._send(shop_id, user_id, reply)

        # 11. 记录回复到上下文
        context_manager.add_message(shop_id, user_id, "assistant", reply)

        # 12. 记录日志
        logger.info(f"自动回复 [{intent}] -> {user_id}: {reply[:50]}...",
                    extra={"shop_id": shop_id, "task_id": f"reply_{shop_id}"})

    async def _send(self, shop_id: str, user_id: str, text: str):
        """发送消息"""
        try:
            await connection_manager.send_message(shop_id, user_id, text)
        except Exception as e:
            logger.error(f"发送回复失败: {e}")


# 全局实例
reply_engine = ReplyEngine()