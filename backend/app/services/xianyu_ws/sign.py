"""Sign 签名引擎 - 调用 Node.js 执行逆向 JS"""
import subprocess
import json
import os
import re
from typing import Optional

import httpx

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# goofish web 默认 appKey
DEFAULT_APP_KEY = "34839810"
# 用于探测 _m_h5_tk 的 mtop 接口（任意 h5 接口即可，服务端会在响应里下发 token）
TOKEN_PROBE_URL = (
    "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopwriteservice.pc.nav/1.0/"
)


def extract_h5_token(cookie: str) -> str:
    """从 Cookie 中提取 _m_h5_tk 的 token 部分（'_' 前的一段）。"""
    if not cookie:
        return ""
    match = re.search(r"_m_h5_tk=([^;]+)", cookie)
    if not match:
        return ""
    return match.group(1).split("_")[0]


def merge_cookie(cookie: str, extra: dict) -> str:
    """把新的 cookie 键值合并进原始 cookie 字符串，同名键覆盖。"""
    jar: dict = {}
    for part in (cookie or "").split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        jar[k.strip()] = v.strip()
    jar.update(extra)
    return "; ".join(f"{k}={v}" for k, v in jar.items())


class SignEngine:
    """闲鱼 sign 签名引擎 — 调用 Node.js 执行逆向 JS"""

    def __init__(self):
        self.js_path = os.path.join(settings.STATIC_DIR, "goofish_js", "goofish_sign.js")

    async def ensure_token(self, cookie: str) -> str:
        """
        确保 Cookie 中包含有效的 _m_h5_tk。
        若缺失，则向 mtop 接口发一次探测请求，从响应的 Set-Cookie 中取回
        _m_h5_tk（以及可能的 _m_h5_tk_enc），合并进 cookie 后返回。
        无法获取时原样返回，让上层继续（服务端会返回 TOKEN_EMPTY，可再次重试）。
        """
        if extract_h5_token(cookie):
            return cookie

        try:
            async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
                resp = await client.get(
                    TOKEN_PROBE_URL,
                    params={
                        "jsv": "2.7.2",
                        "appKey": DEFAULT_APP_KEY,
                        "type": "originaljson",
                        "dataType": "json",
                        "data": "{}",
                    },
                    headers={
                        "Cookie": cookie,
                        "User-Agent": (
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36"
                        ),
                        "Referer": "https://www.goofish.com/",
                    },
                )
            new_cookies = {
                name: value
                for name, value in resp.cookies.items()
                if name.startswith("_m_h5_tk")
            }
            if new_cookies:
                cookie = merge_cookie(cookie, new_cookies)
                logger.info("已从 mtop 探测响应中获取 _m_h5_tk token")
            else:
                logger.warning("探测响应未返回 _m_h5_tk，签名可能被拒绝")
        except Exception as e:
            logger.warning(f"探测 _m_h5_tk 失败: {e}")

        return cookie

    async def sign(self, params: dict, cookie: str) -> str:
        """
        生成 sign 签名
        :param params: 请求参数（可含 t / appKey / data）
        :param cookie: 当前店铺的 Cookie
        :return: sign 签名字符串
        """
        if not os.path.exists(self.js_path):
            logger.warning(f"签名 JS 文件不存在: {self.js_path}")
            return "mock_sign_placeholder"

        # 确保 cookie 含有效 _m_h5_tk，否则先探测拿 token
        cookie = await self.ensure_token(cookie)

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