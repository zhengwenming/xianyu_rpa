"""全局设置模型"""
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, Text
from app.database import Base
from app.utils.helpers import now


class GlobalSettings(Base):
    """全局设置 - 单例模式（id=1）"""
    __tablename__ = "global_settings"

    id = Column(Integer, primary_key=True, default=1)

    # 图片与视频设置
    enable_ai_main_video = Column(Boolean, default=False, comment="AI主图视频")
    enable_smart_crop_3_4 = Column(Boolean, default=True, comment="智能裁剪主图3:4")
    enable_ai_short_title = Column(Boolean, default=False, comment="AI导购短标题")

    # 价格设置
    price_markup_ratio = Column(Float, default=1.3, comment="加价比例")
    price_markup_amount = Column(Float, default=0.0, comment="加价金额")

    # 过滤与屏蔽
    supplier_blacklist = Column(Text, default="[]", comment="供应商黑名单（JSON数组）")
    keyword_blocklist = Column(Text, default="[]", comment="关键词屏蔽（JSON数组）")

    # 节奏控制
    post_listing_delay = Column(Integer, default=30, comment="上货后延迟秒数")
    simulated_pause_interval = Column(Integer, default=15, comment="模拟暂停休息分钟")
    simulated_pause_count = Column(Integer, default=10, comment="每隔多少个商品触发暂停")

    # 目标控制
    target_success_count = Column(Integer, default=10, comment="目标成功个数")

    # 元数据
    updated_at = Column(DateTime, default=now, onupdate=now)

    def to_dict(self):
        return {
            "id": self.id,
            "enable_ai_main_video": self.enable_ai_main_video,
            "enable_smart_crop_3_4": self.enable_smart_crop_3_4,
            "enable_ai_short_title": self.enable_ai_short_title,
            "price_markup_ratio": self.price_markup_ratio,
            "price_markup_amount": self.price_markup_amount,
            "supplier_blacklist": self.supplier_blacklist,
            "keyword_blocklist": self.keyword_blocklist,
            "post_listing_delay": self.post_listing_delay,
            "simulated_pause_interval": self.simulated_pause_interval,
            "simulated_pause_count": self.simulated_pause_count,
            "target_success_count": self.target_success_count,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def defaults() -> dict:
        return {
            "enable_ai_main_video": False,
            "enable_smart_crop_3_4": True,
            "enable_ai_short_title": False,
            "price_markup_ratio": 1.3,
            "price_markup_amount": 0.0,
            "supplier_blacklist": "[]",
            "keyword_blocklist": "[]",
            "post_listing_delay": 30,
            "simulated_pause_interval": 15,
            "simulated_pause_count": 10,
            "target_success_count": 10,
        }