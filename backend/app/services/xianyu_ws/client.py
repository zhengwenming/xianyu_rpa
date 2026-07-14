"""闲鱼 WebSocket 客户端"""
import json
import asyncio
import time
from typing import Optional, Callable, Awaitable
from websockets import connect
from websockets.exceptions import ConnectionClosed
from app.config import settings
from app.services.xianyu_ws.sign import sign_engine
from app.services.xianyu_ws.protocol import protocol_codec
from app.services.xianyu_ws.message import XianyuMessage, XianyuMessageToSend
from app.utils.logger import get_logger

logger = get_logger(__name__)


class XianyuWebSocketClient:
    """闲鱼 WebSocket 客户端"""

    def __init__(self, shop_id: str, cookie: str):
        self.shop_id = shop_id
        self.cookie = cookie
        self.ws = None
        self._running = False
        self._on_message_callback: Optional[Callable[[XianyuMessage], Awaitable[None]]] = None
        self._reconnect_count = 0
        self._max_reconnect = 10

    async def connect(self):
        """建立 WebSocket 连接"""
        try:
            sign = await sign_engine.sign(
                {"ts": str(int(time.time() * 1000))},
                self.cookie,
            )
            headers = {
                "Cookie": self.cookie,
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            }
            # 添加 sign 到 URL 参数
            ws_url = f"{settings.XIANYU_WSS_URL}?sign={sign}"
            self.ws = await connect(ws_url, extra_headers=headers, ping_interval=30)
            self._running = True
            self._reconnect_count = 0
            logger.info(f"店铺 {self.shop_id} WebSocket 连接成功")
            return True

        except Exception as e:
            logger.error(f"店铺 {self.shop_id} WebSocket 连接失败: {e}")
            return False

    async def listen(self, on_message: Callable[[XianyuMessage], Awaitable[None]]):
        """监听消息"""
        self._on_message_callback = on_message
        while self._running:
            try:
                async for raw_data in self.ws:
                    if not self._running:
                        break
                    try:
                        message = protocol_codec.decode_message(raw_data)
                        if message and message.sender_id:
                            message.shop_id = self.shop_id
                            if self._on_message_callback:
                                asyncio.create_task(self._on_message_callback(message))
                    except Exception as e:
                        logger.error(f"消息处理失败: {e}")

            except ConnectionClosed:
                if self._running:
                    logger.warning(f"店铺 {self.shop_id} WebSocket 连接断开，尝试重连...")
                    await self.reconnect()
            except Exception as e:
                logger.error(f"消息监听异常: {e}")
                if self._running:
                    await self.reconnect()

    async def send_message(self, msg: XianyuMessageToSend):
        """发送消息"""
        if not self.ws or not self._running:
            raise RuntimeError("WebSocket 未连接")
        data = protocol_codec.encode_message(msg)
        await self.ws.send(data)

    async def send_text(self, cid: str, to_user_id: str, text: str):
        """发送文本消息"""
        msg = XianyuMessageToSend(
            cid=cid,
            to_user_id=to_user_id,
            content_type="text",
            text=text,
        )
        await self.send_message(msg)

    async def heartbeat(self):
        """心跳保活"""
        while self._running:
            try:
                await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)
                if self.ws and self._running:
                    await self.ws.send(json.dumps({"type": "heartbeat"}))
            except Exception as e:
                logger.warning(f"心跳发送失败: {e}")
                break

    async def reconnect(self):
        """断线重连"""
        self._reconnect_count += 1
        if self._reconnect_count > self._max_reconnect:
            logger.error(f"店铺 {self.shop_id} 重连次数超限，停止重连")
            self._running = False
            return

        wait_time = min(5 * self._reconnect_count, 60)
        logger.info(f"店铺 {self.shop_id} 将在 {wait_time} 秒后重连 (第{self._reconnect_count}次)")
        await asyncio.sleep(wait_time)

        if not self._running:
            return

        await self.close()
        success = await self.connect()
        if success:
            # 重新启动监听
            if self._on_message_callback:
                asyncio.create_task(self.listen(self._on_message_callback))
            asyncio.create_task(self.heartbeat())

    async def close(self):
        """关闭连接"""
        self._running = False
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
            self.ws = None