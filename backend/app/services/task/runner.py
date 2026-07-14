"""任务执行器"""
import asyncio
import json
from datetime import datetime
from app.database import async_session
from app.models.task import Task
from app.models.listing_log import ListingLog
from app.models.settings import GlobalSettings
from app.services.task.state import TaskStatus
from app.services.task.manager import task_manager
from app.services.listing.publisher import ListingPublisher
from app.services.listing.collector import ProductCollector
from app.services.listing.generator import ContentGenerator
from app.services.settings.manager import settings_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskRunner:
    """任务执行器 - 在独立 asyncio Task 中运行"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.publisher = ListingPublisher()
        self.collector = ProductCollector()
        self.generator = ContentGenerator()

    async def run(self):
        """任务执行主循环"""
        logger.info(f"任务执行器启动: {self.task_id}", extra={"task_id": self.task_id})

        try:
            async with async_session() as session:
                task = await session.get(Task, self.task_id)
                if not task:
                    logger.error(f"任务不存在: {self.task_id}")
                    return

                settings = await session.get(GlobalSettings, 1)
                if not settings:
                    settings = GlobalSettings(id=1)
                    session.add(settings)
                    await session.commit()

                # 检查取消
                if task_manager.is_cancelled(self.task_id):
                    await task_manager.on_task_completed(self.task_id, TaskStatus.CANCELLED.value)
                    return

                # 采集商品
                collected_products = await self._collect_products(task, settings)
                if not collected_products:
                    logger.warning(f"任务 {self.task_id} 未采集到商品")
                    await task_manager.on_task_completed(self.task_id, TaskStatus.FAILED.value)
                    return

                # 上架循环
                consecutive_count = 0
                for idx, product in enumerate(collected_products):
                    # 检查取消
                    if task_manager.is_cancelled(self.task_id):
                        await task_manager.on_task_completed(self.task_id, TaskStatus.CANCELLED.value)
                        return

                    # 检查暂停
                    pause_event = task_manager.get_pause_event(self.task_id)
                    await pause_event.wait()
                    if task_manager.is_cancelled(self.task_id):
                        await task_manager.on_task_completed(self.task_id, TaskStatus.CANCELLED.value)
                        return

                    # 检查是否达到目标数量
                    if task.current_count >= task.target_count:
                        logger.info(f"任务 {self.task_id} 达到目标上架数量 {task.target_count}")
                        break

                    # 供应商黑名单检查
                    if self._is_supplier_blocked(product, settings):
                        logger.info(f"商品供应商在黑名单中，跳过: {product.get('title', '')}")
                        continue

                    # 关键词屏蔽检查
                    if self._has_blocked_keywords(product, settings):
                        logger.info(f"商品命中关键词屏蔽，跳过: {product.get('title', '')}")
                        continue

                    # 执行单个商品上架
                    try:
                        success = await self._publish_one_product(task, product, settings)
                        if success:
                            task.current_count += 1
                            consecutive_count += 1
                        else:
                            task.fail_count += 1
                            consecutive_count = 0

                        task.progress = min(int(task.current_count / task.target_count * 100), 100)
                        await session.commit()

                        # 模拟暂停休息
                        if consecutive_count >= settings.simulated_pause_count:
                            pause_minutes = settings.simulated_pause_interval
                            logger.info(f"模拟休息中，暂停 {pause_minutes} 分钟...", extra={"task_id": self.task_id})
                            await asyncio.sleep(pause_minutes * 60)
                            consecutive_count = 0

                        # 上架后延迟
                        delay = settings.post_listing_delay
                        logger.info(f"等待 {delay} 秒后继续下一个...", extra={"task_id": self.task_id})
                        await asyncio.sleep(delay)

                    except Exception as e:
                        task.fail_count += 1
                        await session.commit()
                        logger.error(f"商品上架失败: {e}", extra={"task_id": self.task_id})
                        continue

                # 标记完成
                if task.current_count >= task.target_count:
                    await task_manager.on_task_completed(self.task_id, TaskStatus.COMPLETED.value)
                else:
                    await task_manager.on_task_completed(self.task_id, TaskStatus.COMPLETED.value)

        except Exception as e:
            logger.error(f"任务执行异常: {e}", extra={"task_id": self.task_id})
            await task_manager.on_task_completed(self.task_id, TaskStatus.FAILED.value)

    async def _collect_products(self, task: Task, settings: GlobalSettings) -> list[dict]:
        """采集商品"""
        products = []
        keywords = json.loads(task.keywords) if task.keywords else []
        source_urls = json.loads(task.source_urls) if task.source_urls else []

        # 从关键词采集
        for keyword in keywords:
            collected = await self.collector.collect_by_keyword(keyword, task.target_count)
            products.extend(collected)

        # 从URL采集
        for url in source_urls:
            product = await self.collector.collect_by_url(url)
            if product:
                products.append(product)

        return products

    async def _publish_one_product(self, task: Task, product: dict, settings: GlobalSettings) -> bool:
        """发布单个商品"""
        try:
            # 计算价格
            listing_price = product["price"] * settings.price_markup_ratio + settings.price_markup_amount
            import math
            listing_price = math.ceil(listing_price * 10) / 10  # 保留一位小数

            # 生成内容
            title = await self.generator.generate_title(product)
            description = await self.generator.generate_description(product, listing_price)

            # 处理图片
            images = product.get("images", [])
            if settings.enable_smart_crop_3_4:
                images = await self.generator.crop_images(images)

            # 生成短标题
            short_title = ""
            if settings.enable_ai_short_title:
                try:
                    short_title = await self.generator.generate_short_title(product)
                except Exception:
                    pass

            # 发布到闲鱼
            success = await self.publisher.publish(
                shop_id=task.shop_id,
                title=title,
                description=description,
                price=listing_price,
                image_urls=images,
                short_title=short_title,
            )

            # 记录上架日志
            await self._save_listing_log(task, product, title, listing_price, success)

            return success

        except Exception as e:
            logger.error(f"发布商品异常: {e}", extra={"task_id": self.task_id})
            await self._save_listing_log(task, product, product.get("title", ""), 0, False, str(e))
            return False

    async def _save_listing_log(self, task: Task, product: dict, title: str, price: float, success: bool, fail_reason: str = ""):
        """保存上架日志"""
        try:
            async with async_session() as session:
                log = ListingLog(
                    shop_id=task.shop_id,
                    shop_name=task.shop_name,
                    task_id=task.id,
                    product_title=title,
                    source_url=product.get("source_url", ""),
                    source_supplier=product.get("supplier", ""),
                    source_price=product.get("price", 0),
                    listing_price=price,
                    status="success" if success else "failed",
                    fail_reason=fail_reason,
                    listed_at=datetime.now() if success else None,
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.error(f"保存上架日志失败: {e}")

    def _is_supplier_blocked(self, product: dict, settings: GlobalSettings) -> bool:
        """检查供应商是否在黑名单中"""
        try:
            blacklist = json.loads(settings.supplier_blacklist) if settings.supplier_blacklist else []
            supplier = product.get("supplier", "")
            return supplier in blacklist
        except (json.JSONDecodeError, TypeError):
            return False

    def _has_blocked_keywords(self, product: dict, settings: GlobalSettings) -> bool:
        """检查是否命中关键词屏蔽"""
        try:
            blocklist = json.loads(settings.keyword_blocklist) if settings.keyword_blocklist else []
            title = product.get("title", "")
            for keyword in blocklist:
                if keyword in title:
                    return True
            return False
        except (json.JSONDecodeError, TypeError):
            return False