@echo off
REM Windows 打包脚本 - 生成 exe
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."
set "APP_NAME=闲鱼自动化铺货系统"

echo ==========================================
echo   %APP_NAME% - Windows 打包
echo ==========================================

cd /d "%PROJECT_DIR%"

REM ─── 1. 检查虚拟环境 ───
if not exist "backend\venv\Scripts\activate.bat" (
    echo [ERROR] Python 虚拟环境不存在，请先执行 scripts\setup.bat
    exit /b 1
)

call backend\venv\Scripts\activate.bat

REM ─── 2. 安装依赖 ───
echo.
echo ^>^>^> 检查后端依赖...
pip install -q -r backend\requirements.txt
if errorlevel 1 (
    echo [ERROR] 后端依赖安装失败
    exit /b 1
)

REM ─── 3. 构建前端 ───
echo.
echo ^>^>^> 构建前端...
cd /d "%PROJECT_DIR%\frontend"
if not exist "node_modules" (
    call npm install
    if errorlevel 1 (
        echo [ERROR] 前端依赖安装失败
        exit /b 1
    )
)
call npm run build
if errorlevel 1 (
    echo [ERROR] 前端构建失败
    exit /b 1
)

if not exist "%PROJECT_DIR%\backend\static\web\index.html" (
    echo [ERROR] 前端构建失败：找不到 index.html
    exit /b 1
)
echo [OK] 前端构建完成

REM ─── 4. 清理旧的打包产物 ───
cd /d "%PROJECT_DIR%"
echo.
echo ^>^>^> 清理旧的打包产物...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM ─── 5. PyInstaller 打包 ───
echo.
echo ^>^>^> PyInstaller 打包中（可能需要几分钟）...
pyinstaller build.spec --clean --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller 打包失败
    exit /b 1
)

if not exist "dist\%APP_NAME%\%APP_NAME%.exe" (
    echo [ERROR] 找不到打包后的 exe
    exit /b 1
)
echo [OK] exe 打包完成: dist\%APP_NAME%\%APP_NAME%.exe

REM ─── 6. 打成 zip 便于分发 ───
echo.
echo ^>^>^> 生成 zip 分发包...
cd /d "%PROJECT_DIR%\dist"
powershell -Command "Compress-Archive -Path '%APP_NAME%' -DestinationPath '%APP_NAME%-1.0.0-win.zip' -Force"

echo.
echo ==========================================
echo [OK] 打包完成
echo ==========================================
echo 目录版: dist\%APP_NAME%\
echo 主程序: dist\%APP_NAME%\%APP_NAME%.exe
echo 压缩包: dist\%APP_NAME%-1.0.0-win.zip
echo.
echo 使用: 双击 exe 即可运行

pause
