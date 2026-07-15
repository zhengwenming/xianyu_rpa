"""任务管理 API 路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.task import Task
from app.services.task.manager import task_manager
from app.services.browser.alibaba import alibaba_collector

router = APIRouter(prefix="/api/tasks", tags=["任务管理"])


class TaskCreate(BaseModel):
    name: str
    shop_id: str
    shop_name: str = ""
    keywords: str = "[]"
    source_urls: str = "[]"
    target_count: int = 10
    llm_config_id: Optional[str] = None
    image_plan: str = "original"
    category: str = ""


@router.get("")
async def list_tasks(
    page: int = 1, page_size: int = 20,
    status: Optional[str] = None, shop_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).order_by(desc(Task.created_at))
    if status:
        query = query.where(Task.status == status)
    if shop_id:
        query = query.where(Task.shop_id == shop_id)
    total_result = await db.execute(select(Task).where(*query.whereclause) if query.whereclause else select(Task))
    total = len(list(total_result.scalars().all()))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return {"code": 0, "data": {"items": [t.to_dict() for t in tasks], "total": total, "page": page, "page_size": page_size}, "message": "ok"}


@router.post("")
async def create_task(data: TaskCreate):
    task = await task_manager.create_task(data.dict())
    return {"code": 0, "data": task.to_dict(), "message": "任务创建成功"}


@router.get("/collector/login-status")
async def collector_login_status():
    """查询 1688 采集账号登录态"""
    is_login = await alibaba_collector.check_login()
    return {"code": 0, "data": {"is_login": is_login}, "message": "ok"}


@router.post("/collector/login")
async def collector_login():
    """打开有头浏览器扫码登录 1688 采集账号（阻塞直到登录成功或超时）"""
    ok = await alibaba_collector.login(timeout_sec=240)
    if ok:
        return {"code": 0, "data": {"is_login": True}, "message": "1688 采集账号登录成功"}
    return {"code": 1, "data": {"is_login": False}, "message": "登录超时或失败，请重试（窗口保持打开期间可继续扫码）"}


@router.get("/{task_id}")
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "data": task.to_dict(), "message": "ok"}


@router.post("/{task_id}/start")
async def start_task(task_id: str):
    success = await task_manager.start_task(task_id)
    return {"code": 0 if success else 1, "data": None, "message": "任务已启动" if success else "启动失败"}


@router.post("/{task_id}/restart")
async def restart_task(task_id: str):
    success = await task_manager.restart_task(task_id)
    return {"code": 0 if success else 1, "data": None, "message": "任务已重新启动" if success else "重启失败"}


@router.post("/{task_id}/pause")
async def pause_task(task_id: str):
    success = await task_manager.pause_task(task_id)
    return {"code": 0 if success else 1, "data": None, "message": "任务已暂停" if success else "暂停失败"}


@router.post("/{task_id}/resume")
async def resume_task(task_id: str):
    success = await task_manager.resume_task(task_id)
    return {"code": 0 if success else 1, "data": None, "message": "任务已恢复" if success else "恢复失败"}


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    success = await task_manager.cancel_task(task_id)
    return {"code": 0 if success else 1, "data": None, "message": "任务已取消" if success else "取消失败"}


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    success = await task_manager.delete_task(task_id)
    return {"code": 0 if success else 1, "data": None, "message": "任务已删除" if success else "删除失败"}


@router.get("/{task_id}/progress")
async def get_task_progress(task_id: str):
    progress = await task_manager.get_task_progress(task_id)
    if not progress:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"code": 0, "data": progress, "message": "ok"}