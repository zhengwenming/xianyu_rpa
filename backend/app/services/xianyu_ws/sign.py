"""Sign 签名引擎 - 调用 Node.js 执行逆向 JS"""
import subprocess
import json
import os
from typing import Optional
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SignEngine:
    """闲鱼 sign 签名引擎 — 调用 Node.js 执行逆向 JS"""

    def __init__(self):
        self.js_path = os.path.join(settings.STATIC_DIR, "goofish_js", "goofish_sign.js")

    async def sign(self, params: dict, cookie: str) -> str:
        """
        生成 sign 签名
        :param params: 请求参数
        :param cookie: 当前店铺的 Cookie
        :return: sign 签名字符串
        """
        if not os.path.exists(self.js_path):
            logger.warning(f"签名 JS 文件不存在: {self.js_path}")
            return "mock_sign_placeholder"

        input_data = json.dumps({"params": params, "cookie": cookie})
        try:
            result = subprocess.run(
                ["node", self.js_path],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Sign JS 执行失败: {result.stderr}")
            return json.loads(result.stdout)["sign"]
        except FileNotFoundError:
            logger.warning("Node.js 未安装，使用模拟签名")
            return "mock_sign_placeholder"
        except Exception as e:
            logger.error(f"签名生成失败: {e}")
            return "mock_sign_placeholder"


# 全局实例
sign_engine = SignEngine()