"""闲鱼页面操作封装 - 上架/下架表单"""
import random
from typing import Optional
from playwright.async_api import Page
from app.services.browser.manager import browser_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class XianyuPage:
    """闲鱼页面操作封装"""

    LISTING_URL = "https://www.goofish.com/h5/publish"
    MY_ITEMS_URL = "https://www.goofish.com/h5/my/sell"

    async def publish_product(
        self,
        shop_id: str,
        title: str,
        description: str,
        price: float,
        image_paths: list[str],
        category: str = "",
        short_title: str = "",
        video_path: str = "",
    ) -> bool:
        """发布商品到闲鱼"""
        ctx = await browser_manager.get_context(shop_id, headless=True)
        page = await ctx.new_page()
        try:
            await page.goto(self.LISTING_URL, wait_until="networkidle", timeout=60000)
            await browser_manager.human_delay(2, 4)

            # 填入标题
            await page.fill('input[placeholder*="标题"]', title)
            await browser_manager.human_delay()

            # 填入短标题（如果有）
            if short_title:
                try:
                    await page.fill('input[placeholder*="短标题"]', short_title)
                    await browser_manager.human_delay()
                except Exception:
                    logger.warning("短标题字段不存在，跳过")

            # 上传图片
            if image_paths:
                file_input = page.locator('input[type="file"]').first
                if file_input:
                    # 闲鱼可能使用特殊上传组件，尝试 set_input_files
                    await file_input.set_input_files(image_paths[:9])  # 最多9张
                    await browser_manager.human_delay(3, 5)

            # 上传视频（如果有）
            if video_path:
                try:
                    video_input = page.locator('input[type="file"]').last
                    if video_input:
                        await video_input.set_input_files([video_path])
                        await browser_manager.human_delay(3, 5)
                except Exception:
                    logger.warning("视频上传失败，跳过")

            # 填入描述
            await page.fill('textarea[placeholder*="描述"], div[contenteditable="true"]', description)
            await browser_manager.human_delay()

            # 选择分类（如果有）
            if category:
                try:
                    await page.click('text=分类')
                    await browser_manager.human_delay()
                    await page.click(f'text={category}')
                    await browser_manager.human_delay()
                except Exception:
                    logger.warning("分类选择失败，跳过")

            # 设置价格
            await page.fill('input[placeholder*="价格"], input[placeholder*="¥"]', str(price))
            await browser_manager.human_delay()

            # 点击发布按钮
            await page.click('button:has-text("发布"), button:has-text("确认发布")')
            await browser_manager.human_delay(3, 5)

            # 验证发布结果
            success = await self._check_publish_success(page)
            if success:
                logger.info(f"商品发布成功: {title}")
            else:
                await browser_manager.take_screenshot(shop_id, page, "publish_failed")
                logger.error(f"商品发布失败: {title}")

            return success

        except Exception as e:
            await browser_manager.take_screenshot(shop_id, page, "publish_error")
            logger.error(f"发布商品异常: {e}")
            return False
        finally:
            await page.close()

    async def _check_publish_success(self, page: Page) -> bool:
        """检查发布是否成功"""
        try:
            await page.wait_for_url("**/my/sell**", timeout=15000)
            return True
        except Exception:
            pass
        try:
            success_text = await page.locator('text=发布成功').count()
            if success_text > 0:
                return True
        except Exception:
            pass
        return False

    async def delist_product(self, shop_id: str, item_id: str) -> bool:
        """下架指定商品"""
        ctx = await browser_manager.get_context(shop_id, headless=True)
        page = await ctx.new_page()
        try:
            await page.goto(f"{self.MY_ITEMS_URL}", wait_until="networkidle", timeout=60000)
            await browser_manager.human_delay(2, 4)

            # 查找并下架商品
            await page.fill('input[placeholder*="搜索"]', item_id)
            await browser_manager.human_delay()
            await page.keyboard.press("Enter")
            await browser_manager.human_delay(2, 3)

            # 点击下架按钮
            try:
                await page.click('button:has-text("下架"), span:has-text("下架")')
                await browser_manager.human_delay()
                await page.click('button:has-text("确认"), span:has-text("确认")')
                await browser_manager.human_delay(2, 3)
                logger.info(f"商品 {item_id} 下架成功")
                return True
            except Exception:
                logger.warning(f"商品 {item_id} 下架失败")
                return False

        except Exception as e:
            await browser_manager.take_screenshot(shop_id, page, "delist_error")
            logger.error(f"下架商品异常: {e}")
            return False
        finally:
            await page.close()

    async def batch_delist(self, shop_id: str, item_ids: list[str]) -> list[dict]:
        """批量下架商品"""
        results = []
        for item_id in item_ids:
            success = await self.delist_product(shop_id, item_id)
            results.append({"item_id": item_id, "success": success})
            await browser_manager.human_delay(1, 2)
        return results


# 全局实例
xianyu_page = XianyuPage()