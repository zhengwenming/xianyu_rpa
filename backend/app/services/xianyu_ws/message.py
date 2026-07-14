"""消息类型定义"""
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class XianyuMessage:
    """闲鱼消息统一格式"""
    msg_id: str
    sender_id: str
    sender_nickname: str = ""
    receiver_id: str = ""
    cid: str = ""  # 会话ID
    message_type: str = "text"  # text/image/audio/system_card
    content: str = ""
    product_id: Optional[str] = None
    product_info: Optional[dict] = None
    shop_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    raw_data: Optional[bytes] = None


@dataclass
class XianyuMessageToSend:
    """待发送消息"""
    cid: str
    to_user_id: str
    content_type: str = "text"  # text/image
    text: str = ""
    image_url: str = ""
    product_id: Optional[str] = None