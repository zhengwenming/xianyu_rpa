"""下架日志 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.delisting_log import DelistingLog

router = APIRouter(prefix="/api/delisting-logs", tags=["下架日志"])


@router.get("")
async def list_delisting_logs(
    shop_id: Optional[str] = None, reason: Optional[str] = None,
    page: int = 1, page_size: int = 20,
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(DelistingLog).order_by(desc(DelistingLog.created_at))
    if shop_id:
        query = query.where(DelistingLog.shop_id == shop_id)
    if reason:
        query = query.where(DelistingLog.delist_reason == reason)
    if start_date:
        query = query.where(DelistingLog.created_at >= start_date)
    if end_date:
        query = query.where(DelistingLog.created_at <= end_date)
    total = await db.execute(select(func.count(DelistingLog.id)).where(*query.whereclause) if query.whereclause else select(func.count(DelistingLog.id)))
    total = total.scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()
    return {"code": 0, "data": {"items": [log.to_dict() for log in logs], "total": total, "page": page, "page_size": page_size}, "message": "ok"}


@router.get("/summary")
async def delisting_log_summary(shop_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(DelistingLog)
    if shop_id:
        query = query.where(DelistingLog.shop_id == shop_id)
    result = await db.execute(query)
    logs = result.scalars().all()
    total = len(logs)
    auto = len([l for l in logs if l.delist_type == "auto"])
    manual = len([l for l in logs if l.delist_type == "manual"])
    sold_out = len([l for l in logs if l.delist_reason == "sold_out"])
    return {"code": 0, "data": {"total": total, "auto": auto, "manual": manual, "sold_out": sold_out}, "message": "ok"}


@router.get("/{log_id}")
async def get_delisting_log(log_id: str, db: AsyncSession = Depends(get_db)):
    log = await db.get(DelistingLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return {"code": 0, "data": log.to_dict(), "message": "ok"}


@router.delete("")
async def clear_delisting_logs(shop_id: Optional[str] = None, confirm: bool = False, db: AsyncSession = Depends(get_db)):
    if not confirm:
        return {"code": 1, "data": None, "message": "请确认清空操作（confirm=true）"}
    query = select(DelistingLog)
    if shop_id:
        query = query.where(DelistingLog.shop_id == shop_id)
    result = await db.execute(query)
    for log in result.scalars().all():
        await db.delete(log)
    await db.commit()
    return {"code": 0, "data": None, "message": "下架日志已清空"}