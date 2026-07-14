"""运行日志模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from app.utils.helpers import generate_uuid, now


class RunLog(Base):
    __tablename__ = "run_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(36), nullable=True, index=True, comment="关联任务ID")
    shop_id = Column(String(36), nullable=True, index=True, comment="关联店铺ID")
    timestamp = Column(DateTime, default=now, index=True, comment="时间戳")
    level = Column(String(10), default="info", comment="debug/info/warning/error")
    message = Column(Text, nullable=False, comment="日志内容")
    extra = Column(Text, nullable=True, comment="附加信息JSON")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "shop_id": self.shop_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "message": self.message,
            "extra": self.extra,
        }