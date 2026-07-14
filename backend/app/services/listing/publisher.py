"""闲鱼上架发布服务"""
import os
from typing import Optional
from app.services.browser.xianyu import xianyu_page
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ListingPublisher:
    """上架发布器"""

    async def publish(
        self,
        shop_id: str,
        title: str,
        description: str,
        price: float,
        image_urls: list[str] = None,
        short_title: str = "",
        video_path: str = "",
    ) -> bool:
        """发布商品到闲鱼"""
        # 下载图片到本地
        local_images = []
        if image_urls:
            local_images = await self._download_images(image_urls)

        # 通过浏览器自动化发布
        success = await xianyu_page.publish_product(
            shop_id=shop_id,
            title=title,
            description=description,
            price=price,
            image_paths=local_images,
            short_title=short_title,
            video_path=video_path,
        )

        # 清理临时图片文件
        for img_path in local_images:
            try:
                if os.path.exists(img_path) and "_cache" in img_path:
                    os.remove(img_path)
            except Exception:
                pass

        return success

    async def _download_images(self, image_urls: list[str]) -> list[str]:
        """下载图片到本地"""
        import requests
        import uuid
        from app.config import settings

        local_paths = []
        cache_dir = os.path.join(settings.SESSION_DIR, "_cache")
        os.makedirs(cache_dir, exist_ok=True)

        for url in image_urls[:9]:
            try:
                resp = requests.get(url, timeout=30)
                ext = os.path.splitext(url.split("?")[0])[1] or ".jpg"
                filename = f"{uuid.uuid4().hex}{ext}"
                filepath = os.path.join(cache_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                local_paths.append(filepath)
            except Exception as e:
                logger.warning(f"下载图片失败: {url[:50]}... {e}")

        return local_paths


# 全局实例
listing_publisher = ListingPublisher()