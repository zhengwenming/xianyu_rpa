"""运行日志 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.log import RunLog
from app.utils.logger import ws_manager
from app.utils.helpers import generate_uuid

router = APIRouter(prefix="/api/logs", tags=["运行日志"])


@router.get("")
async def query_logs(
    task_id: Optional[str] = None, level: Optional[str] = None,
    page: int = 1, page_size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(RunLog).order_by(desc(RunLog.timestamp))
    if task_id:
        query = query.where(RunLog.task_id == task_id)
    if level:
        query = query.where(RunLog.level == level)
    total_result = await db.execute(select(RunLog).where(*query.whereclause) if query.whereclause else select(RunLog))
    total = len(list(total_result.scalars().all()))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    logs = result.scalars().all()
    return {"code": 0, "data": {"items": [log.to_dict() for log in logs], "total": total, "page": page, "page_size": page_size}, "message": "ok"}


@router.get("/export")
async def export_logs(task_id: Optional[str] = None, level: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(RunLog).order_by(RunLog.timestamp)
    if task_id:
        query = query.where(RunLog.task_id == task_id)
    if level:
        query = query.where(RunLog.level == level)
    result = await db.execute(query)
    logs = result.scalars().all()
    lines = [f"[{log.timestamp}] [{log.level.upper()}] {log.message}" for log in logs]
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("\n".join(lines), media_type="text/plain", headers={"Content-Disposition": "attachment; filename=logs.txt"})