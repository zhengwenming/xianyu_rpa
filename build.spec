# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置 - 闲鱼自动化铺货系统
用法:
    pyinstaller build.spec --clean --noconfirm

产物:
    dist/闲鱼自动化铺货系统.app  (macOS)
    dist/闲鱼自动化铺货系统/     (Windows 目录版)
"""
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

PROJECT_ROOT = Path(SPECPATH).resolve()
BACKEND_DIR = PROJECT_ROOT / "backend"

# 应用元信息
APP_NAME = "闲鱼自动化铺货系统"
ENTRY_POINT = str(PROJECT_ROOT / "launcher.py")
ICON_MAC = str(PROJECT_ROOT / "assets" / "icon" / "icon.icns")
ICON_WIN = str(PROJECT_ROOT / "assets" / "icon" / "icon.ico")

# 关键：让 PyInstaller 能找到后端 app 包
# 通过 pathex 让 backend/ 加入模块搜索路径
sys.path.insert(0, str(BACKEND_DIR))


# ─── 资源文件 ───
datas = [
    # 前端打包产物
    (str(BACKEND_DIR / "static" / "web"), "static/web"),
    # 闲鱼签名 JS 文件
    (str(BACKEND_DIR / "static" / "goofish_js"), "static/goofish_js"),
]


# ─── 隐藏导入：显式列出所有 app.* 子模块 ───
app_submodules = collect_submodules("app", filter=lambda name: True)

hiddenimports = app_submodules + [
    # FastAPI / Uvicorn
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    # SQLAlchemy 异步驱动
    "aiosqlite",
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.dialects.sqlite.aiosqlite",
    # Pydantic
    "pydantic.deprecated.decorator",
    # 定时任务
    "apscheduler.schedulers.asyncio",
    "apscheduler.triggers.interval",
    "apscheduler.triggers.cron",
    # WebSocket
    "websockets",
    "websockets.legacy",
    "websockets.legacy.client",
    # LLM SDK
    "openai",
    "anthropic",
]

# 平台相关的 pywebview 后端
if sys.platform == "darwin":
    hiddenimports.append("webview.platforms.cocoa")
elif sys.platform == "win32":
    hiddenimports.append("webview.platforms.edgechromium")
    hiddenimports.append("webview.platforms.winforms")


# 排除不需要的大模块
excludes = [
    "tkinter", "matplotlib", "pandas", "numpy", "scipy",
    "PyQt5", "PyQt6", "PySide2", "PySide6",
    "IPython", "jupyter", "notebook",
    "test", "tests", "unittest",
]


# ─── Analysis ───
a = Analysis(
    [ENTRY_POINT],
    pathex=[str(PROJECT_ROOT), str(BACKEND_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)


# ─── 平台差异化打包 ───
if sys.platform == "darwin":
    # macOS: 生成 .app bundle
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    coll = COLLECT(
        exe, a.binaries, a.datas,
        strip=False, upx=False, upx_exclude=[],
        name=APP_NAME,
    )
    app = BUNDLE(
        coll,
        name=f"{APP_NAME}.app",
        icon=ICON_MAC,
        bundle_identifier="com.xianyu.auto",
        info_plist={
            "CFBundleDisplayName": APP_NAME,
            "CFBundleName": APP_NAME,
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleVersion": "1.0.0",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "10.13.0",
            "NSHumanReadableCopyright": "© 2026 Xianyu Auto",
        },
    )
else:
    # Windows: 目录版
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=ICON_WIN,
    )
    coll = COLLECT(
        exe, a.binaries, a.datas,
        strip=False, upx=False, upx_exclude=[],
        name=APP_NAME,
    )
