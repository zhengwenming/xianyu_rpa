"""全局设置 API 路由"""
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.settings.manager import settings_manager

router = APIRouter(prefix="/api/settings", tags=["全局设置"])


class SettingsUpdate(BaseModel):
    enable_ai_main_video: Optional[bool] = None
    enable_smart_crop_3_4: Optional[bool] = None
    enable_ai_short_title: Optional[bool] = None
    price_markup_ratio: Optional[float] = None
    price_markup_amount: Optional[float] = None
    supplier_blacklist: Optional[str] = None
    keyword_blocklist: Optional[str] = None
    post_listing_delay: Optional[int] = None
    simulated_pause_interval: Optional[int] = None
    simulated_pause_count: Optional[int] = None
    target_success_count: Optional[int] = None


@router.get("")
async def get_settings():
    settings = await settings_manager.get_settings()
    return {"code": 0, "data": settings.to_dict(), "message": "ok"}


@router.put("")
async def update_settings(data: SettingsUpdate):
    settings = await settings_manager.update_settings(data.dict(exclude_unset=True))
    return {"code": 0, "data": settings.to_dict(), "message": "设置已保存"}


@router.post("/reset")
async def reset_settings():
    settings = await settings_manager.reset_settings()
    return {"code": 0, "data": settings.to_dict(), "message": "已恢复默认设置"}


@router.get("/blacklist/suppliers")
async def get_suppliers():
    suppliers = await settings_manager.get_blacklist_suppliers()
    return {"code": 0, "data": suppliers, "message": "ok"}


@router.post("/blacklist/suppliers")
async def add_supplier(supplier: str):
    suppliers = await settings_manager.add_blacklist_supplier(supplier)
    return {"code": 0, "data": suppliers, "message": "已添加"}


@router.delete("/blacklist/suppliers")
async def remove_supplier(supplier: str):
    suppliers = await settings_manager.remove_blacklist_supplier(supplier)
    return {"code": 0, "data": suppliers, "message": "已移除"}


@router.get("/blacklist/keywords")
async def get_keywords():
    keywords = await settings_manager.get_blocklist_keywords()
    return {"code": 0, "data": keywords, "message": "ok"}


@router.post("/blacklist/keywords")
async def add_keyword(keyword: str):
    keywords = await settings_manager.add_blocklist_keyword(keyword)
    return {"code": 0, "data": keywords, "message": "已添加"}


@router.delete("/blacklist/keywords")
async def remove_keyword(keyword: str):
    keywords = await settings_manager.remove_blocklist_keyword(keyword)
    return {"code": 0, "data": keywords, "message": "已移除"}