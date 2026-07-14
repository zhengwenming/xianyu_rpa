"""下架日志模型 - 记录自动下架商品明细"""
from sqlalchemy import Column, String, DateTime, Text
from app.database import Base
from app.utils.helpers import generate_uuid, now


class DelistingLog(Base):
    __tablename__ = "delisting_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    shop_id = Column(String(36), nullable=False, index=True, comment="关联店铺")
    shop_name = Column(String(100), nullable=True, comment="店铺名称（冗余）")
    task_id = Column(String(36), nullable=True, index=True, comment="关联任务")
    product_title = Column(String(300), nullable=True, comment="商品标题")
    xianyu_item_id = Column(String(100), nullable=True, comment="闲鱼商品ID")
    delist_reason = Column(String(50), nullable=True, comment="下架原因：sold_out/violation/manual/expired/strategy")
    delist_type = Column(String(20), default="auto", comment="auto/manual")
    screenshot_path = Column(String(500), nullable=True, comment="下架截图路径")
    delisted_at = Column(DateTime, nullable=True, comment="下架时间")
    created_at = Column(DateTime, default=now)

    def to_dict(self):
        return {
            "id": self.id,
            "shop_id": self.shop_id,
            "shop_name": self.shop_name,
            "task_id": self.task_id,
            "product_title": self.product_title,
            "xianyu_item_id": self.xianyu_item_id,
            "delist_reason": self.delist_reason,
            "delist_type": self.delist_type,
            "screenshot_path": self.screenshot_path,
            "delisted_at": self.delisted_at.isoformat() if self.delisted_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }