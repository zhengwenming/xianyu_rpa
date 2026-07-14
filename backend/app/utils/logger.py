"""日志系统 - 标准 logging + 文件 Handler + WebSocket Handler + 数据库 Handler"""
import os
import json
import logging
import logging.handlers
import asyncio
from datetime import datetime
from collections import defaultdict
from typing import Optional
from fastapi import WebSocket
from app.config import settings


class WebSocketManager:
    """WebSocket 连接管理器 - 管理所有日志客户端连接"""

    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._filters: dict[str, dict] = {}  # 连接ID -> 过滤条件

    def add(self, connection_id: str, websocket: WebSocket, filters: dict = None):
        self._connections[connection_id] = websocket
        self._filters[connection_id] = filters or {}

    def remove(self, connection_id: str):
        self._connections.pop(connection_id, None)
        self._filters.pop(connection_id, None)

    async def broadcast(self, message: dict):
        """广播消息到所有连接的客户端"""
        dead_connections = []
        for cid, ws in self._connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                dead_connections.append(cid)
        for cid in dead_connections:
            self.remove(cid)

    async def broadcast_filtered(self, message: dict):
        """根据过滤条件广播"""
        dead_connections = []
        for cid, ws in self._connections.items():
            try:
                filters = self._filters.get(cid, {})
                # 按级别过滤
                level_filter = filters.get("level")
                if level_filter and message.get("level") not in level_filter:
                    continue
                # 按任务ID过滤
                task_filter = filters.get("task_id")
                if task_filter and message.get("task_id") != task_filter:
                    continue
                await ws.send_json(message)
            except Exception:
                dead_connections.append(cid)
        for cid in dead_connections:
            self.remove(cid)

    def get_connection_count(self) -> int:
        return len(self._connections)


ws_manager = WebSocketManager()


class WebSocketLogHandler(logging.Handler):
    """自定义日志 Handler - 通过 WebSocket 推送日志到前端"""

    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "task_id": getattr(record, "task_id", None),
            "shop_id": getattr(record, "shop_id", None),
            "logger": record.name,
        }
        try:
            asyncio.create_task(ws_manager.broadcast_filtered(log_entry))
        except Exception:
            pass


class DatabaseLogHandler(logging.Handler):
    """自定义日志 Handler - 将日志写入 SQLite 数据库"""

    def __init__(self, session_factory=None):
        super().__init__()
        self.session_factory = session_factory
        self.setFormatter(logging.Formatter("%(message)s"))

    def emit(self, record: logging.LogRecord):
        if not self.session_factory:
            return
        try:
            from app.models.log import RunLog
            from app.database import async_session
            import asyncio

            log_entry = RunLog(
                task_id=getattr(record, "task_id", None),
                shop_id=getattr(record, "shop_id", None),
                level=record.levelname.lower(),
                message=record.getMessage(),
            )
            # 异步写入数据库
            asyncio.create_task(self._save_log(log_entry))
        except Exception:
            pass

    async def _save_log(self, log_entry):
        try:
            from app.database import async_session
            async with async_session() as session:
                session.add(log_entry)
                await session.commit()
        except Exception:
            pass


def setup_logger(name: str = "xianyu_auto") -> logging.Logger:
    """配置并返回日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # 控制台 Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(console_handler)

    # 文件 Handler（按天滚动）
    log_file = os.path.join(settings.LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=settings.LOG_RETENTION_DAYS,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(file_handler)

    # WebSocket Handler
    ws_handler = WebSocketLogHandler()
    logger.addHandler(ws_handler)

    # 数据库 Handler
    db_handler = DatabaseLogHandler()
    logger.addHandler(db_handler)

    return logger


logger = setup_logger()


def get_logger(name: str = None) -> logging.Logger:
    """获取指定名称的日志记录器"""
    if name:
        return logging.getLogger(name)
    return logger