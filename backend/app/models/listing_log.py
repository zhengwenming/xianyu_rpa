"""上架日志模型 - 记录每次上架操作的结果明细"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from app.database import Base
from app.utils.helpers import generate_uuid, now


class ListingLog(Base):
    __tablename__ = "listing_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    shop_id = Column(String(36), nullable=False, index=True, comment="关联店铺")
    shop_name = Column(String(100), nullable=True, comment="店铺名称（冗余）")
    task_id = Column(String(36), nullable=True, index=True, comment="关联任务")
    product_title = Column(String(300), nullable=True, comment="闲鱼上架标题")
    source_url = Column(String(500), nullable=True, comment="1688来源URL")
    source_supplier = Column(String(200), nullable=True, comment="1688供应商")
    source_price = Column(Float, nullable=True, comment="1688采集价格")
    listing_price = Column(Float, nullable=True, comment="闲鱼上架价格")
    image_urls = Column(Text, nullable=True, comment="图片URL列表（JSON）")
    status = Column(String(20), default="success", comment="success/failed")
    fail_reason = Column(Text, nullable=True, comment="失败原因")
    screenshot_path = Column(String(500), nullable=True, comment="失败截图路径")
    listed_at = Column(DateTime, nullable=True, comment="上架时间")
    created_at = Column(DateTime, default=now)

    def to_dict(self):
        return {
            "id": self.id,
            "shop_id": self.shop_id,
            "shop_name": self.shop_name,
            "task_id": self.task_id,
            "product_title": self.product_title,
            "source_url": self.source_url,
            "source_supplier": self.source_supplier,
            "source_price": self.source_price,
            "listing_price": self.listing_price,
            "image_urls": self.image_urls,
            "status": self.status,
            "fail_reason": self.fail_reason,
            "screenshot_path": self.screenshot_path,
            "listed_at": self.listed_at.isoformat() if self.listed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }