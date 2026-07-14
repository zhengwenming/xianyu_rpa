"""会话/Cookie 管理"""
import json
from typing import Optional
from app.services.browser.manager import browser_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """会话管理器 - 管理 Cookie 和 storage_state"""

    async def save_session(self, shop_id: str) -> bool:
        """保存当前店铺的会话状态"""
        try:
            ctx = await browser_manager.get_context(shop_id, headless=True)
            # Playwright 的 persistent context 自动保存 storage_state 到 user_data_dir
            logger.info(f"店铺 {shop_id} 会话已保存")
            return True
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
            return False

    async def load_session(self, shop_id: str) -> bool:
        """加载会话（Playwright 会自动从 user_data_dir 加载）"""
        try:
            await browser_manager.get_context(shop_id, headless=True)
            return True
        except Exception as e:
            logger.error(f"加载会话失败: {e}")
            return False

    async def clear_session(self, shop_id: str) -> bool:
        """清除会话"""
        try:
            await browser_manager.close_context(shop_id)
            import shutil
            import os
            from app.config import settings
            session_dir = f"{settings.SESSION_DIR}/{shop_id}"
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)
            logger.info(f"店铺 {shop_id} 会话已清除")
            return True
        except Exception as e:
            logger.error(f"清除会话失败: {e}")
            return False

    async def get_cookie_string(self, shop_id: str) -> str:
        """获取 Cookie 字符串"""
        cookies = await browser_manager.get_cookies(shop_id)
        return "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    async def refresh_cookies(self, shop_id: str) -> bool:
        """刷新 Cookie（通过重新加载页面）"""
        try:
            ctx = await browser_manager.get_context(shop_id, headless=True)
            page = await ctx.new_page()
            await page.goto("https://www.goofish.com/", wait_until="networkidle", timeout=30000)
            await page.close()
            logger.info(f"店铺 {shop_id} Cookie 已刷新")
            return True
        except Exception as e:
            logger.error(f"刷新 Cookie 失败: {e}")
            return False


# 全局实例
session_manager = SessionManager()