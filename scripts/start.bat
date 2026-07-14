@echo off
REM 启动脚本 - Windows（开发模式，一键启动桌面 App）
setlocal

set "PROJECT_DIR=%~dp0.."
cd /d "%PROJECT_DIR%"

echo ==========================================
echo   闲鱼自动化铺货系统 - 桌面版启动
echo ==========================================

REM 检查前端是否已构建
if not exist "backend\static\web\index.html" (
    echo ^>^>^> 首次运行，构建前端...
    cd /d "%PROJECT_DIR%\frontend"
    if not exist "node_modules" (
        call npm install
    )
    call npm run build
    cd /d "%PROJECT_DIR%"
)

REM 启动桌面 App（app.py 会自动激活 venv）
echo ^>^>^> 启动桌面 App...
python app.py

pause
