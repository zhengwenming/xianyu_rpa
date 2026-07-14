"""1688 商品采集服务"""
from typing import Optional
from app.services.browser.alibaba import alibaba_collector
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProductCollector:
    """商品采集器"""

    async def collect_by_keyword(self, keyword: str, max_count: int = 20) -> list[dict]:
        """按关键词采集商品"""
        logger.info(f"开始采集关键词: {keyword}")
        products = await alibaba_collector.search_products(keyword, max_count)
        logger.info(f"关键词 '{keyword}' 采集完成，共 {len(products)} 个商品")
        return products

    async def collect_by_url(self, url: str) -> Optional[dict]:
        """按 URL 采集商品"""
        logger.info(f"开始采集URL: {url}")
        product = await alibaba_collector.collect_from_url(url)
        if product:
            logger.info(f"URL 采集完成: {product.get('title', '')}")
        else:
            logger.warning(f"URL 采集失败: {url}")
        return product


# 全局实例
product_collector = ProductCollector()