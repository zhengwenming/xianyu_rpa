#!/bin/bash
# 安装脚本 - macOS/Linux（一键安装所有依赖）
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "  闲鱼自动化铺货系统 - 安装"
echo "=========================================="

# ─── 1. 检查 Python ───
echo ""
echo ">>> 检查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ 请先安装 Python 3.11+"
    exit 1
fi
echo "✅ Python: $($PYTHON --version)"

# ─── 2. 检查 Node.js（前端构建需要） ───
echo ""
echo ">>> 检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，前端无法构建"
    echo "   请从 https://nodejs.org 下载安装 Node.js 18+"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# ─── 3. 创建后端虚拟环境 ───
echo ""
echo ">>> 创建 Python 虚拟环境..."
cd "$PROJECT_DIR/backend"
if [ ! -d "venv" ]; then
    $PYTHON -m venv venv
fi
source venv/bin/activate

# ─── 4. 安装后端依赖 ───
echo ""
echo ">>> 安装后端依赖（含 pywebview + pyinstaller）..."
pip install --upgrade pip -q
pip install -r requirements.txt

# ─── 5. 安装 Playwright 浏览器 ───
echo ""
echo ">>> 安装 Playwright Chromium..."
playwright install chromium || echo "⚠️  Playwright 浏览器安装失败，可稍后手动执行 playwright install chromium"

# ─── 6. 安装前端依赖 ───
echo ""
echo ">>> 安装前端依赖..."
cd "$PROJECT_DIR/frontend"
npm install

# ─── 7. 构建前端到后端 static 目录 ───
echo ""
echo ">>> 构建前端..."
npm run build

# ─── 8. macOS 建议安装 create-dmg（用于打包 DMG） ───
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v create-dmg &> /dev/null; then
        echo ""
        echo "💡 提示：安装 create-dmg 可获得更漂亮的 DMG 打包（可选）"
        echo "   brew install create-dmg"
    fi
fi

echo ""
echo "=========================================="
echo "✅ 安装完成"
echo "=========================================="
echo ""
echo "启动开发模式:  ./scripts/start.sh"
echo "打包 macOS:   ./scripts/build_mac.sh"
echo "打包 Windows: 在 Windows 下执行 scripts\\build_win.bat"
