"""上架日志 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.listing_log import ListingLog

router = APIRouter(prefix="/api/listing-logs", tags=["上架日志"])


@router.get("")
async def list_listing_logs(
    shop_id: Optional[str] = None, status: Optional[str] = None,
    page: int = 1, page_size: int = 20,
    start_date: Optional[str] = None, end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(ListingLog).order_by(desc(ListingLog.created_at))
    if shop_id:
        query = query.where(ListingLog.shop_id == shop_id)
    if status:
        query = query.where(ListingLog.status == status)
    if start_date:
        query = query.where(ListingLog.created_at >= start_date)
    if end_date:
        query = query.where(ListingLog.created_at <= end_date)
    total = await db.execute(select(func.count(ListingLog.id)).where(*query.whereclause) if query.whereclause else select(func.count(ListingLog.id)))
    total = total.scalar() or 0
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()
    return {"code": 0, "data": {"items": [log.to_dict() for log in logs], "total": total, "page": page, "page_size": page_size}, "message": "ok"}


@router.get("/summary")
async def listing_log_summary(shop_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(ListingLog)
    if shop_id:
        query = query.where(ListingLog.shop_id == shop_id)
    result = await db.execute(query)
    logs = result.scalars().all()
    total = len(logs)
    success = len([l for l in logs if l.status == "success"])
    failed = total - success
    rate = round(success / total * 100, 1) if total > 0 else 0
    return {"code": 0, "data": {"total": total, "success": success, "failed": failed, "success_rate": rate}, "message": "ok"}


@router.get("/{log_id}")
async def get_listing_log(log_id: str, db: AsyncSession = Depends(get_db)):
    log = await db.get(ListingLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return {"code": 0, "data": log.to_dict(), "message": "ok"}


@router.delete("")
async def clear_listing_logs(shop_id: Optional[str] = None, confirm: bool = False, db: AsyncSession = Depends(get_db)):
    if not confirm:
        return {"code": 1, "data": None, "message": "请确认清空操作（confirm=true）"}
    query = select(ListingLog)
    if shop_id:
        query = query.where(ListingLog.shop_id == shop_id)
    result = await db.execute(query)
    for log in result.scalars().all():
        await db.delete(log)
    await db.commit()
    return {"code": 0, "data": None, "message": "上架日志已清空"}


@router.get("/export")
async def export_listing_logs(shop_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(ListingLog).order_by(desc(ListingLog.created_at))
    if shop_id:
        query = query.where(ListingLog.shop_id == shop_id)
    result = await db.execute(query)
    logs = result.scalars().all()
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    f = StringIO()
    writer = csv.writer(f)
    writer.writerow(["上架时间", "店铺", "商品标题", "来源供应商", "采集价", "上架价", "状态", "失败原因"])
    for log in logs:
        writer.writerow([log.created_at.isoformat() if log.created_at else "", log.shop_name or "", log.product_title or "", log.source_supplier or "", log.source_price or "", log.listing_price or "", log.status, log.fail_reason or ""])
    f.seek(0)
    return StreamingResponse(f, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=listing_logs.csv"})