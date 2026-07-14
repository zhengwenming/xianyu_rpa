"""发货配置与日志模型"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float
from app.database import Base
from app.utils.helpers import generate_uuid, now


class DeliveryConfig(Base):
    """发货配置"""
    __tablename__ = "delivery_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    shop_id = Column(String(36), nullable=False, comment="关联店铺")
    product_id = Column(String(100), nullable=False, comment="闲鱼商品ID")
    product_title = Column(String(300), nullable=True, comment="商品标题")
    delivery_type = Column(String(20), nullable=False, comment="card/link/text/proxy")
    card_pool = Column(Text, nullable=True, comment="卡池（JSON数组）")
    link_url = Column(String(500), nullable=True, comment="网盘链接")
    link_code = Column(String(50), nullable=True, comment="提取码")
    text_content = Column(Text, nullable=True, comment="纯文本发货内容")
    source_url = Column(String(500), nullable=True, comment="1688源商品URL")
    auto_ship = Column(Boolean, default=True, comment="是否自动发货")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    def to_dict(self):
        return {
            "id": self.id,
            "shop_id": self.shop_id,
            "product_id": self.product_id,
            "product_title": self.product_title,
            "delivery_type": self.delivery_type,
            "card_pool_count": len(self._parse_card_pool()),
            "link_url": self.link_url,
            "link_code": self.link_code,
            "text_content": self.text_content[:100] + "..." if self.text_content and len(self.text_content) > 100 else self.text_content,
            "source_url": self.source_url,
            "auto_ship": self.auto_ship,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def _parse_card_pool(self) -> list:
        import json
        if not self.card_pool:
            return []
        try:
            return json.loads(self.card_pool)
        except json.JSONDecodeError:
            return []


class DeliveryLog(Base):
    """发货日志"""
    __tablename__ = "delivery_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    shop_id = Column(String(36), nullable=False, comment="关联店铺")
    order_id = Column(String(100), nullable=True, comment="订单ID")
    product_id = Column(String(100), nullable=True, comment="商品ID")
    product_title = Column(String(300), nullable=True, comment="商品标题")
    buyer_id = Column(String(100), nullable=True, comment="买家ID")
    delivery_type = Column(String(20), nullable=True, comment="发货类型")
    tracking_no = Column(String(100), nullable=True, comment="物流单号")
    status = Column(String(20), default="success", comment="success/failed")
    error_message = Column(Text, nullable=True, comment="错误信息")
    shipped_at = Column(DateTime, nullable=True, comment="发货时间")
    created_at = Column(DateTime, default=now)

    def to_dict(self):
        return {
            "id": self.id,
            "shop_id": self.shop_id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_title": self.product_title,
            "buyer_id": self.buyer_id,
            "delivery_type": self.delivery_type,
            "tracking_no": self.tracking_no,
            "status": self.status,
            "error_message": self.error_message,
            "shipped_at": self.shipped_at.isoformat() if self.shipped_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }