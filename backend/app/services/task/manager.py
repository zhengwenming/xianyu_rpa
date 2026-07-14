"""任务管理器"""
import asyncio
import json
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from app.models.task import Task
from app.models.task_log import TaskStrategyLog
from app.models.listing_log import ListingLog
from app.models.settings import GlobalSettings
from app.services.task.state import TaskStatus, can_transition
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskManager:
    """任务管理器 - 管理所有任务的创建、控制、监控"""

    def __init__(self):
        self._runners: dict[str, TaskRunner] = {}
        self._pause_events: dict[str, asyncio.Event] = {}
        self._cancel_flags: dict[str, bool] = {}

    async def create_task(self, task_data: dict) -> Task:
        """创建新任务"""
        async with async_session() as session:
            task = Task(
                name=task_data.get("name", "未命名任务"),
                shop_id=task_data["shop_id"],
                shop_name=task_data.get("shop_name", ""),
                keywords=task_data.get("keywords", "[]"),
                source_urls=task_data.get("source_urls", "[]"),
                target_count=task_data.get("target_count", 10),
                llm_config_id=task_data.get("llm_config_id"),
                image_plan=task_data.get("image_plan", "original"),
                category=task_data.get("category", ""),
                status=TaskStatus.PENDING.value,
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)

            # 创建任务策略日志
            await self._create_strategy_log(session, task, task_data)

            logger.info(f"任务创建成功: {task.name} (ID: {task.id})")
            return task

    async def _create_strategy_log(self, session: AsyncSession, task: Task, task_data: dict):
        """创建任务策略日志"""
        # 获取全局设置快照
        settings = await session.get(GlobalSettings, 1)
        strategy_config = {
            "price_markup_ratio": settings.price_markup_ratio if settings else 1.3,
            "price_markup_amount": settings.price_markup_amount if settings else 0.0,
            "image_plan": task_data.get("image_plan", "original"),
            "enable_ai_main_video": settings.enable_ai_main_video if settings else False,
            "enable_smart_crop_3_4": settings.enable_smart_crop_3_4 if settings else True,
            "enable_ai_short_title": settings.enable_ai_short_title if settings else False,
            "post_listing_delay": settings.post_listing_delay if settings else 30,
            "simulated_pause_interval": settings.simulated_pause_interval if settings else 15,
            "simulated_pause_count": settings.simulated_pause_count if settings else 10,
        }
        strategy_log = TaskStrategyLog(
            task_id=task.id,
            task_name=task.name,
            shop_id=task.shop_id,
            shop_name=task.shop_name,
            product_category=task.category,
            keywords=task.keywords,
            strategy_config=json.dumps(strategy_config, ensure_ascii=False),
            target_count=task.target_count,
            status=TaskStatus.PENDING.value,
        )
        session.add(strategy_log)

    async def start_task(self, task_id: str) -> bool:
        """启动任务"""
        async with async_session() as session:
            task = await session.get(Task, task_id)
            if not task:
                logger.error(f"任务不存在: {task_id}")
                return False
            if not can_transition(task.status, TaskStatus.RUNNING.value):
                logger.error(f"任务 {task_id} 不能从 {task.status} 转换为 running")
                return False

            task.status = TaskStatus.RUNNING.value
            task.start_time = datetime.now()
            await session.commit()

        # 创建暂停事件和取消标志
        self._pause_events[task_id] = asyncio.Event()
        self._pause_events[task_id].set()  # 默认不暂停
        self._cancel_flags[task_id] = False

        # 启动任务执行器（延迟导入避免循环引用）
        from app.services.task.runner import TaskRunner
        runner = TaskRunner(task_id)
        self._runners[task_id] = runner
        asyncio.create_task(runner.run())

        logger.info(f"任务已启动: {task_id}")
        return True

    async def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        if task_id not in self._pause_events:
            logger.error(f"任务 {task_id} 未运行或不存在")
            return False
        self._pause_events[task_id].clear()  # 暂停
        async with async_session() as session:
            task = await session.get(Task, task_id)
            if task and can_transition(task.status, TaskStatus.PAUSED.value):
                task.status = TaskStatus.PAUSED.value
                await session.commit()
        logger.info(f"任务已暂停: {task_id}")
        return True

    async def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        if task_id not in self._pause_events:
            logger.error(f"任务 {task_id} 未运行或不存在")
            return False
        self._pause_events[task_id].set()  # 恢复
        async with async_session() as session:
            task = await session.get(Task, task_id)
            if task and can_transition(task.status, TaskStatus.RUNNING.value):
                task.status = TaskStatus.RUNNING.value
                await session.commit()
        logger.info(f"任务已恢复: {task_id}")
        return True

    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        self._cancel_flags[task_id] = True
        self._pause_events[task_id] = asyncio.Event()
        self._pause_events[task_id].set()  # 确保取消检测能通过
        async with async_session() as session:
            task = await session.get(Task, task_id)
            if task and can_transition(task.status, TaskStatus.CANCELLED.value):
                task.status = TaskStatus.CANCELLED.value
                task.end_time = datetime.now()
                await session.commit()
        logger.info(f"任务已取消: {task_id}")
        return True

    async def delete_task(self, task_id: str) -> bool:
        """删除任务记录"""
        # 先取消任务
        if task_id in self._runners:
            await self.cancel_task(task_id)
        async with async_session() as session:
            task = await session.get(Task, task_id)
            if task:
                await session.delete(task)
                await session.commit()
                logger.info(f"任务已删除: {task_id}")
                return True
            return False

    async def get_task_progress(self, task_id: str) -> Optional[dict]:
        """获取任务进度"""
        async with async_session() as session:
            task = await session.get(Task, task_id)
            if not task:
                return None
            return {
                "current_count": task.current_count,
                "target_count": task.target_count,
                "fail_count": task.fail_count,
                "progress": task.progress,
                "status": task.status,
            }

    def is_paused(self, task_id: str) -> bool:
        """检查任务是否暂停"""
        event = self._pause_events.get(task_id)
        return event is not None and not event.is_set()

    def is_cancelled(self, task_id: str) -> bool:
        """检查任务是否取消"""
        return self._cancel_flags.get(task_id, False)

    def get_pause_event(self, task_id: str) -> asyncio.Event:
        """获取暂停事件"""
        if task_id not in self._pause_events:
            self._pause_events[task_id] = asyncio.Event()
            self._pause_events[task_id].set()
        return self._pause_events[task_id]

    async def on_task_completed(self, task_id: str, status: str = TaskStatus.COMPLETED.value):
        """任务完成回调"""
        self._runners.pop(task_id, None)
        self._pause_events.pop(task_id, None)
        self._cancel_flags.pop(task_id, None)
        async with async_session() as session:
            task = await session.get(Task, task_id)
            if task:
                task.status = status
                task.end_time = datetime.now()
                task.progress = 100 if status == TaskStatus.COMPLETED.value else task.progress
                await session.commit()

            # 更新策略日志
            from sqlalchemy import update
            from sqlalchemy import select as sa_select
            stmt = sa_select(TaskStrategyLog).where(TaskStrategyLog.task_id == task_id)
            result = await session.execute(stmt)
            strategy_log = result.scalar_one_or_none()
            if strategy_log:
                strategy_log.status = status
                strategy_log.end_time = datetime.now()
                if task and task.start_time:
                    strategy_log.duration_seconds = int((datetime.now() - task.start_time).total_seconds())
                strategy_log.success_count = task.current_count if task else 0
                strategy_log.fail_count = task.fail_count if task else 0
                strategy_log.total_attempted = (task.current_count + task.fail_count) if task else 0
                await session.commit()


# 全局任务管理器
task_manager = TaskManager()