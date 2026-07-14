"""通用工具函数"""
import uuid
import json
from datetime import datetime
from typing import Any


def generate_uuid() -> str:
    """生成 UUID 字符串"""
    return str(uuid.uuid4())


def now() -> datetime:
    """获取当前时间"""
    return datetime.now()


def serialize_datetime(dt: datetime) -> str:
    """序列化 datetime 为 ISO 格式字符串"""
    return dt.isoformat() if dt else None


def parse_json_safe(s: str, default=None) -> Any:
    """安全解析 JSON 字符串"""
    if not s:
        return default
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return default


def to_json_safe(obj: Any) -> str:
    """安全转换为 JSON 字符串"""
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return "{}"


def mask_sensitive(text: str, keep_last: int = 4) -> str:
    """脱敏处理 - 只保留最后几位"""
    if not text:
        return ""
    if len(text) <= keep_last:
        return "*" * len(text)
    return "*" * (len(text) - keep_last) + text[-keep_last:]