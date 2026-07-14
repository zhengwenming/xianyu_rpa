"""任务策略日志 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.task_log import TaskStrategyLog
from app.models.listing_log import ListingLog

router = APIRouter(prefix="/api/task-logs", tags=["任务策略日志"])


@router.get("")
async def list_task_logs(
    shop_id: Optional[str] = None, status: Optional[str] = None,
    page: int = 1, page_size: int = 20,
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(TaskStrategyLog).order_by(desc(TaskStrategyLog.created_at))
    if shop_id:
        query = query.where(TaskStrategyLog.shop_id == shop_id)
    if status:
        query = query.where(TaskStrategyLog.status == status)
    if start_date:
        query = query.where(TaskStrategyLog.created_at >= start_date)
    if end_date:
        query = query.where(TaskStrategyLog.created_at <= end_date)
    total = await db.execute(select(func.count(TaskStrategyLog.id)).where(*query.whereclause) if query.whereclause else select(func.count(TaskStrategyLog.id)))
    total = total.scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()
    return {"code": 0, "data": {"items": [log.to_dict() for log in logs], "total": total, "page": page, "page_size": page_size}, "message": "ok"}


@router.get("/summary")
async def task_log_summary(shop_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(TaskStrategyLog)
    if shop_id:
        query = query.where(TaskStrategyLog.shop_id == shop_id)
    result = await db.execute(query)
    logs = result.scalars().all()
    total = len(logs)
    running = len([l for l in logs if l.status == "running"])
    completed = len([l for l in logs if l.status == "completed"])
    interrupted = len([l for l in logs if l.status in ("interrupted", "cancelled", "failed")])
    return {"code": 0, "data": {"total": total, "running": running, "completed": completed, "interrupted": interrupted}, "message": "ok"}


@router.get("/{log_id}")
async def get_task_log(log_id: str, db: AsyncSession = Depends(get_db)):
    log = await db.get(TaskStrategyLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return {"code": 0, "data": log.to_dict(), "message": "ok"}


@router.get("/{log_id}/listings")
async def get_task_listings(log_id: str, db: AsyncSession = Depends(get_db)):
    log = await db.get(TaskStrategyLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    result = await db.execute(select(ListingLog).where(ListingLog.task_id == log.task_id).order_by(ListingLog.created_at))
    listings = result.scalars().all()
    return {"code": 0, "data": [l.to_dict() for l in listings], "message": "ok"}


@router.delete("")
async def clear_task_logs(confirm: bool = False, db: AsyncSession = Depends(get_db)):
    if not confirm:
        return {"code": 1, "data": None, "message": "请确认清空操作（confirm=true）"}
    result = await db.execute(select(TaskStrategyLog))
    for log in result.scalars().all():
        await db.delete(log)
    await db.commit()
    return {"code": 0, "data": None, "message": "任务策略日志已清空"}