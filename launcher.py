#!/usr/bin/env python3
"""
闲鱼自动化铺货系统 - 桌面版启动入口
一个进程搞定：内嵌 FastAPI 后端 + WebView 前端 UI

启动流程：
1. 在后台线程启动 FastAPI (uvicorn)
2. 主线程打开 pywebview 窗口，加载 http://localhost:8765
3. 关闭窗口时优雅退出后端
"""
import os
import sys
import time
import socket
import threading
from pathlib import Path


# ─── 开发模式下自动激活虚拟环境 ───
def ensure_venv():
    """开发模式下确保运行在虚拟环境中；打包后跳过"""
    if getattr(sys, "frozen", False):
        return  # PyInstaller 打包后不需要 venv
    project_dir = Path(__file__).parent.resolve()
    venv_dir = project_dir / "backend" / "venv"
    if os.name == "nt":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
    if not venv_python.exists():
        return  # 没venv就不切
    if str(Path(sys.prefix).resolve()) != str(venv_dir):
        os.execv(str(venv_python), [str(venv_python), __file__] + sys.argv[1:])


ensure_venv()


# ─── 把 backend/ 加到 Python 路径，让 `app.main` 能被导入 ───
_project_dir = Path(__file__).parent.resolve()
_backend_dir = _project_dir / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))


def find_free_port(preferred: int = 8765) -> int:
    """尝试用首选端口，被占用则找一个可用端口"""
    for port in [preferred] + list(range(9000, 9100)):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    return preferred


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """等待后端服务器启动"""
    import urllib.request
    start = time.time()
    while time.time() - start < timeout:
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.2)
    return False


def start_backend(port: int):
    """在后台线程启动 FastAPI 后端"""
    import uvicorn
    # 这里 import 是延迟的，此时 sys.path 已经包含 backend/
    from app.main import app as fastapi_app
    from app.config import settings

    settings.PORT = port
    settings.HOST = "127.0.0.1"
    settings.DEBUG = False

    config = uvicorn.Config(
        fastapi_app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    server.run()


def main():
    port = find_free_port(8765)
    server_url = f"http://127.0.0.1:{port}"

    print(f"🚀 启动闲鱼自动化铺货系统...")
    print(f"   后端端口: {port}")

    backend_thread = threading.Thread(target=start_backend, args=(port,), daemon=True)
    backend_thread.start()

    if not wait_for_server(f"{server_url}/api/system/status", timeout=30):
        print("❌ 后端启动超时，请检查日志")
        sys.exit(1)

    print(f"✅ 后端已就绪，打开桌面窗口...")

    import webview

    def on_closed():
        print("👋 窗口关闭，退出程序")
        os._exit(0)

    window = webview.create_window(
        title="闲鱼自动化铺货系统",
        url=server_url,
        width=1400,
        height=900,
        min_size=(1024, 700),
        resizable=True,
        text_select=True,
        confirm_close=False,
    )
    window.events.closed += on_closed

    webview.start(debug=False)


if __name__ == "__main__":
    main()
