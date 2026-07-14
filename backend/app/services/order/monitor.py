"""订单监控器 - 通过 HTTP API 轮询待发货订单"""
import json
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import async_session
from app.models.shop import Shop
from app.models.delivery import DeliveryLog
from app.services.order.shipper import shipper
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OrderMonitor:
    """闲鱼订单监控器 — 通过 HTTP API 轮询待发货订单"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._running = False

    def start(self):
        """启动定时任务"""
        if self._running:
            return
        self.scheduler.add_job(
            self._check_orders,
            "interval",
            seconds=settings.ORDER_POLL_INTERVAL,
            id="order_check",
            replace_existing=True,
        )
        self.scheduler.start()
        self._running = True
        logger.info("订单监控器已启动")

    def stop(self):
        """停止定时任务"""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("订单监控器已停止")

    async def _check_orders(self):
        """检查所有已授权店铺的待发货订单"""
        async with async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(Shop).where(Shop.login_status == "authorized")
            )
            shops = result.scalars().all()

        for shop in shops:
            try:
                # 模拟获取待发货订单（实际需要调用闲鱼 HTTP API）
                orders = await self._fetch_pending_orders(shop)
                for order in orders:
                    await self._process_order(shop, order)
            except Exception as e:
                logger.error(f"[{shop.name}] 订单检查失败: {e}")

    async def _fetch_pending_orders(self, shop: Shop) -> list[dict]:
        """调用闲鱼 HTTP API 获取待发货订单（模拟实现）"""
        # 实际需要调用闲鱼 API，这里返回模拟数据
        # TODO: 实现真实的闲鱼订单 API 调用
        logger.info(f"检查店铺 {shop.name} 的待发货订单")
        return []

    async def _process_order(self, shop: Shop, order: dict):
        """处理单个订单"""
        try:
            success = await shipper.ship(shop, order)
            if success:
                logger.info(f"订单自动发货成功: {order.get('order_id', '')}")
            else:
                logger.warning(f"订单自动发货失败: {order.get('order_id', '')}")
        except Exception as e:
            logger.error(f"订单处理异常: {e}")


# 全局实例
order_monitor = OrderMonitor()