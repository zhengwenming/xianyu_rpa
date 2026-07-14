#!/usr/bin/env python3
"""启动脚本 - 自动切换到虚拟环境"""
import os
import sys
from pathlib import Path


def ensure_venv():
    """确保运行在虚拟环境中，否则用venv的python重新执行"""
    project_dir = Path(__file__).parent.resolve()
    venv_dir = project_dir / "venv"

    # 选择正确的python可执行文件路径
    if os.name == "nt":  # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:  # macOS/Linux
        venv_python = venv_dir / "bin" / "python"

    if not venv_python.exists():
        print("❌ 未找到虚拟环境，请先运行：")
        print(f"   cd {project_dir}")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate  # macOS/Linux")
        print("   venv\\Scripts\\activate    # Windows")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    # 判断当前是否运行在venv内：sys.prefix 应该指向venv目录
    running_in_venv = str(Path(sys.prefix).resolve()) == str(venv_dir)

    if not running_in_venv:
        print(f"🔄 切换到虚拟环境: {venv_python}")
        # 用venv的python重新执行本脚本
        os.execv(str(venv_python), [str(venv_python), __file__] + sys.argv[1:])


ensure_venv()

# 到这里说明已经在venv里了
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   访问 http://localhost:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )