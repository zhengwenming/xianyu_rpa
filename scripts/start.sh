#!/bin/bash
# 启动脚本 - macOS/Linux（开发模式，一键启动桌面 App）
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

echo "=========================================="
echo "  闲鱼自动化铺货系统 - 桌面版启动"
echo "=========================================="

# 检查前端是否已构建
if [ ! -f "backend/static/web/index.html" ]; then
    echo ">>> 首次运行，构建前端..."
    cd "$PROJECT_DIR/frontend"
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run build
    cd "$PROJECT_DIR"
fi

# 启动桌面 App（launcher.py 会自动激活 venv）
echo ">>> 启动桌面 App..."
python3 launcher.py
