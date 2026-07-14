"""任务策略日志模型 - 以任务维度记录执行策略和结果"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from app.database import Base
from app.utils.helpers import generate_uuid, now


class TaskStrategyLog(Base):
    __tablename__ = "task_strategy_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), nullable=False, index=True, comment="关联任务ID")
    task_name = Column(String(200), nullable=True, comment="任务名称")
    shop_id = Column(String(36), nullable=False, index=True, comment="关联店铺")
    shop_name = Column(String(100), nullable=True, comment="店铺名称")
    product_category = Column(String(50), nullable=True, comment="商品类别")
    keywords = Column(Text, nullable=True, comment="采集关键词（JSON）")
    strategy_config = Column(Text, nullable=True, comment="策略配置快照（JSON）")
    target_count = Column(Integer, default=0, comment="目标上架数量")
    success_count = Column(Integer, default=0, comment="成功数量")
    fail_count = Column(Integer, default=0, comment="失败数量")
    total_attempted = Column(Integer, default=0, comment="总尝试数")
    status = Column(String(20), default="running", comment="running/paused/completed/cancelled/failed/interrupted")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    duration_seconds = Column(Integer, nullable=True, comment="总耗时（秒）")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "shop_id": self.shop_id,
            "shop_name": self.shop_name,
            "product_category": self.product_category,
            "keywords": self.keywords,
            "strategy_config": self.strategy_config,
            "target_count": self.target_count,
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "total_attempted": self.total_attempted,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }