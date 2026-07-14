@echo off
REM 安装脚本 - Windows（一键安装所有依赖）
setlocal

set "PROJECT_DIR=%~dp0.."

echo ==========================================
echo   闲鱼自动化铺货系统 - 安装
echo ==========================================

REM ─── 1. 检查 Python ───
echo.
echo ^>^>^> 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 请先安装 Python 3.11+
    echo         下载地址: https://www.python.org
    exit /b 1
)
python --version

REM ─── 2. 检查 Node.js ───
echo.
echo ^>^>^> 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js 未安装
    echo         下载地址: https://nodejs.org
    exit /b 1
)
node --version

REM ─── 3. 创建虚拟环境 ───
echo.
echo ^>^>^> 创建 Python 虚拟环境...
cd /d "%PROJECT_DIR%\backend"
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat

REM ─── 4. 安装后端依赖 ───
echo.
echo ^>^>^> 安装后端依赖（含 pywebview + pyinstaller）...
python -m pip install --upgrade pip -q
pip install -r requirements.txt

REM ─── 5. 安装 Playwright 浏览器 ───
echo.
echo ^>^>^> 安装 Playwright Chromium...
playwright install chromium

REM ─── 6. 安装前端依赖 ───
echo.
echo ^>^>^> 安装前端依赖...
cd /d "%PROJECT_DIR%\frontend"
call npm install

REM ─── 7. 构建前端 ───
echo.
echo ^>^>^> 构建前端...
call npm run build

echo.
echo ==========================================
echo [OK] 安装完成
echo ==========================================
echo.
echo 启动开发模式: scripts\start.bat
echo 打包 Windows: scripts\build_win.bat

pause
