"""自动发货执行器"""
import json
from typing import Optional
from datetime import datetime
from app.database import async_session
from app.models.delivery import DeliveryConfig, DeliveryLog
from app.services.xianyu_ws.connection_manager import connection_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class Shipper:
    """自动发货执行器"""

    async def ship(self, shop, order: dict) -> bool:
        """执行发货"""
        product_id = order.get("product_id", "")
        if not product_id:
            logger.error("订单无商品ID")
            return False

        # 获取发货配置
        config = await self._get_delivery_config(shop.id, product_id)
        if not config:
            logger.warning(f"商品 {product_id} 未配置发货内容")
            return False

        if not config.auto_ship:
            logger.info(f"商品 {product_id} 未开启自动发货")
            return False

        # 根据类型发货
        try:
            if config.delivery_type == "card":
                return await self._ship_card(shop, order, config)
            elif config.delivery_type == "link":
                return await self._ship_link(shop, order, config)
            elif config.delivery_type == "text":
                return await self._ship_text(shop, order, config)
            elif config.delivery_type == "proxy":
                return await self._ship_proxy(shop, order, config)
            else:
                logger.error(f"未知发货类型: {config.delivery_type}")
                return False
        except Exception as e:
            logger.error(f"发货失败: {e}")
            await self._log_delivery(shop.id, order, config.delivery_type, "failed", str(e))
            return False

    async def _get_delivery_config(self, shop_id: str, product_id: str) -> Optional[DeliveryConfig]:
        """获取发货配置"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(DeliveryConfig).where(
                    DeliveryConfig.shop_id == shop_id,
                    DeliveryConfig.product_id == product_id,
                )
            )
            return result.scalar_one_or_none()

    async def _pop_card(self, product_id: str) -> Optional[str]:
        """从卡池取出一张卡密"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(DeliveryConfig).where(DeliveryConfig.product_id == product_id)
            )
            config = result.scalar_one_or_none()
            if not config or not config.card_pool:
                return None

            cards = json.loads(config.card_pool)
            if not cards:
                return None

            card = cards.pop(0)
            config.card_pool = json.dumps(cards, ensure_ascii=False)
            await session.commit()
            return card

    async def _ship_card(self, shop, order: dict, config: DeliveryConfig) -> bool:
        """卡券发货"""
        card = await self._pop_card(config.product_id)
        if not card:
            logger.warning(f"商品 {config.product_title} 卡池已耗尽")
            return False

        message = f"您的卡密：{card}\n请妥善保管，如有问题随时联系~"
        await self._send_to_buyer(shop.id, order, message)
        await self._log_delivery(shop.id, order, "card", "success", f"卡密已发送: {card[:10]}...")
        return True

    async def _ship_link(self, shop, order: dict, config: DeliveryConfig) -> bool:
        """网盘链接发货"""
        message = f"资源链接：{config.link_url}\n提取码：{config.link_code}"
        await self._send_to_buyer(shop.id, order, message)
        await self._log_delivery(shop.id, order, "link", "success")
        return True

    async def _ship_text(self, shop, order: dict, config: DeliveryConfig) -> bool:
        """纯文本发货"""
        await self._send_to_buyer(shop.id, order, config.text_content or "")
        await self._log_delivery(shop.id, order, "text", "success")
        return True

    async def _ship_proxy(self, shop, order: dict, config: DeliveryConfig) -> bool:
        """1688 代发（暂未实现完整流程）"""
        logger.warning(f"1688 代发功能需浏览器自动化配合，暂未完整实现")
        await self._log_delivery(shop.id, order, "proxy", "pending", "代发功能待实现")
        return False

    async def _send_to_buyer(self, shop_id: str, order: dict, message: str):
        """通过 WebSocket 发送消息给买家"""
        try:
            buyer_id = order.get("buyer_id", "")
            if buyer_id:
                await connection_manager.send_message(shop_id, buyer_id, message)
        except Exception as e:
            logger.error(f"发送消息给买家失败: {e}")

    async def _log_delivery(self, shop_id: str, order: dict, delivery_type: str, status: str, error: str = ""):
        """记录发货日志"""
        try:
            async with async_session() as session:
                log = DeliveryLog(
                    shop_id=shop_id,
                    order_id=order.get("order_id", ""),
                    product_id=order.get("product_id", ""),
                    product_title=order.get("product_title", ""),
                    buyer_id=order.get("buyer_id", ""),
                    delivery_type=delivery_type,
                    status=status,
                    error_message=error,
                    shipped_at=datetime.now() if status == "success" else None,
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"记录发货日志失败: {e}")


# 全局实例
shipper = Shipper()