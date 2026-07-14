"""全局设置服务"""
import json
from typing import Optional
from app.database import async_session
from app.models.settings import GlobalSettings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    """设置管理器"""

    async def get_settings(self) -> GlobalSettings:
        """获取全局设置（单例模式）"""
        async with async_session() as session:
            settings = await session.get(GlobalSettings, 1)
            if not settings:
                settings = GlobalSettings(id=1)
                session.add(settings)
                await session.commit()
                await session.refresh(settings)
            return settings

    async def update_settings(self, data: dict) -> GlobalSettings:
        """更新全局设置"""
        async with async_session() as session:
            settings = await session.get(GlobalSettings, 1)
            if not settings:
                settings = GlobalSettings(id=1)
                session.add(settings)

            updatable_fields = [
                "enable_ai_main_video", "enable_smart_crop_3_4", "enable_ai_short_title",
                "price_markup_ratio", "price_markup_amount",
                "supplier_blacklist", "keyword_blocklist",
                "post_listing_delay", "simulated_pause_interval", "simulated_pause_count",
                "target_success_count",
            ]
            for field in updatable_fields:
                if field in data:
                    setattr(settings, field, data[field])

            await session.commit()
            await session.refresh(settings)
            logger.info("全局设置已更新")
            return settings

    async def reset_settings(self) -> GlobalSettings:
        """恢复默认设置"""
        defaults = GlobalSettings.defaults()
        return await self.update_settings(defaults)

    async def get_blacklist_suppliers(self) -> list[str]:
        """获取供应商黑名单列表"""
        settings = await self.get_settings()
        try:
            return json.loads(settings.supplier_blacklist) if settings.supplier_blacklist else []
        except json.JSONDecodeError:
            return []

    async def add_blacklist_supplier(self, supplier: str) -> list[str]:
        """添加供应商到黑名单"""
        suppliers = await self.get_blacklist_suppliers()
        if supplier not in suppliers:
            suppliers.append(supplier)
            await self.update_settings({"supplier_blacklist": json.dumps(suppliers, ensure_ascii=False)})
        return suppliers

    async def remove_blacklist_supplier(self, supplier: str) -> list[str]:
        """从黑名单移除供应商"""
        suppliers = await self.get_blacklist_suppliers()
        if supplier in suppliers:
            suppliers.remove(supplier)
            await self.update_settings({"supplier_blacklist": json.dumps(suppliers, ensure_ascii=False)})
        return suppliers

    async def get_blocklist_keywords(self) -> list[str]:
        """获取关键词屏蔽列表"""
        settings = await self.get_settings()
        try:
            return json.loads(settings.keyword_blocklist) if settings.keyword_blocklist else []
        except json.JSONDecodeError:
            return []

    async def add_blocklist_keyword(self, keyword: str) -> list[str]:
        """添加屏蔽关键词"""
        keywords = await self.get_blocklist_keywords()
        if keyword not in keywords:
            keywords.append(keyword)
            await self.update_settings({"keyword_blocklist": json.dumps(keywords, ensure_ascii=False)})
        return keywords

    async def remove_blocklist_keyword(self, keyword: str) -> list[str]:
        """移除屏蔽关键词"""
        keywords = await self.get_blocklist_keywords()
        if keyword in keywords:
            keywords.remove(keyword)
            await self.update_settings({"keyword_blocklist": json.dumps(keywords, ensure_ascii=False)})
        return keywords


# 全局实例
settings_manager = SettingsManager()