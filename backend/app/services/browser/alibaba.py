"""1688 采集封装"""
from typing import Optional
from playwright.async_api import Page
from app.services.browser.manager import browser_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AlibabaCollector:
    """1688 商品采集器"""

    SEARCH_URL = "https://www.1688.com/chanpin/"

    async def search_products(self, keyword: str, max_count: int = 20) -> list[dict]:
        """按关键词搜索 1688 商品"""
        products = []
        pw = await browser_manager._ensure_playwright()
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        try:
            await page.goto(f"https://s.1688.com/selloffer/offer_search.htm?keywords={keyword}", wait_until="networkidle", timeout=60000)
            await browser_manager.human_delay(2, 4)

            # 等待商品列表加载
            await page.wait_for_selector(".offer-list-row", timeout=15000)

            # 提取商品信息
            items = await page.query_selector_all(".offer-list-row .offer-card")
            for item in items[:max_count]:
                try:
                    product = await self._extract_product(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.warning(f"提取商品信息失败: {e}")

            logger.info(f"1688 搜索 '{keyword}' 采集到 {len(products)} 个商品")
            return products

        except Exception as e:
            logger.error(f"1688 采集失败: {e}")
            return products
        finally:
            await page.close()
            await browser.close()

    async def collect_from_url(self, url: str) -> Optional[dict]:
        """从 1688 商品 URL 采集"""
        pw = await browser_manager._ensure_playwright()
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await browser_manager.human_delay(2, 4)

            # 提取商品信息
            product = await self._extract_detail(page)
            if product:
                product["source_url"] = url
                logger.info(f"1688 URL 采集成功: {product.get('title', '')}")
            return product

        except Exception as e:
            logger.error(f"1688 URL 采集失败: {e}")
            return None
        finally:
            await page.close()
            await browser.close()

    async def _extract_product(self, element) -> Optional[dict]:
        """从搜索结果卡片提取商品信息"""
        try:
            title_el = await element.query_selector(".offer-card-title a")
            title = await title_el.inner_text() if title_el else ""
            title = title.strip()

            price_el = await element.query_selector(".offer-card-price")
            price_text = await price_el.inner_text() if price_el else "0"
            import re
            prices = re.findall(r"[\d.]+", price_text.replace(",", ""))
            price = float(prices[0]) if prices else 0.0

            url_el = await element.query_selector("a.offer-card-title")
            url = await url_el.get_attribute("href") if url_el else ""

            img_el = await element.query_selector("img")
            img_url = await img_el.get_attribute("src") if img_el else ""

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
        try:
            title_el = await page.query_selector(".detail-title")
            result["title"] = (await title_el.inner_text()).strip() if title_el else ""
        except Exception:
            result["title"] = ""

        try:
            price_el = await page.query_selector(".price-value")
            price_text = await price_el.inner_text() if price_el else "0"
            import re
            prices = re.findall(r"[\d.]+", price_text.replace(",", ""))
            result["price"] = float(prices[0]) if prices else 0.0
        except Exception:
            result["price"] = 0.0

        # 采集图片
        images = []
        try:
            img_elements = await page.query_selector_all(".detail-gallery img")
            for img in img_elements[:9]:
                src = await img.get_attribute("src") or await img.get_attribute("data-src")
                if src:
                    if src.startswith("//"):
                        src = "https:" + src
                    images.append(src)
        except Exception:
            pass
        result["images"] = images

        # 采集规格
        try:
            specs_el = await page.query_selector(".detail-params")
            result["specs"] = (await specs_el.inner_text()).strip() if specs_el else ""
        except Exception:
            result["specs"] = ""

        # 采集供应商
        try:
            supplier_el = await page.query_selector(".company-name")
            result["supplier"] = (await supplier_el.inner_text()).strip() if supplier_el else ""
        except Exception:
            result["supplier"] = ""

        # 采集发货地
        try:
            ship_el = await page.query_selector(".delivery-from")
            result["ship_from"] = (await ship_el.inner_text()).strip() if ship_el else ""
        except Exception:
            result["ship_from"] = ""

        return result


# 全局实例
alibaba_collector = AlibabaCollector()