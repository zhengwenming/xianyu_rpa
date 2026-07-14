"""店铺管理 API 路由"""
import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.shop import Shop
from app.services.browser.manager import browser_manager
from app.services.browser.session import session_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/shops", tags=["店铺管理"])


class ShopCreate(BaseModel):
    name: str


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None


@router.get("")
async def list_shops(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Shop).order_by(Shop.created_at.desc()))
    shops = result.scalars().all()
    return {"code": 0, "data": [s.to_dict() for s in shops], "message": "ok"}


@router.post("")
async def create_shop(data: ShopCreate, db: AsyncSession = Depends(get_db)):
    shop = Shop(name=data.name)
    db.add(shop)
    await db.commit()
    await db.refresh(shop)
    return {"code": 0, "data": shop.to_dict(), "message": "店铺创建成功"}


@router.put("/{shop_id}")
async def update_shop(shop_id: str, data: ShopUpdate, db: AsyncSession = Depends(get_db)):
    shop = await db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    if data.name is not None:
        shop.name = data.name
    if data.status is not None:
        shop.status = data.status
    await db.commit()
    await db.refresh(shop)
    return {"code": 0, "data": shop.to_dict(), "message": "更新成功"}


@router.delete("/{shop_id}")
async def delete_shop(shop_id: str, db: AsyncSession = Depends(get_db)):
    shop = await db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    await session_manager.clear_session(shop_id)
    await db.delete(shop)
    await db.commit()
    return {"code": 0, "data": None, "message": "店铺已删除"}


@router.post("/{shop_id}/authorize")
async def authorize_shop(shop_id: str, db: AsyncSession = Depends(get_db)):
    shop = await db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    ctx = await browser_manager.get_context(shop_id, headless=False)
    page = await ctx.new_page()
    await page.goto("https://www.goofish.com/", wait_until="networkidle")
    try:
        await page.wait_for_url("https://www.goofish.com/**", timeout=180000)
        if "login" not in page.url.lower():
            shop.login_status = "authorized"
            shop.authorized_at = datetime.now()
            shop.xianyu_user_id = shop_id
            shop.xianyu_nickname = shop.name
            await db.commit()
            await page.close()
            return {"code": 0, "data": shop.to_dict(), "message": "授权成功"}
    except Exception:
        pass
    await page.close()
    return {"code": 1, "data": None, "message": "登录超时或失败"}


@router.post("/{shop_id}/revoke")
async def revoke_shop(shop_id: str, db: AsyncSession = Depends(get_db)):
    shop = await db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    await session_manager.clear_session(shop_id)
    shop.login_status = "unauthorized"
    shop.authorized_at = None
    shop.xianyu_user_id = None
    shop.xianyu_nickname = None
    shop.xianyu_avatar = None
    await db.commit()
    return {"code": 0, "data": shop.to_dict(), "message": "已取消授权"}


@router.get("/{shop_id}/login-status")
async def check_login_status(shop_id: str, db: AsyncSession = Depends(get_db)):
    shop = await db.get(Shop, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    is_valid = await browser_manager.check_login_status(shop_id)
    if not is_valid and shop.login_status == "authorized":
        shop.login_status = "expired"
        await db.commit()
    return {"code": 0, "data": {"login_status": shop.login_status, "is_valid": is_valid}, "message": "ok"}


@router.delete("/{shop_id}/session")
async def clear_session(shop_id: str):
    success = await session_manager.clear_session(shop_id)
    return {"code": 0 if success else 1, "data": None, "message": "会话已清除" if success else "清除失败"}