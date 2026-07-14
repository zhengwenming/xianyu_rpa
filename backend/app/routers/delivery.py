"""自动发货 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.delivery import DeliveryConfig, DeliveryLog
from app.services.order.virtual_goods import virtual_goods_shipper

router = APIRouter(prefix="/api/delivery", tags=["自动发货"])


class DeliveryConfigCreate(BaseModel):
    shop_id: str
    product_id: str
    product_title: str = ""
    delivery_type: str
    card_pool: str = "[]"
    link_url: str = ""
    link_code: str = ""
    text_content: str = ""
    source_url: str = ""
    auto_ship: bool = True


class DeliveryConfigUpdate(BaseModel):
    product_title: Optional[str] = None
    delivery_type: Optional[str] = None
    card_pool: Optional[str] = None
    link_url: Optional[str] = None
    link_code: Optional[str] = None
    text_content: Optional[str] = None
    source_url: Optional[str] = None
    auto_ship: Optional[bool] = None


@router.get("/configs")
async def list_configs(shop_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(DeliveryConfig).order_by(DeliveryConfig.created_at.desc())
    if shop_id:
        query = query.where(DeliveryConfig.shop_id == shop_id)
    result = await db.execute(query)
    configs = result.scalars().all()
    return {"code": 0, "data": [c.to_dict() for c in configs], "message": "ok"}


@router.post("/configs")
async def create_config(data: DeliveryConfigCreate, db: AsyncSession = Depends(get_db)):
    config = DeliveryConfig(**data.dict())
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return {"code": 0, "data": config.to_dict(), "message": "创建成功"}


@router.put("/configs/{config_id}")
async def update_config(config_id: str, data: DeliveryConfigUpdate, db: AsyncSession = Depends(get_db)):
    config = await db.get(DeliveryConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(config, key, value)
    await db.commit()
    await db.refresh(config)
    return {"code": 0, "data": config.to_dict(), "message": "更新成功"}


@router.delete("/configs/{config_id}")
async def delete_config(config_id: str, db: AsyncSession = Depends(get_db)):
    config = await db.get(DeliveryConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    await db.delete(config)
    await db.commit()
    return {"code": 0, "data": None, "message": "已删除"}


@router.get("/configs/{product_id}")
async def get_product_config(product_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryConfig).where(DeliveryConfig.product_id == product_id))
    config = result.scalar_one_or_none()
    return {"code": 0, "data": config.to_dict() if config else None, "message": "ok"}


@router.get("/orders")
async def list_orders():
    return {"code": 0, "data": {"items": [], "total": 0}, "message": "ok"}


@router.get("/logs")
async def list_delivery_logs(page: int = 1, page_size: int = 20, db: AsyncSession = Depends(get_db)):
    query = select(DeliveryLog).order_by(desc(DeliveryLog.created_at))
    total = await db.execute(select(func.count(DeliveryLog.id)))
    total = total.scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()
    return {"code": 0, "data": {"items": [l.to_dict() for l in logs], "total": total, "page": page, "page_size": page_size}, "message": "ok"}


@router.get("/logs/summary")
async def delivery_log_summary(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DeliveryLog))
    logs = result.scalars().all()
    total = len(logs)
    success = len([l for l in logs if l.status == "success"])
    failed = len([l for l in logs if l.status == "failed"])
    return {"code": 0, "data": {"total": total, "success": success, "failed": failed}, "message": "ok"}


@router.get("/cards/{product_id}")
async def get_card_pool(product_id: str):
    cards = await virtual_goods_shipper.get_card_pool(product_id)
    return {"code": 0, "data": {"count": len(cards), "cards": cards}, "message": "ok"}


@router.post("/cards/{product_id}")
async def add_cards(product_id: str, cards: list[str]):
    success = await virtual_goods_shipper.add_cards(product_id, cards)
    return {"code": 0 if success else 1, "data": None, "message": "补充成功" if success else "补充失败"}