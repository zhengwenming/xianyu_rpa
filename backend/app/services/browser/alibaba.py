"""1688 采集封装"""
import os
import re
from datetime import datetime
from typing import Optional
from playwright.async_api import Page
from app.config import settings as app_settings
from app.services.browser.manager import browser_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AlibabaCollector:
    """1688 商品采集器"""

    SEARCH_URL = "https://www.1688.com/chanpin/"

    # 采集专用上下文 id（复用 browser_manager 的反检测配置，匿名可搜，不依赖店铺登录）
    COLLECTOR_CTX = "_collector"

    # 搜索结果商品容器的候选选择器（1688 前端结构会变，逐个尝试）
    SEARCH_ITEM_SELECTORS = [
        ".offer-list-row .offer-card",
        ".offer-list-row-offer",
        "[data-content='offerList'] .grid-offer",
        ".grid-offer-item",
        ".sm-offer-item",
        ".J_offerCard",
        "a[href*='offer/'][href*='.html']",
    ]

    async def _save_debug(self, page: Page, tag: str) -> str:
        """采集异常时保存截图与 HTML 片段，返回诊断信息文本"""
        debug_dir = os.path.join(app_settings.SESSION_DIR, self.COLLECTOR_CTX, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shot_path = os.path.join(debug_dir, f"{tag}_{ts}.png")
        info_parts = [f"当前页面URL: {page.url}"]
        try:
            await page.screenshot(path=shot_path, full_page=True)
            info_parts.append(f"已保存截图: {shot_path}")
        except Exception as e:
            info_parts.append(f"截图失败: {e}")
        try:
            title = await page.title()
            info_parts.append(f"页面标题: {title}")
        except Exception:
            pass
        # 判断是否被风控/登录拦截
        url_low = page.url.lower()
        if any(k in url_low for k in ("login", "passport", "captcha", "punish", "sufei")):
            info_parts.append("疑似被 1688 风控拦截（跳转到登录/验证页），请降低采集频率或稍后重试")
        return "；".join(info_parts)

    @staticmethod
    def _is_login_page(url: str) -> bool:
        """判断当前 URL 是否是 1688/淘宝的登录页"""
        url_low = (url or "").lower()
        return any(k in url_low for k in ("login.taobao.com", "login.1688.com", "passport", "/member/signin"))

    async def _cookies_logged_in(self) -> bool:
        """通过 cookie 判断 1688 采集账号是否已登录。

        只认 unb（阿里体系登录后的用户数字编号，未登录绝不会下发）；
        cookie2 在未登录态也可能被下发，不能作为登录依据，故不采用。
        另外校验 unb 属于阿里相关域且有非空值，避免残留空 cookie 误判。
        """
        try:
            cookies = await browser_manager.get_cookies(self.COLLECTOR_CTX)
        except Exception:
            return False
        return self._cookies_has_unb(cookies)

    @staticmethod
    def _cookies_has_unb(cookies) -> bool:
        """在给定 cookie 列表里判断是否存在有效的登录票据 unb。"""
        for c in (cookies or []):
            if c.get("name") != "unb":
                continue
            value = (c.get("value") or "").strip()
            domain = (c.get("domain") or "").lower()
            if value and ("1688.com" in domain or "taobao.com" in domain or "alibaba" in domain):
                return True
        return False

    async def check_login(self) -> bool:
        """检测 1688 采集账号是否已登录。

        以“实际访问搜索页是否被跳转到登录页”为最终依据（最可靠）。
        cookie 仅作为快速否定：无 unb 一定未登录，可省去开浏览器；
        有 unb 也不直接判定成功，仍需搜索页验证，避免 cookie 残留导致的假登录绿标。
        """
        has_cookie = await self._cookies_logged_in()
        ctx = await browser_manager.get_context(self.COLLECTOR_CTX, headless=True)
        page = await ctx.new_page()
        try:
            # 1688 未登录时会对搜索页做 JS 跳转，导致 goto 抛 ERR_ABORTED；
            # 这不代表"网络故障"而是"被拦截了"，所以异常后也要等跳转稳定再检查最终 URL。
            import asyncio as _asyncio
            try:
                await page.goto(
                    "https://s.1688.com/selloffer/offer_search.htm?keywords=%E6%89%8B%E6%9C%BA",
                    wait_until="domcontentloaded", timeout=30000,
                )
            except Exception as e:
                logger.debug(f"check_login goto 抛异常（可能是登录跳转）: {e}")
            # 1688 未登录会经过多级跳转（s.1688.com → login.1688.com → login.taobao.com），需等足够时间
            await _asyncio.sleep(3)
            if self._is_login_page(page.url):
                return False
            # 未被跳转即视为可正常采集（无论是否已实名登录，能出结果即可）
            return True
        except Exception as e:
            logger.error(f"检测 1688 登录态失败: {e}")
            # 网络异常时，退回 cookie 判断，避免误报未登录打断用户
            return has_cookie
        finally:
            await page.close()

    async def login(self, timeout_sec: int = 180) -> bool:
        """打开有头浏览器让用户扫码登录 1688，登录态持久化到 _collector 上下文。

        关键点：
        - 落地页用 www.1688.com 首页（比独立 signin 页稳定），页面右上角点“请登录”即可扫码；
        - goto 即使超时/报错也绝不关闭窗口，让用户有足够时间手动登录；
        - 登录成功以 cookie（unb/cookie2）出现为准，而非“是否离开登录页”。
        """
        import asyncio as _asyncio
        # 有头模式复用持久上下文，先关掉已缓存的无头实例
        await browser_manager.close_context(self.COLLECTOR_CTX)
        ctx = await browser_manager.get_context(self.COLLECTOR_CTX, headless=False)
        page = await ctx.new_page()
        # 打开落地页：优先首页，失败再退回登录页；任何一步超时都不放弃窗口
        opened = False
        for target in ("https://www.1688.com/", "https://login.1688.com/member/signin.htm"):
            try:
                await page.goto(target, wait_until="commit", timeout=30000)
                opened = True
                logger.info(f"已打开 1688 页面：{target}，请在弹出的浏览器窗口中扫码/账号登录…")
                break
            except Exception as e:
                logger.warning(f"打开 {target} 超时/失败（可继续手动操作）：{e}")
        if not opened:
            logger.warning("1688 页面初始加载均超时，窗口仍保持打开，请手动在地址栏访问 1688 并登录")
        try:
            # 轮询等待登录成功：直接读取“当前登录窗口所在上下文”的 cookie。
            # 关键：绝不在此上下文里 new_page()/close()（那会打断/刷新用户正在扫码的页面），
            # 因此不走 browser_manager.get_cookies（它内部会开关标签页），只调 ctx.cookies()。
            waited = 0
            while waited < timeout_sec:
                await _asyncio.sleep(2)
                waited += 2
                # 页面被用户关闭时提前退出
                if page.is_closed():
                    logger.warning("登录窗口已被关闭，登录未完成")
                    break
                try:
                    cookies = await ctx.cookies()
                    if self._cookies_has_unb(cookies):
                        logger.info("1688 登录成功（检测到登录 cookie unb）")
                        await browser_manager.human_delay(1, 2)
                        try:
                            if not page.is_closed():
                                await page.close()
                        except Exception:
                            pass
                        # 关闭有头上下文，后续采集用无头（登录 cookie 已持久化）
                        await browser_manager.close_context(self.COLLECTOR_CTX)
                        return True
                except Exception:
                    pass
            logger.warning("1688 登录超时（未在规定时间内完成扫码）")
            try:
                if not page.is_closed():
                    await page.close()
            except Exception:
                pass
            await browser_manager.close_context(self.COLLECTOR_CTX)
            return False
        except Exception as e:
            logger.error(f"1688 登录流程异常: {e}")
            try:
                if not page.is_closed():
                    await page.close()
            except Exception:
                pass
            await browser_manager.close_context(self.COLLECTOR_CTX)
            return False

    async def search_products(self, keyword: str, max_count: int = 20) -> list[dict]:
        """按关键词搜索 1688 商品"""
        products = []
        # 复用反检测上下文（STEALTH 参数 + init script + 真实 UA），避免被判定为无头自动化
        ctx = await browser_manager.get_context(self.COLLECTOR_CTX, headless=True)
        page = await ctx.new_page()
        try:
            search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={keyword}"
            # 用 commit 而非 domcontentloaded：未登录时 1688 会 JS 跳转到登录页，
            # 导致原始导航被中断抛 ERR_ABORTED--这不代表"网络错误"而是"被拦截了"。
            try:
                await page.goto(search_url, wait_until="commit", timeout=60000)
            except Exception as e:
                logger.debug(f"search_products goto 抛异常（可能是登录跳转）: {e}")
            await browser_manager.human_delay(2, 4)

            # 若被重定向到登录页，直接抛出清晰错误（1688 未登录会强制拦截搜索）
            if self._is_login_page(page.url):
                await self._save_debug(page, "search_need_login")
                raise RuntimeError(
                    "1688 采集账号未登录，已被跳转到登录页。请先在\"任务管理\"页点击\"登录1688采集账号\"扫码登录后再采集"
                )
            # 触发懒加载
            try:
                await page.mouse.wheel(0, 2000)
                await browser_manager.human_delay(1, 2)
            except Exception:
                pass

            # 逐个尝试候选选择器，任一命中即可
            matched_selector = None
            for sel in self.SEARCH_ITEM_SELECTORS:
                try:
                    await page.wait_for_selector(sel, timeout=6000, state="attached")
                    matched_selector = sel
                    break
                except Exception:
                    continue

            if not matched_selector:
                debug_info = await self._save_debug(page, "search_no_result")
                logger.error(f"1688 采集失败：未找到商品列表元素。{debug_info}")
                return products

            items = await page.query_selector_all(matched_selector)
            for item in items[:max_count]:
                try:
                    product = await self._extract_product(item)
                    if product and product.get("title"):
                        products.append(product)
                except Exception as e:
                    logger.warning(f"提取商品信息失败: {e}")

            logger.info(f"1688 搜索 '{keyword}' 采集到 {len(products)} 个商品（命中选择器: {matched_selector}）")
            return products

        except Exception as e:
            try:
                debug_info = await self._save_debug(page, "search_error")
            except Exception:
                debug_info = ""
            logger.error(f"1688 采集失败: {e}。{debug_info}")
            return products
        finally:
            await page.close()

    async def collect_from_url(self, url: str) -> Optional[dict]:
        """从 1688 商品 URL 采集"""
        ctx = await browser_manager.get_context(self.COLLECTOR_CTX, headless=True)
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await browser_manager.human_delay(2, 4)

            if self._is_login_page(page.url):
                await self._save_debug(page, "detail_need_login")
                raise RuntimeError(
                    "1688 采集账号未登录，已被跳转到登录页。请先在\"任务管理\"页点击\"登录1688采集账号\"扫码登录后再采集"
                )

            # 提取商品信息
            product = await self._extract_detail(page)
            if product:
                product["source_url"] = url
                logger.info(f"1688 URL 采集成功: {product.get('title', '')}")
            return product

        except Exception as e:
            try:
                debug_info = await self._save_debug(page, "detail_error")
            except Exception:
                debug_info = ""
            logger.error(f"1688 URL 采集失败: {e}。{debug_info}")
            return None
        finally:
            await page.close()

    async def _query_text(self, element, selectors: list[str]) -> str:
        """按候选选择器列表依次取文本，返回首个命中"""
        for sel in selectors:
            try:
                el = await element.query_selector(sel)
                if el:
                    text = (await el.inner_text()).strip()
                    if text:
                        return text
            except Exception:
                continue
        return ""

    async def _query_attr(self, element, selectors: list[str], attrs: list[str]) -> str:
        """按候选选择器 + 候选属性依次取值，返回首个命中"""
        for sel in selectors:
            try:
                el = await element.query_selector(sel)
                if not el:
                    continue
                for attr in attrs:
                    val = await el.get_attribute(attr)
                    if val:
                        return val
            except Exception:
                continue
        return ""

    async def _extract_product(self, element) -> Optional[dict]:
        """从搜索结果卡片提取商品信息"""
        try:
            title = await self._query_text(element, [
                ".offer-card-title a",
                ".offer-title",
                ".title",
                "a[title]",
                "img[alt]",
            ])
            if not title:
                # 兜底：取卡片链接的 title / alt
                title = await self._query_attr(element, ["a[title]", "img[alt]"], ["title", "alt"])
            title = title.strip()

            price_text = await self._query_text(element, [
                ".offer-card-price",
                ".price",
                ".price-value",
                "[class*='price']",
            ]) or "0"
            prices = re.findall(r"[\d.]+", price_text.replace(",", ""))
            price = float(prices[0]) if prices else 0.0

            url = await self._query_attr(element, [
                "a.offer-card-title",
                "a[href*='offer/']",
                "a[href*='.html']",
                "a",
            ], ["href"])

            img_url = await self._query_attr(element, ["img"], ["src", "data-src", "data-lazy-src"])

            return {
                "title": title,
                "price": price,
                "source_url": f"https:{url}" if url and url.startswith("//") else url,
                "image_url": f"https:{img_url}" if img_url and img_url.startswith("//") else img_url,
                "specs": "",
                "supplier": "",
                "ship_from": "",
            }
        except Exception:
            return None

    async def _extract_detail(self, page: Page) -> dict:
        """从商品详情页提取完整信息"""
        result = {}
        result["title"] = await self._query_text(page, [
            ".detail-title",
            ".title-text",
            ".od-pc-offer-title",
            "h1",
        ])

        price_text = await self._query_text(page, [
            ".price-value",
            ".price-now",
            ".od-pc-offer-price",
            "[class*='price']",
        ]) or "0"
        prices = re.findall(r"[\d.]+", price_text.replace(",", ""))
        result["price"] = float(prices[0]) if prices else 0.0

        # 采集图片
        images = []
        try:
            img_elements = await page.query_selector_all(
                ".detail-gallery img, .od-pc-offer-gallery img, [class*='gallery'] img"
            )
            for img in img_elements[:9]:
                src = await img.get_attribute("src") or await img.get_attribute("data-src")
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    if src not in images:
                        images.append(src)
        except Exception:
            pass
        result["images"] = images

        # 采集规格
        result["specs"] = await self._query_text(page, [
            ".detail-params",
            ".obj-content",
            "[class*='attribute']",
        ])

        # 采集供应商
        result["supplier"] = await self._query_text(page, [
            ".company-name",
            ".supplier-name",
            "[class*='company']",
        ])

        # 采集发货地
        result["ship_from"] = await self._query_text(page, [
            ".delivery-from",
            ".delivery-address",
            "[class*='delivery']",
        ])

        return result


# 全局实例
alibaba_collector = AlibabaCollector()