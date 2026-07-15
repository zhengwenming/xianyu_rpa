# 闲鱼自动化铺货系统（桌面版）

**桌面级应用**：单一进程整合前端 UI + 后端服务，双击即用。

闲鱼自动上架 + 大模型自动回复 + 自动发货 + 自动下架 全能桌面应用。

## 功能特性

- **多店铺管理**：多个闲鱼店铺独立管理，Cookie 隔离
- **1688 商品采集**：按关键词或 URL 采集商品信息
- **AI 内容生成**：OpenAI/Anthropic/DeepSeek/Ollama，自动生成标题、描述
- **自动上架**：浏览器自动化操作，模拟人工发布
- **自动回复**：WebSocket 直连闲鱼，多专家路由（议价/技术/物流/售后/客服）
- **自动发货**：虚拟商品（卡券/链接/文本）自动发货，实物 1688 代发
- **自动下架**：售罄/违规/手动/策略下架
- **三类日志**：上架日志、下架日志、任务策略日志，持久化可查询
- **全局策略配置**：加价、过滤、节奏控制、AI 增强等

## 技术架构

- **桌面框架**：PyWebView（内嵌 WebView 显示前端 UI）
- **后端**：Python FastAPI + SQLite + Playwright + WebSocket
- **前端**：Vue 3 + Element Plus + Pinia + Vite（构建后嵌入到后端）
- **打包**：PyInstaller（macOS `.app`/`.dmg`，Windows `.exe`）

一个 Python 进程同时运行：
1. 内置 FastAPI 后端（监听本地 `127.0.0.1:8765`）
2. PyWebView 窗口加载前端 UI（内嵌浏览器）
3. 前端通过 HTTP/WebSocket 调用本地后端

## 快速开始

### 开发模式（源码运行）

**首次安装：**
```bash
# macOS / Linux
./scripts/setup.sh

# Windows
.\scripts\setup.bat
```

**启动应用：**
```bash
# macOS / Linux
./scripts/start.sh

# Windows
.\scripts\start.bat
```

**或直接：**
```bash
python3 launcher.py
```

> 提示：如需单独安装 Python 依赖，可在项目根目录执行 `pip install -r requirements.txt`。

启动后自动弹出桌面窗口，无需浏览器。

### 打包为可分发的 App

#### macOS（生成 .app + .dmg）
```bash
./scripts/build_mac.sh
```
产物：
- `dist/闲鱼自动化铺货系统.app` — 双击运行
- `dist/闲鱼自动化铺货系统-1.0.0.dmg` — 分发用

#### Windows（生成 .exe + zip）
```bat
scripts\build_win.bat
```
产物：
- `dist\闲鱼自动化铺货系统\闲鱼自动化铺货系统.exe` — 主程序
- `dist\闲鱼自动化铺货系统-1.0.0-win.zip` — 压缩包

## 项目结构

```
xianyu_rpa/
├── launcher.py                # 桌面 App 启动入口（关键文件）
├── build.spec                 # PyInstaller 打包配置
├── requirements.txt           # 根级依赖入口（转引用 backend/requirements.txt）
├── pyproject.toml             # Python 项目元数据
├── docs/                      # 文档与开发资料
├── frontend/                  # Vue3 前端源码
│   └── src/
├── backend/                   # Python 后端
│   ├── app/                   # FastAPI 应用
│   ├── static/
│   │   ├── web/               # 前端构建产物（npm run build 生成）
│   │   └── goofish_js/        # 闲鱼签名 JS
│   └── requirements.txt       # 后端真实依赖清单
├── scripts/
│   ├── setup.sh / .bat        # 一键安装
│   ├── start.sh / .bat        # 一键启动
│   ├── build_mac.sh           # macOS 打包
│   └── build_win.bat          # Windows 打包
└── README.md
```

## 数据存储位置

打包后应用数据保存在系统用户目录：
- **macOS**: `~/Library/Application Support/XianyuAuto/`
- **Windows**: `%APPDATA%\XianyuAuto\`
- **开发模式**: `backend/data/`

包含 SQLite 数据库、Cookie、日志、截图等。

## 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.11+ |
| Node.js | 18+ |
| macOS | 10.13+ |
| Windows | 10+ |

## 注意事项

1. **首次运行会自动下载 Chromium 浏览器**（Playwright 需要），约 100MB
2. **闲鱼签名 JS**：需要放在 `backend/static/goofish_js/goofish_sign.js`，当前是占位实现
3. **打包体积**：完整打包后 macOS 约 300MB、Windows 约 250MB（含 Python 运行时和依赖）
4. **API Key** 加密存储在本地 SQLite 中
5. **建议先在小号测试**，避免触发风控
