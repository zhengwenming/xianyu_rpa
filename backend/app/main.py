"""FastAPI 应用入口"""
import os
import json
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.database import init_db, close_db
from app.routers import shop, task, llm, log, listing_log, delisting_log, task_log, reply, delivery, settings as settings_router
from app.utils.logger import ws_manager, get_logger
from app.utils.helpers import generate_uuid

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    await init_db()
    logger.info("数据库初始化完成")
    yield
    await close_db()
    logger.info("应用已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS 配置（桌面 App 通过 file:// 或 http://localhost:xxx 访问时都要放行）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(shop.router)
app.include_router(task.router)
app.include_router(llm.router)
app.include_router(log.router)
app.include_router(listing_log.router)
app.include_router(delisting_log.router)
app.include_router(task_log.router)
app.include_router(reply.router)
app.include_router(delivery.router)
app.include_router(settings_router.router)


# WebSocket 实时日志端点
@app.websocket("/ws/logs")
async def log_websocket(websocket: WebSocket):
    await websocket.accept()
    connection_id = generate_uuid()
    ws_manager.add(connection_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                filters = json.loads(data)
                ws_manager._filters[connection_id] = filters
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        ws_manager.remove(connection_id)
    except Exception:
        ws_manager.remove(connection_id)


@app.get("/api/system/status")
async def system_status():
    return {
        "code": 0,
        "data": {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "ws_connections": ws_manager.get_connection_count(),
        },
        "message": "ok",
    }


@app.get("/api/system/browser/check")
async def check_browser():
    """检查 Playwright 浏览器是否安装"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            chromium = p.chromium
            return {"code": 0, "data": {"installed": True}, "message": "浏览器已安装"}
    except Exception as e:
        return {"code": 1, "data": {"installed": False}, "message": str(e)}


@app.post("/api/system/browser/install")
async def install_browser():
    """安装 Playwright 浏览器"""
    import subprocess
    try:
        result = subprocess.run(["playwright", "install", "chromium"], capture_output=True, text=True)
        if result.returncode == 0:
            return {"code": 0, "data": None, "message": "浏览器安装成功"}
        return {"code": 1, "data": None, "message": result.stderr}
    except Exception as e:
        return {"code": 1, "data": None, "message": str(e)}


# ─── 前端静态文件挂载 ───
# 打包后前端资源在 static/web/ 目录下
STATIC_WEB_DIR = Path(settings.STATIC_DIR) / "web"


@app.get("/")
async def root():
    """根路径 - 返回前端 index.html 或后端 API 信息"""
    index_html = STATIC_WEB_DIR / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return {"message": f"{settings.APP_NAME} API is running", "version": settings.APP_VERSION,
            "hint": "前端未构建，请先运行 npm run build"}


# 挂载 assets 静态资源（Vite 打包后的 JS/CSS）
if (STATIC_WEB_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_WEB_DIR / "assets")), name="assets")


# SPA fallback：所有非 API 的路径都返回 index.html（Vue Router hash 模式其实不需要，但保险起见）
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    # API 路径不处理
    if full_path.startswith("api/") or full_path.startswith("ws/"):
        return {"detail": "Not Found"}
    # 静态资源
    static_file = STATIC_WEB_DIR / full_path
    if static_file.exists() and static_file.is_file():
        return FileResponse(str(static_file))
    # SPA fallback
    index_html = STATIC_WEB_DIR / "index.html"
    if index_html.exists():
        return FileResponse(str(index_html))
    return {"detail": "Not Found"}
