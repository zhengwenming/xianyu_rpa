"""多店铺 WebSocket 连接管理器"""
from typing import Optional
from app.services.xianyu_ws.client import XianyuWebSocketClient
from app.services.xianyu_ws.sign import sign_engine
from app.services.browser.session import session_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class XianyuConnectionManager:
    """多店铺 WebSocket 连接管理器"""

    def __init__(self):
        self._connections: dict[str, XianyuWebSocketClient] = {}
        self._reply_engine = None

    def set_reply_engine(self, reply_engine):
        """设置回复引擎引用"""
        self._reply_engine = reply_engine

    async def start_shop(self, shop_id: str, shop_name: str = ""):
        """启动指定店铺的 WebSocket 连接"""
        if shop_id in self._connections:
            logger.info(f"店铺 {shop_name or shop_id} 已连接，跳过")
            return True

        cookie = await session_manager.get_cookie_string(shop_id)
        if not cookie:
            logger.error(f"店铺 {shop_name or shop_id} 无 Cookie，无法连接")
            return False

        client = XianyuWebSocketClient(shop_id, cookie)
        success = await client.connect()
        if not success:
            return False

        # 启动心跳
        asyncio.create_task(client.heartbeat())

        # 启动消息监听（如果回复引擎已设置）
        if self._reply_engine:
            asyncio.create_task(
                client.listen(on_message=self._reply_engine.handle)
            )

        self._connections[shop_id] = client
        logger.info(f"店铺 {shop_name or shop_id} WebSocket 连接已启动")
        return True

    async def stop_shop(self, shop_id: str):
        """停止指定店铺的连接"""
        if shop_id in self._connections:
            await self._connections[shop_id].close()
            del self._connections[shop_id]
            logger.info(f"店铺 {shop_id} WebSocket 连接已停止")

    async def stop_all(self):
        """停止所有连接"""
        for shop_id in list(self._connections.keys()):
            await self.stop_shop(shop_id)

    def get_status(self, shop_id: str) -> str:
        """获取店铺连接状态"""
        if shop_id in self._connections:
            return "connected"
        return "disconnected"

    def get_all_status(self) -> dict[str, str]:
        """获取所有店铺连接状态"""
        return {
            shop_id: "connected" if client._running else "disconnected"
            for shop_id, client in self._connections.items()
        }

    async def send_message(self, shop_id: str, to_user_id: str, text: str, cid: str = ""):
        """通过店铺连接发送消息"""
        if shop_id not in self._connections:
            raise RuntimeError(f"店铺 {shop_id} 未连接")
        await self._connections[shop_id].send_text(cid, to_user_id, text)


# 全局实例
connection_manager = XianyuConnectionManager()

import asyncio