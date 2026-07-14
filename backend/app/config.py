"""应用配置管理 - Pydantic Settings"""
import os
import sys
from pathlib import Path
from pydantic_settings import BaseSettings


def get_app_data_dir() -> Path:
    """
    获取应用数据目录 - 打包后 vs 开发模式使用不同路径

    - 打包后（PyInstaller）：使用用户目录下的 ~/.xianyu_auto/
    - 开发模式：使用项目目录下的 backend/data/
    """
    # PyInstaller 打包后，sys.frozen 为 True
    if getattr(sys, "frozen", False):
        # 使用用户目录（可写、跨平台）
        if sys.platform == "win32":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        data_dir = base / "XianyuAuto"
    else:
        # 开发模式：项目本地目录
        data_dir = Path(__file__).parent.parent / "data"

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_static_dir() -> Path:
    """获取静态资源目录（前端文件、签名JS等）"""
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后，资源在 _MEIPASS 临时目录
        base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(sys.executable).parent
        return base / "static"
    else:
        return Path(__file__).parent.parent / "static"


APP_DATA_DIR = get_app_data_dir()
STATIC_DIR_PATH = get_static_dir()


class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "闲鱼自动化铺货系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # 打包后默认关闭 DEBUG

    # 服务器配置
    HOST: str = "127.0.0.1"  # 桌面 App 只监听本地
    PORT: int = 8765

    # 数据库（用户数据目录）
    DATABASE_URL: str = f"sqlite+aiosqlite:///{APP_DATA_DIR}/xianyu_auto.db"

    # 前端地址（CORS，桌面模式下不需要）
    FRONTEND_URL: str = "*"

    # 加密密钥
    ENCRYPTION_KEY: str = ""

    # 日志（用户数据目录）
    LOG_DIR: str = str(APP_DATA_DIR / "logs")
    LOG_LEVEL: str = "INFO"
    LOG_RETENTION_DAYS: int = 30

    # 会话存储（用户数据目录）
    SESSION_DIR: str = str(APP_DATA_DIR / "sessions")

    # 静态资源目录（前端 + 签名JS等）
    STATIC_DIR: str = str(STATIC_DIR_PATH)

    # 闲鱼 WebSocket 配置
    XIANYU_WSS_URL: str = "wss://wss-goofish.dingtalk.com/lh/"
    XIANYU_API_BASE: str = "https://api.goofish.com"

    # 任务默认配置
    DEFAULT_TARGET_COUNT: int = 10
    DEFAULT_POST_DELAY: int = 30
    DEFAULT_PRICE_MARKUP_RATIO: float = 1.3
    DEFAULT_PRICE_MARKUP_AMOUNT: float = 0.0

    WS_HEARTBEAT_INTERVAL: int = 30
    ORDER_POLL_INTERVAL: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# 确保必要的目录存在
os.makedirs(settings.LOG_DIR, exist_ok=True)
os.makedirs(settings.SESSION_DIR, exist_ok=True)
