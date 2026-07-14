"""店铺模型"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import Mapped
from app.database import Base
from app.utils.helpers import generate_uuid, now


class Shop(Base):
    __tablename__ = "shops"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, comment="店铺名称")
    status = Column(String(20), default="active", comment="active/inactive")
    login_status = Column(String(20), default="unauthorized", comment="authorized/unauthorized/expired")
    session_path = Column(String(500), nullable=True, comment="会话文件路径")
    authorized_at = Column(DateTime, nullable=True, comment="授权时间")
    last_active_time = Column(DateTime, nullable=True, comment="最近活跃时间")
    xianyu_user_id = Column(String(100), nullable=True, comment="闲鱼用户ID")
    xianyu_nickname = Column(String(100), nullable=True, comment="闲鱼昵称")
    xianyu_avatar = Column(String(500), nullable=True, comment="闲鱼头像URL")
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "login_status": self.login_status,
            "session_path": self.session_path,
            "authorized_at": self.authorized_at.isoformat() if self.authorized_at else None,
            "last_active_time": self.last_active_time.isoformat() if self.last_active_time else None,
            "xianyu_user_id": self.xianyu_user_id,
            "xianyu_nickname": self.xianyu_nickname,
            "xianyu_avatar": self.xianyu_avatar,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }