"""协议封装 - sign 签名 + 消息编解码"""
import json
import base64
from typing import Optional
from app.services.xianyu_ws.message import XianyuMessage, XianyuMessageToSend
from app.utils.helpers import generate_uuid
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ProtocolCodec:
    """协议编解码器"""

    @staticmethod
    def decode_message(raw_data: bytes) -> Optional[XianyuMessage]:
        """解码原始消息为统一格式"""
        try:
            # 尝试直接 JSON 解析（部分消息是 JSON 格式）
            text = raw_data.decode("utf-8", errors="ignore")
            data = json.loads(text)

            # 提取关键字段
            msg = XianyuMessage(
                msg_id=data.get("msgId", data.get("id", generate_uuid())),
                sender_id=data.get("senderId", data.get("sender", "")),
                sender_nickname=data.get("senderNickname", data.get("nickname", "")),
                receiver_id=data.get("receiverId", data.get("receiver", "")),
                cid=data.get("cid", data.get("conversationId", "")),
                message_type=data.get("type", "text"),
                content=data.get("content", data.get("text", "")),
                product_id=data.get("productId", data.get("itemId")),
                raw_data=raw_data,
            )
            return msg

        except json.JSONDecodeError:
            # 尝试 Protobuf 解码（base64 + Protobuf）
            try:
                # 简单尝试 base64 解码
                decoded = base64.b64decode(text)
                # 尝试解析 Protobuf（使用 blackprotobuf）
                try:
                    import blackprotobuf
                    parsed = blackprotobuf.decode_message(decoded)
                    return XianyuMessage(
                        msg_id=str(parsed.get("msgId", generate_uuid())),
                        sender_id=str(parsed.get("senderId", "")),
                        cid=str(parsed.get("cid", "")),
                        message_type="text",
                        content=str(parsed.get("content", "")),
                        raw_data=raw_data,
                    )
                except ImportError:
                    pass
            except Exception:
                pass

            # 无法解析，返回原始数据
            return XianyuMessage(
                msg_id=generate_uuid(),
                sender_id="",
                message_type="unknown",
                content=text[:200],
                raw_data=raw_data,
            )

    @staticmethod
    def encode_message(msg: XianyuMessageToSend) -> bytes:
        """编码待发送消息为协议格式"""
        payload = {
            "cid": msg.cid,
            "toUserId": msg.to_user_id,
            "type": msg.content_type,
            "content": msg.text,
        }
        if msg.image_url:
            payload["imageUrl"] = msg.image_url
        if msg.product_id:
            payload["productId"] = msg.product_id

        # JSON 序列化后发送
        return json.dumps(payload, ensure_ascii=False).encode("utf-8")


# 全局实例
protocol_codec = ProtocolCodec()