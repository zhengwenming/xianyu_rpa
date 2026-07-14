"""虚拟商品发货 - 卡券/网盘链接/激活码"""
import json
from typing import Optional
from app.database import async_session
from app.models.delivery import DeliveryConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VirtualGoodsShipper:
    """虚拟商品自动发货"""

    async def get_card_pool(self, product_id: str) -> list[str]:
        """查看商品卡池库存"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(DeliveryConfig).where(DeliveryConfig.product_id == product_id)
            )
            config = result.scalar_one_or_none()
            if not config or not config.card_pool:
                return []
            return json.loads(config.card_pool)

    async def add_cards(self, product_id: str, cards: list[str]) -> bool:
        """补充卡池"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(DeliveryConfig).where(DeliveryConfig.product_id == product_id)
            )
            config = result.scalar_one_or_none()
            if not config:
                logger.error(f"商品 {product_id} 未配置发货内容")
                return False

            existing = json.loads(config.card_pool) if config.card_pool else []
            existing.extend(cards)
            config.card_pool = json.dumps(existing, ensure_ascii=False)
            await session.commit()
            logger.info(f"商品 {product_id} 卡池补充了 {len(cards)} 张卡密")
            return True


# 全局实例
virtual_goods_shipper = VirtualGoodsShipper()