"""浏览器管理器 - Playwright 持久化上下文管理"""
import os
import random
import asyncio
from datetime import datetime
from typing import Optional
from pathlib import Path
from playwright.async_api import async_playwright, BrowserContext, Page
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BrowserManager:
    """浏览器实例管理器"""

    def __init__(self):
        self._playwright = None
        self._contexts: dict[str, BrowserContext] = {}
        self._lock = asyncio.Lock()

    async def _ensure_playwright(self):
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        return self._playwright

    async def get_context(self, shop_id: str, headless: bool = True) -> BrowserContext:
        """获取或创建指定店铺的浏览器上下文"""
        async with self._lock:
            if shop_id in self._contexts:
                ctx = self._contexts[shop_id]
                try:
                    # 检查上下文是否有效
                    page = await ctx.new_page()
                    await page.close()
                    return ctx
                except Exception:
                    # 上下文已失效，重新创建
                    del self._contexts[shop_id]

            pw = await self._ensure_playwright()
            user_data_dir = os.path.join(settings.SESSION_DIR, shop_id)
            os.makedirs(user_data_dir, exist_ok=True)

            ctx = await pw.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=headless,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
                bypass_csp=True,
                ignore_https_errors=True,
            )
            self._contexts[shop_id] = ctx
            logger.info(f"店铺 {shop_id} 浏览器上下文已创建")
            return ctx

    async def close_context(self, shop_id: str):
        """关闭指定店铺的浏览器上下文"""
        async with self._lock:
            if shop_id in self._contexts:
                try:
                    await self._contexts[shop_id].close()
                except Exception as e:
                    logger.warning(f"关闭店铺 {shop_id} 上下文异常: {e}")
                del self._contexts[shop_id]
                logger.info(f"店铺 {shop_id} 浏览器上下文已关闭")

    async def close_all(self):
        """关闭所有浏览器上下文"""
        async with self._lock:
            for shop_id in list(self._contexts.keys()):
                try:
                    await self._contexts[shop_id].close()
                except Exception:
                    pass
            self._contexts.clear()
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None

    async def check_login_status(self, shop_id: str) -> bool:
        """检测登录态是否有效"""
        try:
            ctx = await self.get_context(shop_id, headless=True)
            page = await ctx.new_page()
            try:
                await page.goto("https://www.goofish.com/", wait_until="networkidle", timeout=30000)
                current_url = page.url
                await page.close()
                # 如果被重定向到登录页，说明登录态已过期
                if "login" in current_url.lower() or "passport" in current_url.lower():
                    return False
                return True
            except Exception:
                await page.close()
                return False
        except Exception as e:
            logger.error(f"检查登录态失败: {e}")
            return False

    async def get_cookies(self, shop_id: str) -> list[dict]:
        """获取指定店铺的 Cookie"""
        try:
            ctx = await self.get_context(shop_id, headless=True)
            return await ctx.cookies()
        except Exception as e:
            logger.error(f"获取 Cookie 失败: {e}")
            return []

    async def take_screenshot(self, shop_id: str, page: Page, name: str = "screenshot") -> Optional[str]:
        """截图保存"""
        screenshot_dir = os.path.join(settings.SESSION_DIR, shop_id, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(screenshot_dir, filename)
        try:
            await page.screenshot(path=filepath, full_page=True)
            return filepath
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return None

    async def human_delay(self, min_sec: float = 1.0, max_sec: float = 3.0):
        """模拟人类操作的随机延迟"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)

    def is_context_active(self, shop_id: str) -> bool:
        return shop_id in self._contexts


# 全局浏览器管理器实例
browser_manager = BrowserManager()