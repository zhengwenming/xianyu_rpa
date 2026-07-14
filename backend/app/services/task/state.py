"""任务状态机"""
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"        # 等待中
    RUNNING = "running"        # 执行中
    PAUSED = "paused"          # 已暂停（可恢复）
    CANCELLED = "cancelled"    # 已取消（终态）
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败


# 合法状态转换
VALID_TRANSITIONS = {
    TaskStatus.PENDING: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
    TaskStatus.RUNNING: [TaskStatus.PAUSED, TaskStatus.CANCELLED, TaskStatus.COMPLETED, TaskStatus.FAILED],
    TaskStatus.PAUSED: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
    TaskStatus.CANCELLED: [],
    TaskStatus.COMPLETED: [],
    TaskStatus.FAILED: [],
}


def can_transition(from_status: str, to_status: str) -> bool:
    """检查状态转换是否合法"""
    from_enum = TaskStatus(from_status)
    to_enum = TaskStatus(to_status)
    return to_enum in VALID_TRANSITIONS.get(from_enum, [])