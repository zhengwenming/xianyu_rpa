#!/bin/bash
# macOS 打包脚本 - 生成 .app 和 .dmg
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="闲鱼自动化铺货系统"

echo "=========================================="
echo "  ${APP_NAME} - macOS 打包"
echo "=========================================="

# ─── 1. 检查环境 ───
cd "$PROJECT_DIR"

if [ ! -d "backend/venv" ]; then
    echo "❌ Python 虚拟环境不存在，请先执行 scripts/setup.sh"
    exit 1
fi

# 激活虚拟环境
source backend/venv/bin/activate

# ─── 2. 检查并安装依赖 ───
echo ""
echo ">>> 检查后端依赖..."
pip install -q -r backend/requirements.txt

# ─── 3. 构建前端 ───
echo ""
echo ">>> 构建前端..."
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build

# 验证前端产物
if [ ! -f "$PROJECT_DIR/backend/static/web/index.html" ]; then
    echo "❌ 前端构建失败：找不到 index.html"
    exit 1
fi
echo "✅ 前端构建完成"

# ─── 4. 清理旧的打包产物 ───
cd "$PROJECT_DIR"
echo ""
echo ">>> 清理旧的打包产物..."
rm -rf build/ dist/

# ─── 5. PyInstaller 打包 ───
echo ""
echo ">>> PyInstaller 打包中（可能需要几分钟）..."
pyinstaller build.spec --clean --noconfirm

if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ PyInstaller 打包失败"
    exit 1
fi
echo "✅ .app 打包完成: dist/${APP_NAME}.app"

# ─── 6. 打 DMG ───
echo ""
echo ">>> 生成 DMG..."
DMG_PATH="dist/${APP_NAME}-1.0.0.dmg"
rm -f "$DMG_PATH"

# 检查 create-dmg 工具
if command -v create-dmg &> /dev/null; then
    # 使用 create-dmg（更漂亮）
    create-dmg \
        --volname "${APP_NAME}" \
        --window-pos 200 120 \
        --window-size 800 400 \
        --icon-size 100 \
        --icon "${APP_NAME}.app" 200 190 \
        --hide-extension "${APP_NAME}.app" \
        --app-drop-link 600 185 \
        --no-internet-enable \
        "$DMG_PATH" \
        "dist/${APP_NAME}.app" || true
fi

# 如果 create-dmg 失败或不存在，用 hdiutil 兜底
if [ ! -f "$DMG_PATH" ]; then
    echo ">>> 使用 hdiutil 生成 DMG..."
    hdiutil create -volname "${APP_NAME}" \
        -srcfolder "dist/${APP_NAME}.app" \
        -ov -format UDZO \
        "$DMG_PATH"
fi

echo ""
echo "=========================================="
echo "✅ 打包完成"
echo "=========================================="
echo "App:  dist/${APP_NAME}.app"
echo "DMG:  ${DMG_PATH}"
echo ""
echo "使用: 双击 .app 即可运行"
echo "     或双击 .dmg 拖拽到 Applications 文件夹安装"
