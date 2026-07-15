"""任务模型"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from app.database import Base
from app.utils.helpers import generate_uuid, now


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(200), nullable=False, comment="任务名称")
    shop_id = Column(String(36), nullable=False, comment="关联店铺ID")
    shop_name = Column(String(100), nullable=True, comment="店铺名称（冗余）")
    keywords = Column(Text, nullable=True, comment="采集关键词（JSON数组）")
    source_urls = Column(Text, nullable=True, comment="1688商品URL列表（JSON数组）")
    target_count = Column(Integer, default=10, comment="目标上架数量")
    current_count = Column(Integer, default=0, comment="当前已上架数量")
    fail_count = Column(Integer, default=0, comment="失败数量")
    llm_config_id = Column(String(36), nullable=True, comment="LLM配置ID")
    image_plan = Column(String(20), default="original", comment="图片方案：original/ai_enhance/ai_generate")
    status = Column(String(20), default="pending", comment="pending/running/paused/cancelled/completed/failed")
    category = Column(String(50), nullable=True, comment="商品类别")
    progress = Column(Integer, default=0, comment="进度百分比")
    error_message = Column(Text, nullable=True, comment="错误信息")
    start_time = Column(DateTime, nullable=True, comment="开始时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    TRANSITIONS = {
        "pending": ["running", "cancelled"],
        "running": ["paused", "cancelled", "completed", "failed"],
        "paused": ["running", "cancelled"],
        "cancelled": ["running"],
        "completed": ["running"],
        "failed": ["running"],
    }

    def can_transition_to(self, target_status: str) -> bool:
        return target_status in self.TRANSITIONS.get(self.status, [])

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "shop_id": self.shop_id,
            "shop_name": self.shop_name,
            "keywords": self.keywords,
            "source_urls": self.source_urls,
            "target_count": self.target_count,
            "current_count": self.current_count,
            "fail_count": self.fail_count,
            "llm_config_id": self.llm_config_id,
            "image_plan": self.image_plan,
            "status": self.status,
            "category": self.category,
            "progress": self.progress,
            "error_message": self.error_message,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }