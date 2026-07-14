"""闲鱼自动下架服务"""
from datetime import datetime
from typing import Optional
from app.database import async_session
from app.models.delisting_log import DelistingLog
from app.services.browser.xianyu import xianyu_page
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DelistService:
    """下架服务"""

    async def delist_product(
        self,
        shop_id: str,
        item_id: str,
        product_title: str = "",
        reason: str = "manual",
        is_auto: bool = False,
    ) -> bool:
        """下架单个商品"""
        success = await xianyu_page.delist_product(shop_id, item_id)

        # 记录下架日志
        await self._save_delisting_log(
            shop_id=shop_id,
            item_id=item_id,
            product_title=product_title,
            reason=reason,
            is_auto=is_auto,
            success=success,
        )

        return success

    async def batch_delist(
        self,
        shop_id: str,
        items: list[dict],
        reason: str = "manual",
    ) -> list[dict]:
        """批量下架商品"""
        results = []
        for item in items:
            success = await self.delist_product(
                shop_id=shop_id,
                item_id=item["item_id"],
                product_title=item.get("title", ""),
                reason=reason,
                is_auto=False,
            )
            results.append({"item_id": item["item_id"], "success": success})
        return results

    async def _save_delisting_log(
        self,
        shop_id: str,
        item_id: str,
        product_title: str,
        reason: str,
        is_auto: bool,
        success: bool,
    ):
        """保存下架日志"""
        try:
            async with async_session() as session:
                log = DelistingLog(
                    shop_id=shop_id,
                    product_title=product_title,
                    xianyu_item_id=item_id,
                    delist_reason=reason,
                    delist_type="auto" if is_auto else "manual",
                    delisted_at=datetime.now() if success else None,
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"保存下架日志失败: {e}")

    async def auto_delist_sold_out(self, shop_id: str, item_ids: list[str]) -> list[dict]:
        """自动下架已售罄商品"""
        results = []
        for item_id in item_ids:
            success = await self.delist_product(
                shop_id=shop_id,
                item_id=item_id,
                reason="sold_out",
                is_auto=True,
            )
            results.append({"item_id": item_id, "success": success})
        return results


# 全局实例
delist_service = DelistService()