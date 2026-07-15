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


# 反自动化检测的浏览器启动参数
STEALTH_ARGS = [
    "--disable-blink-features=AutomationControlled",  # 关键：去掉 navigator.webdriver 特征来源
    "--no-sandbox",
    "--disable-infobars",  # 去掉"正受自动控制"提示条
    "--disable-dev-shm-usage",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-web-security",
    "--no-first-run",
    "--no-default-browser-check",
    "--password-store=basic",
    "--use-mock-keychain",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
]

# 忽略 Playwright 默认注入的自动化开关
IGNORE_DEFAULT_ARGS = ["--enable-automation"]

# 每个页面加载前注入，抹掉自动化指纹（navigator.webdriver 等）
STEALTH_INIT_SCRIPT = """
// 抹掉 navigator.webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// 伪造 window.chrome（headless 下通常缺失）
if (!window.chrome) {
    window.chrome = { runtime: {} };
}

// 伪造 plugins / mimeTypes 长度（自动化环境常为空）
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5],
});
Object.defineProperty(navigator, 'mimeTypes', {
    get: () => [1, 2, 3, 4, 5],
});

// 语言
Object.defineProperty(navigator, 'languages', {
    get: () => ['zh-CN', 'zh', 'en'],
});

// 硬件并发 / 内存（避免异常小值被判定为无头）
Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });

// permissions.query 对 notifications 返回 default（headless 会异常）
const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
if (originalQuery) {
    window.navigator.permissions.query = (parameters) => (
        parameters && parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters)
    );
}

// WebGL vendor/renderer 伪装成真实显卡
try {
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function (parameter) {
        if (parameter === 37445) { return 'Intel Inc.'; }        // UNMASKED_VENDOR_WEBGL
        if (parameter === 37446) { return 'Intel Iris OpenGL Engine'; } // UNMASKED_RENDERER_WEBGL
        return getParameter.call(this, parameter);
    };
} catch (e) {}
"""

# 与真实 Chrome 对齐的 UA
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


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

            ctx = await self._launch_persistent(pw, user_data_dir, headless)
            # 注入反检测脚本（对该上下文内所有页面、所有导航生效）
            await ctx.add_init_script(STEALTH_INIT_SCRIPT)
            self._contexts[shop_id] = ctx
            logger.info(f"店铺 {shop_id} 浏览器上下文已创建")
            return ctx

    async def _launch_persistent(self, pw, user_data_dir: str, headless: bool):
        """启动持久化上下文，带 SingletonLock 清理与重试。

        持久化目录同一时刻只能被一个 Chromium 进程占用。前一个（例如 check_login 用的
        无头实例）关闭后，SingletonLock/SingletonSocket 释放有毫秒级延迟，紧接着以
        headless=False 重新启动同目录会报 ProcessSingleton 相关错误、导致窗口开不出来。
        这里做最多 3 次重试，失败时清理残留锁文件后再试。
        """
        last_err = None
        for attempt in range(3):
            try:
                return await pw.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=headless,
                    args=STEALTH_ARGS,
                    ignore_default_args=IGNORE_DEFAULT_ARGS,
                    viewport={"width": 1920, "height": 1080},
                    user_agent=DEFAULT_USER_AGENT,
                    locale="zh-CN",
                    timezone_id="Asia/Shanghai",
                    bypass_csp=True,
                    ignore_https_errors=True,
                )
            except Exception as e:
                last_err = e
                logger.warning(f"启动持久化上下文失败（第 {attempt + 1} 次）：{e}")
                # 清理可能残留的单例锁，给上一个进程退出留出时间
                for lock_name in ("SingletonLock", "SingletonSocket", "SingletonCookie"):
                    lock_path = os.path.join(user_data_dir, lock_name)
                    try:
                        if os.path.islink(lock_path) or os.path.exists(lock_path):
                            os.remove(lock_path)
                    except Exception:
                        pass
                await asyncio.sleep(1.0)
        raise last_err


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
                # 给底层 Chromium 进程退出、释放持久目录 SingletonLock 留出时间，
                # 否则紧接着以另一种 headless 模式重启同目录会因单例锁冲突而失败
                await asyncio.sleep(0.8)

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