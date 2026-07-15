# 闲鱼自动化铺货系统 — Claude Code 项目提示词

## 一、项目概述

构建一个**闲鱼自动上架 + 大模型自动回复 + 自动发货 + 自动下架**的桌面级应用。系统采用**双通道架构**与闲鱼交互：通过 **WebSocket 直连闲鱼服务器**实现消息实时收发和自动回复，通过 **Playwright 浏览器自动化**实现扫码登录、Cookie 管理、商品上架/下架表单操作。从 1688 采集商品信息，利用大模型生成上架所需的图片、视频和文本，自动完成闲鱼商品上架流程。自动回复采用多专家路由架构（议价/技术/物流/售后/客服），自动发货支持虚拟商品即时发货和实物 1688 代发。支持多店铺授权管理、任务暂停/继续/取消、三类日志（上架日志、下架日志、任务策略日志）持久化查询、全局策略配置（加价、过滤、节奏控制、AI 增强等），以及实时运行日志展示。

**目标平台：** macOS + Windows 双平台支持

---

## 二、技术栈

### 前端 UI
- **构建工具：** Vite 5.x
- **框架：** Vue 3.x（Composition API + `<script setup>`）
- **语言：** JavaScript（不使用 TypeScript）
- **UI 组件库：** Element Plus
- **状态管理：** Pinia
- **路由：** Vue Router 4
- **HTTP 客户端：** Axios
- **实时通信：** WebSocket（原生，用于日志实时推送）
- **图表（可选）：** ECharts（用于任务统计可视化）

### 后端服务
- **语言：** Python 3.11+
- **Web 框架：** FastAPI（原生支持 async + WebSocket）
- **ASGI 服务器：** Uvicorn
- **浏览器自动化：** Playwright（Python 版，支持 Chromium，跨平台）— 仅用于扫码登录、Cookie 获取/刷新、商品上架/下架表单操作
- **闲鱼消息通信：** websockets（Python WebSocket 客户端库）— 直连闲鱼 WebSocket 服务器，实时收发私信
- **闲鱼 HTTP API：** httpx（async）— 调用闲鱼 HTTP 接口（订单查询、商品详情、媒体上传等），需 sign 签名
- **签名算法执行：** Node.js 子进程 — 闲鱼 sign 签名核心算法为逆向 JS，通过 `subprocess` 调用 Node.js 执行
- **Protobuf 解码：** protobuf / blackboxprotobuf — 解析闲鱼 WebSocket 消息体
- **数据存储：** SQLite（via SQLAlchemy ORM）
- **任务管理：** asyncio + 自定义任务状态机
- **定时任务：** APScheduler — 订单轮询、Cookie 刷新、自动发货调度
- **日志：** Python logging + 自定义 WebSocket 日志处理器
- **配置管理：** Pydantic Settings

### 大模型集成
- **OpenAI SDK：** openai（Python）
- **Anthropic SDK：** anthropic（Python）
- **DeepSeek：** 使用 OpenAI SDK 配兼容端点
- **本地模型：** 使用 Ollama 或 OpenAI 兼容端点

---

## 三、项目目录结构

```
xianyu-auto/
├── frontend/                    # Vue3 前端
│   ├── src/
│   │   ├── api/                 # API 请求封装
│   │   │   ├── shop.js          # 店铺管理 API
│   │   │   ├── task.js          # 任务管理 API
│   │   │   ├── llm.js           # LLM 配置 API
│   │   │   ├── log.js           # 运行日志 API
│   │   │   ├── listingLog.js    # 上架日志 API
│   │   │   ├── delistingLog.js  # 下架日志 API
│   │   │   ├── taskLog.js       # 任务策略日志 API
│   │   │   ├── reply.js         # 自动回复 API
│   │   │   ├── delivery.js      # 自动发货 API
│   │   │   └── settings.js      # 全局设置 API
│   │   ├── components/          # 通用组件
│   │   │   ├── LogViewer.vue        # 实时运行日志组件
│   │   │   ├── TaskCard.vue         # 任务卡片
│   │   │   ├── ShopSelector.vue     # 店铺选择器
│   │   │   ├── ListingLogTable.vue  # 上架日志表格
│   │   │   ├── DelistingLogTable.vue # 下架日志表格
│   │   │   ├── TaskLogTable.vue     # 任务策略日志表格
│   │   │   └── StatCards.vue        # 汇总统计卡片
│   │   ├── views/               # 页面视图
│   │   │   ├── Dashboard.vue        # 仪表盘首页
│   │   │   ├── Shops.vue            # 店铺管理
│   │   │   ├── Tasks.vue            # 任务管理
│   │   │   ├── LLMConfig.vue        # 大模型配置
│   │   │   ├── ListingLogs.vue      # 上架日志页
│   │   │   ├── DelistingLogs.vue    # 下架日志页
│   │   │   ├── TaskLogs.vue         # 任务策略日志页
│   │   │   ├── AutoReply.vue        # 自动回复页（会话列表 + 对话窗口）
│   │   │   ├── ReplyRules.vue       # 回复规则与专家 Prompt 配置
│   │   │   ├── Delivery.vue         # 自动发货页（订单 + 配置 + 日志 + 卡池）
│   │   │   └── Settings.vue         # 全局设置
│   │   ├── stores/              # Pinia 状态
│   │   │   ├── shop.js
│   │   │   ├── task.js
│   │   │   ├── llm.js
│   │   │   ├── log.js
│   │   │   ├── listingLog.js
│   │   │   ├── delistingLog.js
│   │   │   ├── taskLog.js
│   │   │   ├── reply.js
│   │   │   ├── delivery.js
│   │   │   └── settings.js
│   │   ├── composables/         # 组合式函数
│   │   │   ├── useWebSocket.js  # WebSocket 连接管理
│   │   │   └── useTask.js       # 任务操作
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
│
├── backend/                     # Python 后端
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库初始化
│   │   ├── models/              # 数据模型
│   │   │   ├── shop.py          # 店铺模型
│   │   │   ├── task.py          # 任务模型
│   │   │   ├── log.py           # 运行日志模型
│   │   │   ├── listing_log.py   # 上架商品明细模型
│   │   │   ├── delisting_log.py # 下架商品明细模型
│   │   │   ├── task_log.py      # 任务策略日志模型
│   │   │   ├── llm_config.py    # LLM 配置模型
│   │   │   ├── delivery.py      # 发货配置与日志模型
│   │   │   ├── conversation.py  # 会话上下文模型
│   │   │   └── settings.py      # 全局设置模型
│   │   ├── routers/             # API 路由
│   │   │   ├── shop.py
│   │   │   ├── task.py
│   │   │   ├── llm.py
│   │   │   ├── log.py
│   │   │   ├── listing_log.py
│   │   │   ├── delisting_log.py
│   │   │   ├── task_log.py
│   │   │   ├── reply.py
│   │   │   ├── delivery.py
│   │   │   └── settings.py
│   │   ├── services/            # 业务逻辑
│   │   │   ├── browser/         # 浏览器自动化（仅用于登录/Cookie/上架/下架表单操作）
│   │   │   │   ├── manager.py   # 浏览器实例管理
│   │   │   │   ├── xianyu.py    # 闲鱼页面操作封装（上架/下架表单）
│   │   │   │   ├── alibaba.py   # 1688 采集封装
│   │   │   │   └── session.py   # 会话/Cookie 管理
│   │   │   ├── xianyu_ws/       # 闲鱼 WebSocket 通信服务（自动回复核心）
│   │   │   │   ├── client.py    # WebSocket 客户端（连接闲鱼服务器）
│   │   │   │   ├── protocol.py  # 协议封装（sign 签名 + Protobuf 编解码）
│   │   │   │   ├── sign.py      # 签名算法（调用 Node.js 执行逆向 JS）
│   │   │   │   ├── message.py   # 消息类型定义（文本/图片/音频/系统卡片）
│   │   │   │   ├── handler.py   # 消息路由处理器
│   │   │   │   └── connection_manager.py # 多店铺 WebSocket 连接管理
│   │   │   ├── reply/           # 自动回复引擎
│   │   │   │   ├── engine.py    # 回复引擎主逻辑
│   │   │   │   ├── context.py   # 会话上下文管理器
│   │   │   │   ├── experts.py   # 多专家路由（议价/技术/客服）
│   │   │   │   ├── classifier.py # 意图分类器（LLM 驱动）
│   │   │   │   └── prompts.py   # 各专家 Prompt 模板
│   │   │   ├── order/           # 订单与发货服务
│   │   │   │   ├── monitor.py   # 订单监控（HTTP API 轮询）
│   │   │   │   ├── shipper.py   # 自动发货执行器
│   │   │   │   ├── virtual_goods.py # 虚拟商品发货（卡券/网盘链接）
│   │   │   │   └── proxy_order.py   # 1688 代发（实物商品）
│   │   │   ├── llm/             # 大模型服务
│   │   │   │   ├── base.py      # 抽象基类
│   │   │   │   ├── openai_provider.py
│   │   │   │   ├── anthropic_provider.py
│   │   │   │   ├── deepseek_provider.py
│   │   │   │   ├── ollama_provider.py
│   │   │   │   └── factory.py   # 工厂模式
│   │   │   ├── task/            # 任务管理
│   │   │   │   ├── manager.py   # 任务管理器
│   │   │   │   ├── state.py     # 状态机
│   │   │   │   └── runner.py    # 任务执行器
│   │   │   ├── listing/         # 上架流程
│   │   │   │   ├── collector.py # 1688 商品采集
│   │   │   │   ├── generator.py # LLM 内容生成
│   │   │   │   ├── publisher.py # 闲鱼上架发布
│   │   │   │   └── delister.py  # 闲鱼自动下架
│   │   │   └── settings/        # 全局设置服务
│   │   │       └── manager.py   # 设置读取/应用/校验
│   │   └── utils/
│   │       ├── logger.py        # 日志工具（含 WebSocket 推送）
│   │       └── helpers.py       # 通用工具函数
│   ├── static/
│   │   └── goofish_js/          # 闲鱼签名逆向 JS 文件
│   │       └── goofish_sign.js  # sign 签名核心算法
│   ├── data/                    # 运行时数据
│   │   ├── xianyu_auto.db       # SQLite 数据库
│   │   └── sessions/            # 浏览器会话存储
│   │       └── {shop_id}/       # 按店铺隔离
│   ├── requirements.txt
│   └── run.py                   # 启动脚本
│
├── scripts/
│   ├── setup.sh                 # macOS/Linux 安装脚本
│   ├── setup.bat                # Windows 安装脚本
│   └── start.sh / start.bat     # 一键启动脚本
│
└── README.md
```

---

## 四、核心功能详细设计

### 4.1 多店铺管理

**数据模型：**
```python
class Shop:
    id: str                    # UUID
    name: str                  # 店铺名称（用户自定义，如"数码小店A"）
    status: str                # active / inactive
    login_status: str          # logged_in / logged_out / expired
    session_path: str          # 会话文件路径（持久化的 Cookie/LocalStorage）
    last_login_time: datetime  # 最近登录时间
    created_at: datetime
```

**功能要求：**
- 用户可添加多个闲鱼店铺，每个店铺独立管理
- 首次使用时，系统打开浏览器跳转闲鱼登录页，用户手动扫码/账密登录
- 登录成功后，自动持久化当前浏览器的 `storage_state`（Cookie + LocalStorage）到 `data/sessions/{shop_id}/` 目录
- 下次使用该店铺时，加载已保存的 `storage_state`，跳过登录步骤
- 如果检测到登录态过期（页面跳转到登录页或 API 返回 401），自动通知前端要求重新登录
- 店铺列表支持增、删、改（重命名）、查
- 删除店铺时同时清理对应的会话文件

### 4.2 浏览器自动化

**技术方案：** Playwright (Python)

**关键设计：**
- 使用 `persistent context`（持久化上下文）模式，每个店铺一个独立的 `user_data_dir`，天然隔离 Cookie 和缓存
- 浏览器实例按需启动，空闲超时后自动关闭以节省资源
- 所有页面操作加入随机延迟（1-3 秒），模拟人类行为，降低风控风险
- 支持无头模式（headless）和有头模式（headed）切换 — 有头模式用于调试和首次登录
- 操作失败时自动截图保存到 `data/sessions/{shop_id}/screenshots/`，便于排查

```python
# 浏览器管理器伪代码
class BrowserManager:
    async def get_context(self, shop_id: str, headless: bool = True):
        """获取或创建指定店铺的浏览器上下文"""
        user_data_dir = f"data/sessions/{shop_id}"
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            viewport={"width": 1920, "height": 1080},
            user_agent="...",  # 使用真实 UA
        )
        return context

    async def close_context(self, shop_id: str):
        """关闭指定店铺的浏览器"""
        ...

    async def check_login_status(self, shop_id: str) -> bool:
        """检测登录态是否有效"""
        ...
```

### 4.3 1688 商品采集

**功能要求：**
- 支持按关键词搜索 1688 商品
- 支持按 1688 商品 URL 直达采集
- 采集字段：
  - 商品标题
  - 商品主图（多张）
  - 商品详情图
  - 价格区间
  - 规格参数
  - 发货地
  - 供应商信息
- 采集结果存储到数据库，作为上架的素材源
- 采集过程需处理反爬：随机延迟、页面滚动模拟、必要时使用已登录的 1688 会话

### 4.4 大模型内容生成

**LLM 抽象层设计：**

```python
from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    """大模型提供商抽象基类"""

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        """对话接口"""
        ...

    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> bytes:
        """图片生成接口（如提供商不支持，抛出 NotImplementedError）"""
        ...

    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接是否正常"""
        ...


class LLMFactory:
    """大模型工厂"""

    @staticmethod
    def create(config: LLMConfig) -> LLMProvider:
        providers = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "deepseek": DeepSeekProvider,
            "ollama": OllamaProvider,       # 本地模型
            "custom": CustomProvider,       # 自定义 OpenAI 兼容端点
        }
        provider_class = providers.get(config.provider_type)
        if not provider_class:
            raise ValueError(f"不支持的提供商: {config.provider_type}")
        return provider_class(config)
```

**LLM 配置数据模型：**
```python
class LLMConfig:
    id: str
    name: str                    # 配置名称（如"我的GPT-4"）
    provider_type: str           # openai / anthropic / deepseek / ollama / custom
    api_key: str                 # API 密钥（加密存储）
    api_base: str                # API 端点（可自定义）
    model: str                   # 模型名称（如 gpt-4o, claude-3-5-sonnet, deepseek-chat）
    temperature: float           # 温度参数
    max_tokens: int              # 最大 token 数
    image_model: Optional[str]   # 图片生成模型（如 dall-e-3，可选）
    is_active: bool              # 是否当前激活
```

**生成内容：**
- **商品标题：** 基于 1688 采集的标题，生成适合闲鱼的吸引眼球标题（30 字以内）
- **商品描述：** 基于采集信息，生成符合闲鱼风格的商品描述文案（突出卖点、成色、发货等信息）
- **商品图片：**
  - 可选方案 A：直接使用 1688 采集的原图
  - 可选方案 B：用大模型对图片进行二次加工/美化（如生成产品场景图）
  - 可选方案 C：纯文字生成图片（DALL-E / 其他文生图模型）
  - 前端可配置选择哪种方案

**Prompt 模板设计：**
```python
LISTING_TITLE_PROMPT = """你是一个闲鱼商品文案专家。请根据以下商品信息，生成一个吸引人的闲鱼商品标题。

原始商品信息：
- 标题：{original_title}
- 价格：{price}
- 规格：{specs}

要求：
1. 标题不超过 30 个字
2. 突出核心卖点和性价比
3. 符合闲鱼平台的文案风格（口语化、有吸引力）
4. 不要使用违禁词或夸大宣传

请直接输出标题，不要加其他内容。"""

LISTING_DESC_PROMPT = """你是一个闲鱼商品文案专家。请根据以下信息，生成一段闲鱼商品描述。

商品信息：
- 标题：{title}
- 原始描述：{original_desc}
- 价格：{price}
- 规格：{specs}
- 发货地：{ship_from}

要求：
1. 描述分为几个部分：商品介绍、规格参数、发货说明、售后说明
2. 语气真诚、口语化，像个人卖家
3. 突出商品成色和性价比
4. 适当使用 emoji 增加亲和力
5. 总字数控制在 200-400 字

请直接输出商品描述。"""
```

### 4.5 闲鱼上架流程

**上架流程编排：**

```
1. 选择目标店铺 → 加载/验证会话
2. 从 1688 采集商品信息（按关键词或 URL）
3. 调用 LLM 生成闲鱼标题 + 描述
4. 处理图片（下载/生成/加工）
5. 打开闲鱼"发布商品"页面
6. 自动填写表单：
   - 填入标题
   - 上传图片（逐张上传，等待上传完成）
   - 填入描述
   - 选择分类
   - 设置价格
   - 设置发货地
   - 其他必填项
7. 点击发布
8. 验证发布是否成功（检测页面跳转或成功提示）
9. 记录上架结果，进入下一个商品
```

**关键细节：**
- 每个商品上架过程中，每个步骤都打日志（带时间戳）
- 上架失败时记录失败原因 + 截图，但不中断整体流程，继续下一个商品
- 支持「设置目标上架数量」：采集到足够数量的商品后停止采集，上架到目标数量后停止上架

### 4.6 任务状态机

**状态定义：**
```
                    ┌─────────┐
         create     │  PENDING  │
        ─────────▶  │ (等待中)  │
                    └─────┬─────┘
                          │ start
                          ▼
                    ┌─────────┐
                    │ RUNNING  │ ◄────── resume
                    │ (执行中)  │         │
                    └──┬───┬───┘         │
              pause    │   │ cancel      │
                  ┌────┘   └─────┐       │
                  ▼              ▼       │
            ┌─────────┐   ┌──────────┐   │
            │ PAUSED   │   │ CANCELLED │   │
            │ (已暂停)  │   │ (已取消)   │   │
            └─────┬───┘   └──────────┘   │
                  │              ✗ 终态，不可恢复
                  │ resume              │
                  └──────────────────────┘

            ┌─────────┐   ┌──────────┐
            │COMPLETED │   │  FAILED  │
            │ (已完成)  │   │ (失败)    │
            └─────────┘   └──────────┘
              ✗ 终态         ✗ 终态
```

**状态机实现：**
```python
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"        # 等待中
    RUNNING = "running"        # 执行中
    PAUSED = "paused"          # 已暂停（可恢复）
    CANCELLED = "cancelled"    # 已取消（终态，不可恢复）
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"          # 失败

# 合法状态转换
VALID_TRANSITIONS = {
    TaskStatus.PENDING: [TaskStatus.RUNNING, TaskStatus.CANCELLED],
    TaskStatus.RUNNING: [TaskStatus.PAUSED, TaskStatus.CANCELLED, TaskStatus.COMPLETED, TaskStatus.FAILED],
    TaskStatus.PAUSED:  [TaskStatus.RUNNING, TaskStatus.CANCELLED],  # 可恢复或取消
    TaskStatus.CANCELLED: [],   # 终态
    TaskStatus.COMPLETED: [],   # 终态
    TaskStatus.FAILED: [],      # 终态
}
```

**暂停/继续/取消实现要点：**
- **暂停：** 在上架循环的每个商品之间检查暂停标志。设置 `asyncio.Event`，暂停时 `clear()`，继续时 `set()`。任务执行循环在处理完当前商品后等待 Event。
- **继续：** 从数据库读取任务进度（已上架到第几个商品），从断点继续执行。
- **取消：** 设置取消标志，当前商品处理完后终止任务。已取消的任务在数据库中标记为 `cancelled`，前端不显示"继续"按钮，只能重新创建新任务。
- **任务进度持久化：** 每上架完一个商品，更新数据库中的 `current_count` 字段，确保即使程序重启也能从断点恢复。

```python
class TaskRunner:
    async def run(self, task: Task):
        """任务执行主循环"""
        await self._transition(task, TaskStatus.RUNNING)

        while task.current_count < task.target_count:
            # 检查取消
            if self._is_cancelled(task.id):
                await self._transition(task, TaskStatus.CANCELLED)
                return

            # 检查暂停（阻塞等待，不消耗 CPU）
            await self._pause_event.wait()
            if self._is_cancelled(task.id):
                await self._transition(task, TaskStatus.CANCELLED)
                return

            # 执行单个商品上架
            try:
                await self._publish_one_product(task)
                task.current_count += 1
                await self._save_progress(task)
            except Exception as e:
                await self._log(task.id, f"商品上架失败: {e}", level="error")
                # 失败不中断，继续下一个
                continue

        await self._transition(task, TaskStatus.COMPLETED)
```

### 4.7 实时日志系统

**架构设计：**
```
Python 业务逻辑
      │
      ▼
  Logger（标准 logging）
      │
      ├──▶ 写入 SQLite（持久化，支持历史查询）
      ├──▶ 写入文件（data/logs/{date}.log，按天滚动）
      └──▶ WebSocket 推送（实时到前端）
```

**日志数据模型：**
```python
class TaskLog:
    id: str
    task_id: str                # 关联任务
    shop_id: str                # 关联店铺
    timestamp: datetime         # 时间戳
    level: str                  # debug / info / warning / error
    message: str                # 日志内容
    extra: str                  # JSON 格式的附加信息（截图路径等）
```

**WebSocket 实现：**
```python
# FastAPI WebSocket 端点
@app.websocket("/ws/logs")
async def log_websocket(websocket: WebSocket):
    await websocket.accept()
    # 注册到此连接的客户端
    connection_id = str(uuid4())
    ws_manager.add(connection_id, websocket)
    try:
        while True:
            # 保持连接，可接收前端的消息（如订阅特定 task 的日志）
            data = await websocket.receive_text()
            # 处理订阅逻辑
    except WebSocketDisconnect:
        ws_manager.remove(connection_id)

# 自定义日志 Handler
class WebSocketLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "task_id": getattr(record, "task_id", None),
        }
        # 异步推送到所有连接的 WebSocket 客户端
        asyncio.create_task(ws_manager.broadcast(json.dumps(log_entry)))
```

**前端日志组件要求：**
- 日志按时间顺序展示，最新在底部，自动滚动到底部
- 不同级别日志用不同颜色区分：info 白色、warning 黄色、error 红色、debug 灰色
- 支持按级别过滤（复选框切换显示/隐藏）
- 支持按任务 ID 过滤
- 支持搜索关键字
- 支持暂停自动滚动（用户查看历史日志时不被新日志打断）
- 支持一键清空显示（不清空数据库）
- 支持导出当前日志为 txt 文件
- 单条日志最多显示 500 字，超出截断并显示"展开"

### 4.8 闲鱼消息协议层（WebSocket 通信基座）

> **核心原理参考：** [XianYuApis](https://github.com/cv-cat/XianYuApis) 项目逆向还原了闲鱼 WebSocket 私信协议。我们参考其原理，代码自行实现。

闲鱼官方未开放 IM 消息接口。要实现实时自动回复，需通过 WebSocket 直连闲鱼服务器。核心涉及三层技术：

**① Sign 签名算法**
闲鱼所有 API 请求（HTTP + WebSocket 握手）都需要 `sign` 签名参数。签名算法是逆向得到的 JS 代码，通过 Node.js 子进程执行：

```python
import subprocess
import json

class SignEngine:
    """闲鱼 sign 签名引擎 — 调用 Node.js 执行逆向 JS"""

    def __init__(self, js_path: str):
        self.js_path = js_path  # static/goofish_js/goofish_sign.js

    async def sign(self, params: dict, cookie: str) -> str:
        """
        生成 sign 签名
        :param params: 请求参数
        :param cookie: 当前店铺的 Cookie
        :return: sign 签名字符串
        """
        input_data = json.dumps({"params": params, "cookie": cookie})
        result = subprocess.run(
            ["node", self.js_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Sign JS 执行失败: {result.stderr}")
        return json.loads(result.stdout)["sign"]
```

**② WebSocket 连接与认证**
连接闲鱼 WebSocket 服务器，使用 Cookie + sign 进行认证握手：

```python
import websockets
import json

class XianyuWebSocketClient:
    """闲鱼 WebSocket 客户端"""

    WSS_URL = "wss://wss-goofish.dingtalk.com/lh/"  # 闲鱼 WebSocket 端点

    def __init__(self, shop_id: str, cookie: str, sign_engine: SignEngine):
        self.shop_id = shop_id
        self.cookie = cookie
        self.sign_engine = sign_engine
        self.ws: websockets.WebSocketClientProtocol = None
        self._running = False

    async def connect(self):
        """建立 WebSocket 连接"""
        # 生成认证 sign
        sign = await self.sign_engine.sign(
            {"ts": str(int(time.time() * 1000))},
            self.cookie
        )
        headers = {"Cookie": self.cookie}
        self.ws = await websockets.connect(
            self.WSS_URL,
            extra_headers=headers,
        )
        self._running = True
        # 发送注册消息
        await self._send_register(sign)

    async def listen(self, on_message_callback):
        """监听消息"""
        async for raw_data in self.ws:
            try:
                message = self._decode_message(raw_data)
                if message:
                    await on_message_callback(message)
            except Exception as e:
                logger.error(f"消息解码失败: {e}")

    async def send_message(self, cid: str, to_user_id: str, content: dict):
        """发送消息"""
        msg = self._encode_message(cid, to_user_id, content)
        await self.ws.send(msg)

    def _decode_message(self, raw_data: bytes) -> Optional[dict]:
        """解码 Protobuf 消息 → 解析为统一消息格式"""
        # 1. base64 解码
        # 2. Protobuf 反序列化
        # 3. 提取关键字段：sender_id, cid, message_type, content
        ...

    def _encode_message(self, cid: str, to_user_id: str, content: dict) -> bytes:
        """编码消息为 Protobuf + base64 格式"""
        ...

    async def heartbeat(self):
        """心跳保活"""
        while self._running:
            await asyncio.sleep(30)
            await self.ws.send(json.dumps({"type": "heartbeat"}))

    async def reconnect(self):
        """断线重连"""
        self._running = False
        await asyncio.sleep(5)
        await self.connect()
```

**③ 多店铺连接管理**
每个已授权店铺维护一个独立的 WebSocket 连接：

```python
class XianyuConnectionManager:
    """多店铺 WebSocket 连接管理器"""

    def __init__(self):
        self._connections: dict[str, XianyuWebSocketClient] = {}
        self._sign_engine = SignEngine("static/goofish_js/goofish_sign.js")

    async def start_shop(self, shop: Shop):
        """启动指定店铺的 WebSocket 连接"""
        cookie = await self._load_cookie(shop.id)
        client = XianyuWebSocketClient(shop.id, cookie, self._sign_engine)
        await client.connect()

        # 启动心跳
        asyncio.create_task(client.heartbeat())

        # 启动消息监听
        asyncio.create_task(
            client.listen(on_message_callback=self._dispatch_message)
        )
        self._connections[shop.id] = client

    async def stop_shop(self, shop_id: str):
        """停止指定店铺的连接"""
        if shop_id in self._connections:
            await self._connections[shop_id].close()
            del self._connections[shop_id]

    async def _dispatch_message(self, message: dict):
        """消息分发到回复引擎"""
        shop_id = message.get("shop_id")
        await self.reply_engine.handle(shop_id, message)
```

### 4.9 大模型自动回复引擎（多专家路由）

> **核心原理参考：** [XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent) 的多专家协同决策架构。我们参考其意图分类 + 专家路由 + 上下文管理的思路，代码自行实现。

**架构设计：**
```
闲鱼 WebSocket 消息
        │
        ▼
  消息预处理器（过滤系统卡片消息、提取商品 ID）
        │
        ▼
  会话上下文管理器（加载该用户的历史对话 + 关联商品信息）
        │
        ▼
  意图分类器（LLM 驱动，判断用户意图）
        │
        ├──▶ 议价专家（用户询问能否便宜、砍价）
        ├──▶ 技术专家（用户询问商品参数、功能、兼容性）
        ├──▶ 客服专家（物流、发货、售后问题）
        └──▶ 默认专家（通用闲聊、商品推荐）
        │
        ▼
  回复生成（LLM 生成回复文本）
        │
        ▼
  回复发送（通过 WebSocket 发送到闲鱼）
        │
        ▼
  上下文更新（保存本轮对话到会话历史）
```

**会话上下文管理器：**
```python
class ConversationContext:
    """单店铺单用户的会话上下文"""

    MAX_HISTORY = 20  # 最多保留最近 20 轮对话

    def __init__(self, shop_id: str, user_id: str):
        self.shop_id = shop_id
        self.user_id = user_id
        self.history: list[dict] = []       # [{"role": "user/assistant", "content": "..."}]
        self.product_id: Optional[str] = None  # 当前讨论的商品 ID
        self.product_info: Optional[dict] = None  # 商品信息缓存
        self.human_takeover: bool = False     # 人工接管模式


class ContextManager:
    """会话上下文管理器 — 管理所有店铺所有用户的会话"""

    def __init__(self):
        self._contexts: dict[str, ConversationContext] = {}  # key: f"{shop_id}:{user_id}"

    def get_or_create(self, shop_id: str, user_id: str) -> ConversationContext:
        key = f"{shop_id}:{user_id}"
        if key not in self._contexts:
            self._contexts[key] = ConversationContext(shop_id, user_id)
        return self._contexts[key]

    def add_message(self, shop_id: str, user_id: str, role: str, content: str):
        ctx = self.get_or_create(shop_id, user_id)
        ctx.history.append({"role": role, "content": content})
        # 超出上限时丢弃最早的
        if len(ctx.history) > ctx.MAX_HISTORY:
            ctx.history = ctx.history[-ctx.MAX_HISTORY:]
```

**意图分类器：**
```python
CLASSIFY_PROMPT = """你是一个闲鱼客服意图分类器。根据用户消息判断意图类型。

用户消息：{user_message}

商品信息：{product_info}

对话历史（最近3轮）：
{recent_history}

请只输出以下分类之一，不要输出其他内容：
- BARGAIN: 用户在讨价还价、询问能否便宜、要求降价
- TECHNICAL: 用户询问商品参数、功能、规格、兼容性、使用方法
- LOGISTICS: 用户询问发货、物流、快递、到货时间
- AFTER_SALE: 用户询问售后、退换货、质量问题
- GENERAL: 通用咨询、闲聊、其他

只输出分类标签，如：BARGAIN"""


class IntentClassifier:
    """LLM 驱动的意图分类器"""

    async def classify(self, context: ConversationContext, user_message: str) -> str:
        prompt = CLASSIFY_PROMPT.format(
            user_message=user_message,
            product_info=context.product_info or "无",
            recent_history=self._format_history(context.history[-6:]),
        )
        result = await self.llm.chat([
            {"role": "system", "content": "你是一个意图分类器，只输出分类标签。"},
            {"role": "user", "content": prompt},
        ], temperature=0.1, max_tokens=20)
        return result.strip().upper()
```

**多专家回复：**
```python
class ReplyEngine:
    """自动回复引擎"""

    EXPERTS = {
        "BARGAIN": "price_expert",      # 议价专家
        "TECHNICAL": "tech_expert",     # 技术专家
        "LOGISTICS": "logistics_expert", # 物流专家
        "AFTER_SALE": "service_expert",  # 售后专家
        "GENERAL": "default_expert",     # 默认客服
    }

    async def handle(self, shop_id: str, message: dict):
        """处理收到的消息"""
        user_id = message["sender_id"]
        user_message = message["content"]
        product_id = message.get("product_id")

        # 1. 获取/创建会话上下文
        ctx = self.context_manager.get_or_create(shop_id, user_id)

        # 2. 人工接管检查
        if ctx.human_takeover:
            return  # 人工接管模式下不自动回复

        # 3. 接管切换关键词检测（如输入句号切换人工接管）
        if user_message.strip() in self.takeover_keywords:
            ctx.human_takeover = not ctx.human_takeover
            status = "开启" if ctx.human_takeover else "关闭"
            await self._send(shop_id, user_id, f"已{status}人工接管模式")
            return

        # 4. 过滤系统卡片消息
        if message.get("type") == "system_card":
            return

        # 5. 加载商品信息（注入到上下文）
        if product_id and product_id != ctx.product_id:
            ctx.product_id = product_id
            ctx.product_info = await self._fetch_product_info(shop_id, product_id)

        # 6. 记录用户消息到上下文
        self.context_manager.add_message(shop_id, user_id, "user", user_message)

        # 7. 意图分类
        intent = await self.classifier.classify(ctx, user_message)

        # 8. 路由到对应专家生成回复
        expert_name = self.EXPERTS.get(intent, "default_expert")
        reply = await self._generate_reply(expert_name, ctx, user_message)

        # 9. 模拟人工回复延迟（可选）
        if self.settings.simulate_human_typing:
            delay = min(len(reply) * 0.1, 5)  # 按字数估算打字时间
            await asyncio.sleep(delay)

        # 10. 发送回复
        await self._send(shop_id, user_id, reply)

        # 11. 记录回复到上下文
        self.context_manager.add_message(shop_id, user_id, "assistant", reply)

        # 12. 记录日志
        await self._log_reply(shop_id, user_id, user_message, reply, intent)
```

**专家 Prompt 模板示例：**
```python
PRICE_EXPERT_PROMPT = """你是一个闲鱼二手商品议价专家。买家正在和你讨价还价。

商品信息：
- 标题：{title}
- 标价：{price}
- 成本价：{cost_price}（仅你知晓，不要透露）
- 最低可接受价：{min_price}（仅你知晓，不要透露）

对话历史：
{history}

买家最新消息：{user_message}

议价策略：
1. 初始报价坚守标价，强调商品价值
2. 买家坚持砍价时，可适当让步但不能低于最低可接受价
3. 用真诚的语气，像个人卖家
4. 可以用"包邮"、"送小礼物"等替代直接降价
5. 如果买家出价低于最低可接受价，委婉拒绝

请生成回复（50字以内，口语化）："""

TECH_EXPERT_PROMPT = """你是一个闲鱼商品技术解答专家。买家在询问商品的技术问题。

商品信息：
- 标题：{title}
- 描述：{description}
- 规格：{specs}

对话历史：
{history}

买家最新消息：{user_message}

要求：
1. 基于商品信息准确回答
2. 不确定的信息要诚实说明
3. 语气专业但通俗，像懂行的卖家
4. 50-150字

请生成回复："""

DEFAULT_PROMPT = """你是一个友好的闲鱼卖家客服。

商品信息：
- 标题：{title}
- 描述：{description}

对话历史：
{history}

买家最新消息：{user_message}

要求：
1. 热情、真诚、口语化
2. 推销商品卖点
3. 引导下单
4. 50字以内

请生成回复："""
```

**商品信息注入：**
当买家从商品详情页发起私信时，消息中会携带 `product_id`。系统通过闲鱼 HTTP API 获取商品详情（标题、描述、价格、图片），注入到 LLM 上下文中，让 AI 回复有商品感知能力。

**人工接管模式：**
- 用户输入预设关键词（默认为句号 `。`）切换人工/AI 接管
- 人工接管时不自动回复，所有消息留给卖家手动处理
- 前端可查看哪些会话处于人工接管状态

**回复规则降级：**
- LLM 不可用时（API 超时/余额不足），降级为关键词匹配回复
- 关键词规则前端可配置：关键词 → 回复内容（支持多条规则）
- 无匹配时使用默认回复模板

### 4.10 自动发货系统

> **核心原理参考：** [xianyu-auto-reply](https://github.com/zhinianboke/xianyu-auto-reply) 的 scheduler 服务设计。我们参考其定时任务调度 + 订单轮询 + 多类型发货的思路，代码自行实现。

**架构设计：**
```
APScheduler 定时任务（每 60 秒执行一次）
        │
        ▼
  订单轮询器（调用闲鱼 HTTP API 获取待发货订单）
        │
        ▼
  订单分类器（虚拟商品 / 实物代发）
        │
        ├──▶ 虚拟商品发货器（卡券/网盘链接/激活码 → 直接通过 API 发送）
        ├──▶ 实物代发发货器（1688 下单 → 获取物流单号 → 回填闲鱼）
        └──▶ 异常处理（发货失败 → 重试 → 记录日志）
```

**订单轮询器：**
```python
class OrderMonitor:
    """闲鱼订单监控器 — 通过 HTTP API 轮询待发货订单"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """启动定时任务"""
        self.scheduler.add_job(
            self._check_orders,
            "interval",
            seconds=60,
            id="order_check",
        )
        self.scheduler.start()

    async def _check_orders(self):
        """检查所有已授权店铺的待发货订单"""
        shops = await self._get_authorized_shops()
        for shop in shops:
            try:
                orders = await self._fetch_pending_orders(shop)
                for order in orders:
                    await self._process_order(shop, order)
            except Exception as e:
                logger.error(f"[{shop.name}] 订单检查失败: {e}")

    async def _fetch_pending_orders(self, shop: Shop) -> list[dict]:
        """调用闲鱼 HTTP API 获取待发货订单"""
        # 1. 获取 sign 签名
        sign = await self.sign_engine.sign(
            {"status": "pending", "page": 1},
            shop.cookie,
        )
        # 2. 调用闲鱼订单 API
        response = await httpx_client.post(
            XIANYU_ORDER_API,
            params={"sign": sign},
            cookies={"cookie": shop.cookie},
        )
        return self._parse_orders(response.json())
```

**虚拟商品发货器：**
```python
class VirtualGoodsShipper:
    """虚拟商品自动发货 — 卡券/网盘/激活码"""

    async def ship(self, shop: Shop, order: dict) -> bool:
        """执行虚拟商品发货"""
        product_id = order["product_id"]
        buyer_id = order["buyer_id"]

        # 1. 获取该商品绑定的发货内容
        delivery_content = await self._get_delivery_content(product_id)
        if not delivery_content:
            logger.warning(f"商品 {product_id} 未配置发货内容")
            return False

        # 2. 根据类型发货
        if delivery_content["type"] == "card":
            # 卡券：从卡池取出一张，标记已使用
            card = await self._pop_card(product_id)
            message = f"您的卡密：{card}\n请妥善保管，如有问题随时联系~"
        elif delivery_content["type"] == "link":
            # 网盘链接：直接发送预设链接
            message = f"资源链接：{delivery_content['link']}\n提取码：{delivery_content['code']}"
        elif delivery_content["type"] == "text":
            # 纯文本：发送预设内容
            message = delivery_content["content"]
        else:
            return False

        # 3. 通过 WebSocket 发送给买家
        await self.ws_manager.send_message(
            shop_id=shop.id,
            to_user_id=buyer_id,
            content={"type": "text", "text": message},
        )

        # 4. 调用闲鱼 API 确认发货
        await self._confirm_shipping(shop, order, "virtual")

        # 5. 记录发货日志
        await self._log_shipping(shop, order, "virtual", message)

        return True
```

**实物代发发货器（1688 代发）：**
```python
class ProxyOrderShipper:
    """实物商品 1688 代发"""

    async def ship(self, shop: Shop, order: dict) -> bool:
        """执行 1688 代发流程"""
        product_id = order["product_id"]

        # 1. 查找该商品对应的 1688 源商品
        source_url = await self._get_source_url(product_id)
        if not source_url:
            logger.error(f"商品 {product_id} 未关联 1688 源")
            return False

        # 2. 提取买家收货信息
        address = await self._get_shipping_address(shop, order)

        # 3. 通过浏览器自动化在 1688 下单
        async with self.browser_manager.get_context(shop.id) as ctx:
            page = await ctx.new_page()
            await page.goto(source_url)
            await self._fill_1688_order(page, address, order)
            await self._submit_1688_order(page)

        # 4. 等待 1688 发货，获取物流单号
        tracking_no = await self._wait_for_tracking(shop, order)

        if tracking_no:
            # 5. 回填物流单号到闲鱼
            await self._fill_xianyu_tracking(shop, order, tracking_no)
            await self._log_shipping(shop, order, "proxy", tracking_no)
            return True
        else:
            await self._log_shipping(shop, order, "proxy_failed", "未获取到物流单号")
            return False
```

**发货内容配置（前端可配置）：**
```python
class DeliveryConfig:
    id: str
    shop_id: str                    # 关联店铺
    product_id: str                 # 闲鱼商品 ID
    product_title: str              # 商品标题（冗余）
    delivery_type: str              # card / link / text / proxy
    # ─── 卡券类型 ───
    card_pool: str                  # 卡池（JSON 数组，每行一个卡密）
    # ─── 链接类型 ───
    link_url: str                   # 网盘链接
    link_code: str                  # 提取码
    # ─── 文本类型 ───
    text_content: str               # 纯文本发货内容
    # ─── 代发类型 ───
    source_url: str                 # 1688 源商品 URL
    # ─── 通用 ───
    auto_ship: bool                 # 是否自动发货（False=仅通知不自动发）
    created_at: datetime
```

**发货重试与异常处理：**
- 发货失败自动重试 3 次，间隔 5 分钟
- 重试仍失败：记录到日志，前端弹窗提醒人工处理
- 卡池耗尽：自动通知卖家补充库存

### 4.11 上架日志（已发布商品明细 + 汇总数据）

**功能定位：** 记录每一次上架操作的结果明细，提供按店铺查看、汇总统计、刷新和清空功能。与 4.7 的实时运行日志不同，上架日志聚焦于「商品维度」的记录——每个商品上架成功或失败都有一条独立记录，附带商品信息。

**数据模型：**
```python
class ListingLog:
    id: str                         # UUID
    shop_id: str                    # 关联店铺
    shop_name: str                  # 店铺名称（冗余存储，店铺改名后历史日志不受影响）
    task_id: str                    # 关联任务
    product_title: str              # 闲鱼上架标题
    source_url: str                 # 1688 商品来源 URL
    source_supplier: str            # 1688 供应商名称
    source_price: float             # 1688 采集价格
    listing_price: float            # 闲鱼上架价格（加价后）
    image_urls: str                 # 上传的图片 URL 列表（JSON 数组）
    status: str                     # success / failed
    fail_reason: Optional[str]      # 失败原因（status=failed 时填写）
    screenshot_path: Optional[str]  # 失败截图路径
    listed_at: datetime             # 上架时间
    created_at: datetime            # 记录创建时间
```

**汇总统计：**
- 每个店铺（或全局）的上架汇总数据：总尝试数、成功数、失败数、成功率
- 支持时间范围筛选：今日、近 7 天、近 30 天、自定义日期范围
- 汇总数据在页面顶部以统计卡片形式展示

**前端页面设计（ListingLogs.vue）：**
- 顶部：店铺切换下拉框（支持「全部店铺」选项）+ 时间范围选择器
- 统计卡片行：总尝试 | 成功数（绿色） | 失败数（红色） | 成功率（百分比）
- 工具栏：[刷新] [清空当前店铺日志] [导出 Excel]
- 数据表格列：
  | 上架时间 | 店铺 | 商品标题 | 来源供应商 | 采集价 | 上架价 | 状态 | 失败原因 | 操作 |
  - 状态列：绿色「成功」标签 / 红色「失败」标签
  - 操作列：[查看详情]（弹窗展示完整商品信息、图片预览、失败截图）
- 表格支持分页（每页 20/50/100 条可选）
- 日志持久化在 SQLite，下次启动程序仍然可查询

**清空逻辑：**
- 「清空」按钮仅清空当前选中店铺的上架日志（或全部店铺，需二次确认）
- 清空操作写入一条系统日志记录操作人和时间
- 清空后数据不可恢复，需弹窗二次确认

### 4.12 下架日志（自动下架商品明细）

**功能定位：** 系统自动下架商品时（如商品售罄、违规下架、手动触发批量下架等），记录下架明细。功能结构与上架日志一致。

**数据模型：**
```python
class DelistingLog:
    id: str                         # UUID
    shop_id: str                    # 关联店铺
    shop_name: str                  # 店铺名称（冗余存储）
    task_id: Optional[str]          # 关联任务（手动下架可为空）
    product_title: str              # 商品标题
    xianyu_item_id: str             # 闲鱼商品 ID
    delist_reason: str              # 下架原因：sold_out / violation / manual / expired / strategy
    delist_type: str                # auto / manual（自动触发 or 手动触发）
    screenshot_path: Optional[str]  # 下架时页面截图
    delisted_at: datetime           # 下架时间
    created_at: datetime            # 记录创建时间
```

**汇总统计：** 与上架日志一致——总下架数、按原因分类统计（售罄/违规/手动/过期/策略下架）

**前端页面设计（DelistingLogs.vue）：**
- 结构与上架日志页面一致：店铺切换 + 时间筛选 + 统计卡片 + 数据表格
- 统计卡片：总下架数 | 自动下架 | 手动下架 | 售罄下架
- 表格列：
  | 下架时间 | 店铺 | 商品标题 | 闲鱼商品ID | 下架原因 | 下架类型 | 操作 |
  - 下架原因列用不同颜色标签：售罄=灰色、违规=红色、手动=蓝色、过期=橙色、策略=紫色
  - 操作列：[查看详情]（弹窗展示截图和详情）
- 同样支持刷新、清空（二次确认）、导出

### 4.13 任务策略日志

**功能定位：** 以「任务」为维度，记录每个上架任务的完整执行策略和结果统计。区别于上架日志（商品维度）和运行日志（事件维度），任务策略日志关注的是任务级别的宏观数据。

**数据模型：**
```python
class TaskStrategyLog:
    id: str                         # UUID
    task_id: str                    # 关联任务 ID
    task_name: str                  # 任务名称
    shop_id: str                    # 关联店铺
    shop_name: str                  # 店铺名称
    product_category: str           # 商品类别（如"数码"、"服饰"、"家居"等）
    keywords: str                   # 采集关键词（JSON 数组）
    strategy_config: str            # 策略配置快照（JSON：加价比例、图片方案、LLM配置等）
    target_count: int               # 目标上架数量
    success_count: int              # 成功数量
    fail_count: int                 # 失败数量
    total_attempted: int            # 总尝试数（成功+失败）
    status: str                     # running / paused / completed / cancelled / failed / interrupted
    start_time: datetime            # 任务开始时间
    end_time: Optional[datetime]    # 任务结束时间
    duration_seconds: Optional[int] # 总耗时（秒）
    created_at: datetime            # 记录创建时间
    updated_at: datetime            # 最后更新时间
```

**status 字段说明：**
- `running`：任务正在执行中
- `paused`：任务已暂停
- `completed`：任务已正常完成（达到目标数量）
- `cancelled`：任务被用户取消
- `failed`：任务异常终止
- `interrupted`：任务因程序重启等原因被中断（重启后 running → interrupted）

**前端页面设计（TaskLogs.vue）：**
- 顶部：店铺切换 + 状态筛选 + 时间范围
- 统计卡片：总任务数 | 运行中 | 已完成 | 已中断/取消
- 数据表格列：
  | 任务名称 | 店铺 | 商品类别 | 目标数 | 成功 | 失败 | 状态 | 开始时间 | 耗时 | 操作 |
  - 成功/失败列用颜色区分（绿色/红色数字）
  - 状态列用彩色标签
  - 操作列：[查看详情]（弹窗展示策略配置快照、关联的上架日志列表、执行时间线）
- 支持按状态筛选：全部 / 运行中 / 已完成 / 已中断 / 已取消
- 支持刷新和导出

### 4.14 店铺管理（增强版）

**在原有 4.1 基础上增强以下能力：**

**授权与取消授权：**
```python
class Shop:
    id: str                         # UUID
    name: str                       # 店铺名称
    status: str                     # active / inactive
    login_status: str               # authorized / unauthorized / expired
    session_path: str               # 会话文件路径
    authorized_at: Optional[datetime]  # 授权时间
    last_active_time: Optional[datetime] # 最近活跃时间
    xianyu_user_id: Optional[str]   # 闲鱼用户 ID（授权后自动提取）
    xianyu_nickname: Optional[str]  # 闲鱼昵称（授权后自动提取）
    xianyu_avatar: Optional[str]    # 闲鱼头像 URL
    created_at: datetime
    updated_at: datetime
```

**授权流程：**
1. 用户添加店铺（仅填店铺名称）
2. 点击「授权登录」→ 系统打开浏览器（有头模式），跳转闲鱼登录页
3. 用户手动完成登录（扫码/账密）
4. 系统检测到登录成功后：
   - 自动提取闲鱼用户 ID、昵称、头像
   - 持久化 `storage_state` 到 `data/sessions/{shop_id}/`
   - 更新 `login_status` 为 `authorized`
   - 更新 `authorized_at` 时间戳
5. 店铺卡片显示授权状态：绿色「已授权」+ 昵称 + 头像

**取消授权：**
- 点击「取消授权」→ 弹窗二次确认
- 确认后：删除会话文件、清除 `storage_state`、`login_status` 置为 `unauthorized`
- 清除闲鱼用户信息（user_id / nickname / avatar）
- 店铺记录本身保留，可重新授权

**登录态检测与自动续期：**
- 每次任务启动前检测登录态：访问闲鱼个人主页，检查是否被重定向到登录页
- 登录态过期时：`login_status` → `expired`，前端弹窗提示重新授权
- 每次成功操作后自动刷新 `last_active_time`

**前端店铺管理页面（Shops.vue）增强：**
- 卡片信息：头像 + 昵称 + 店铺名称 + 授权状态徽章 + 授权时间 + 最近活跃时间
- 操作按钮：
  - 未授权：[授权登录]
  - 已授权：[进入任务] [取消授权] [重命名] [删除]
  - 已过期：[重新授权] [取消授权] [删除]
- 删除店铺时：如果该店铺有运行中的任务，提示先停止任务

### 4.15 全局设置

**功能定位：** 系统级配置中心，影响所有店铺和任务的默认行为。设置持久化在 SQLite，前端可视化配置。

**数据模型：**
```python
class GlobalSettings:
    id: int                         # 固定为 1（单例）
    # ─── 图片与视频设置 ───
    enable_ai_main_video: bool      # 开启 AI 主图视频（为每个商品生成短视频主图）
    enable_smart_crop_3_4: bool     # 开启智能裁剪主图 3:4（闲鱼推荐比例）
    enable_ai_short_title: bool     # 开启 AI 导购短标题（生成 8-12 字导购标题）
    # ─── 价格设置 ───
    price_markup_ratio: float       # 加价比例（如 1.3 表示加价 30%）
    price_markup_amount: float      # 加价金额（在比例加价基础上再叠加固定金额，如 5 元）
    # ─── 过滤与屏蔽 ───
    supplier_blacklist: str         # 供应商黑名单（JSON 数组，如 ["供应商A", "供应商B"]）
    keyword_blocklist: str          # 上货关键词屏蔽（JSON 数组，违规词过滤）
    # ─── 节奏控制 ───
    post_listing_delay: int         # 上货后延迟时间（秒，每个商品上架后的间隔）
    simulated_pause_interval: int   # 模拟上货暂停时间（分钟，连续上架 N 个后暂停休息）
    simulated_pause_count: int      # 每隔多少个商品触发一次暂停
    # ─── 目标控制 ───
    target_success_count: int       # 目标成功个数（默认值，创建任务时可覆盖）
    # ─── 元数据 ───
    updated_at: datetime            # 最后修改时间
```

**各设置项详细说明：**

**1. 开启 AI 主图视频（`enable_ai_main_video`）**
- 开启后：上架时调用 LLM/文生图/文生视频能力，为商品主图生成一段 5-10 秒的短视频
- 闲鱼支持主图视频，视频商品曝光率更高
- 实现方式：使用 LLM 生成视频脚本 → 调用文生视频 API（或图片转视频）→ 上传到闲鱼
- 关闭时：仅上传静态图片

**2. 开启智能裁剪主图 3:4（`enable_smart_crop_3_4`）**
- 开启后：所有采集到的商品主图自动裁剪为 3:4 比例（闲鱼主图推荐比例）
- 裁剪策略：智能识别商品主体，居中裁剪，不裁掉关键内容
- 使用 PIL/Pillow 的 `Image.resize` + 智能裁剪算法（或简单中心裁剪 + 填充）
- 关闭时：保持原图比例上传

**3. AI 导购短标题（`enable_ai_short_title`）**
- 开启后：LLM 额外生成一个 8-12 字的导购短标题
- 闲鱼搜索流量部分来自短标题匹配
- 短标题填入闲鱼发布表单的「短标题」字段

**4. 加价比例（`price_markup_ratio`）**
- 闲鱼上架价格 = 1688 采集价格 × 加价比例 + 加价金额
- 示例：1688 价格 10 元，加价比例 1.3，加价金额 5 → 闲鱼价格 = 10 × 1.3 + 5 = 18 元
- 范围限制：1.0 - 5.0

**5. 加价金额（`price_markup_amount`）**
- 在加价比例基础上叠加的固定金额
- 范围限制：0 - 500

**6. 供应商黑名单（`supplier_blacklist`）**
- JSON 数组格式存储：`["某劣质供应商", "某高风险店铺"]`
- 采集 1688 商品时，如果供应商名称在黑名单中，自动跳过该商品
- 前端提供标签输入组件（Tag Input），支持添加/删除/批量导入

**7. 上货关键词屏蔽（`keyword_blocklist`）**
- JSON 数组格式存储：`["高仿", "A货", "1:1", "原单"]`
- 在生成闲鱼标题和描述前，检查 1688 原始标题和描述是否包含屏蔽词
- 如果包含：跳过该商品（记录到上架日志，fail_reason = "命中关键词屏蔽"）
- 同时在 LLM 生成内容后，再次检查生成结果是否包含违规词，如有则替换或重新生成

**8. 上货后延迟时间（`post_listing_delay`）**
- 每个商品上架成功后，等待 N 秒再开始下一个
- 在等待时间基础上叠加 1-3 秒随机抖动
- 范围：5 - 120 秒

**9. 模拟上货暂停时间（`simulated_pause_interval` + `simulated_pause_count`）**
- 每连续上架 `simulated_pause_count` 个商品后，暂停休息 `simulated_pause_interval` 分钟
- 模拟真人卖家的上架节奏，降低风控触发概率
- 暂停期间任务状态显示为 `running`（不改为 paused），日志中记录「模拟休息中...」
- 范围：暂停时间 5-60 分钟，触发数量 5-50 个

**10. 目标成功个数（`target_success_count`）**
- 全局默认值：创建任务时自动填充此值，但可在任务创建弹窗中单独修改
- 任务执行到成功数达到此值时自动标记为 `completed`

**前端全局设置页面（Settings.vue）：**
- 使用折叠面板（Collapse）或分区卡片组织：
  - 📐 图片与视频设置区
  - 💰 价格设置区
  - 🚫 过滤与屏蔽区
  - ⏱️ 节奏控制区
  - 🎯 目标控制区
- 每个设置项：标签 + 输入控件 + 说明文字（灰色小字解释作用）
- 开关类设置用 Switch 组件
- 数值类设置用 InputNumber 组件（带 min/max 限制）
- 黑名单/关键词用 Tag Input 组件（Element Plus 的 Dynamic Tags）
- 底部：[保存设置] [恢复默认] 按钮
- 保存后立即生效（下次任务创建/执行时读取最新配置）

**设置在业务流程中的应用点：**
```python
# 上架流程中读取全局设置
class ListingPipeline:
    async def run(self, product: Product, shop: Shop, task: Task):
        settings = await self.settings_manager.get()

        # 1. 供应商黑名单检查
        if product.supplier in json.loads(settings.supplier_blacklist):
            await self.log_skip(product, "供应商在黑名单中")
            return SkipResult()

        # 2. 关键词屏蔽检查
        if self._contains_blocked_words(product, settings.keyword_blocklist):
            await self.log_skip(product, "命中关键词屏蔽")
            return SkipResult()

        # 3. 价格计算
        listing_price = product.price * settings.price_markup_ratio + settings.price_markup_amount

        # 4. 图片处理
        images = product.images
        if settings.enable_smart_crop_3_4:
            images = [self._crop_to_3_4(img) for img in images]

        # 5. LLM 内容生成
        title = await self.llm.generate_title(product)
        desc = await self.llm.generate_desc(product)
        short_title = None
        if settings.enable_ai_short_title:
            short_title = await self.llm.generate_short_title(product)

        # 6. AI 主图视频
        main_video = None
        if settings.enable_ai_main_video:
            main_video = await self.llm.generate_video(product, images[0])

        # 7. 发布到闲鱼
        result = await self.publisher.publish(shop, title, desc, images, listing_price, short_title, main_video)

        # 8. 上架后延迟
        delay = settings.post_listing_delay + random.randint(1, 3)
        await asyncio.sleep(delay)

        return result
```

---

## 五、API 接口设计

### 5.1 店铺管理
```
GET    /api/shops                    # 获取店铺列表
POST   /api/shops                    # 添加店铺
PUT    /api/shops/{id}               # 更新店铺信息
DELETE /api/shops/{id}               # 删除店铺
POST   /api/shops/{id}/login         # 打开浏览器进行登录
GET    /api/shops/{id}/login-status  # 检查登录状态
DELETE /api/shops/{id}/session       # 清除会话（退出登录）
POST   /api/shops/{id}/authorize     # 授权登录（打开浏览器）
POST   /api/shops/{id}/revoke        # 取消授权（删除会话+清除用户信息）
```

### 5.2 任务管理
```
GET    /api/tasks                    # 获取任务列表（支持分页、筛选）
POST   /api/tasks                    # 创建上架任务
GET    /api/tasks/{id}               # 获取任务详情
POST   /api/tasks/{id}/start         # 启动任务
POST   /api/tasks/{id}/pause         # 暂停任务
POST   /api/tasks/{id}/resume        # 恢复任务（仅暂停状态可恢复）
POST   /api/tasks/{id}/cancel        # 取消任务（不可恢复）
DELETE /api/tasks/{id}               # 删除任务记录
GET    /api/tasks/{id}/progress      # 获取任务进度
```

### 5.3 LLM 配置
```
GET    /api/llm/configs              # 获取所有 LLM 配置
POST   /api/llm/configs              # 添加 LLM 配置
PUT    /api/llm/configs/{id}         # 更新 LLM 配置
DELETE /api/llm/configs/{id}         # 删除 LLM 配置
POST   /api/llm/configs/{id}/test    # 测试 LLM 连接
POST   /api/llm/configs/{id}/activate # 设为当前使用的 LLM
POST   /api/llm/generate             # 手动触发生成（测试用）
```

### 5.4 日志
```
GET    /api/logs                     # 查询运行日志（支持筛选：task_id, level, 时间范围）
GET    /api/logs/export              # 导出日志文件
WS     /ws/logs                      # WebSocket 实时日志推送
```

### 5.5 上架日志
```
GET    /api/listing-logs             # 查询上架日志（支持筛选：shop_id, status, 时间范围, 分页）
GET    /api/listing-logs/summary     # 上架汇总统计（支持 shop_id + 时间范围筛选）
GET    /api/listing-logs/{id}        # 上架日志详情
DELETE /api/listing-logs             # 清空上架日志（支持按 shop_id 清空，需二次确认参数 confirm=true）
GET    /api/listing-logs/export      # 导出上架日志（Excel/CSV）
```

### 5.6 下架日志
```
GET    /api/delisting-logs           # 查询下架日志（支持筛选：shop_id, reason, 时间范围, 分页）
GET    /api/delisting-logs/summary   # 下架汇总统计
GET    /api/delisting-logs/{id}      # 下架日志详情
DELETE /api/delisting-logs           # 清空下架日志（支持按 shop_id 清空）
GET    /api/delisting-logs/export    # 导出下架日志
```

### 5.7 任务策略日志
```
GET    /api/task-logs                # 查询任务策略日志（支持筛选：shop_id, status, 时间范围, 分页）
GET    /api/task-logs/summary        # 任务汇总统计
GET    /api/task-logs/{id}           # 任务策略日志详情（含策略配置快照）
GET    /api/task-logs/{id}/listings  # 该任务关联的上架明细列表
DELETE /api/task-logs                # 清空任务策略日志
GET    /api/task-logs/export         # 导出任务策略日志
```

### 5.8 全局设置
```
GET    /api/settings                 # 获取全局设置
PUT    /api/settings                 # 更新全局设置
POST   /api/settings/reset           # 恢复默认设置
GET    /api/settings/blacklist/suppliers   # 获取供应商黑名单列表
POST   /api/settings/blacklist/suppliers   # 添加供应商到黑名单
DELETE /api/settings/blacklist/suppliers   # 从黑名单移除供应商
GET    /api/settings/blacklist/keywords    # 获取关键词屏蔽列表
POST   /api/settings/blacklist/keywords    # 添加屏蔽关键词
DELETE /api/settings/blacklist/keywords    # 移除屏蔽关键词
```

### 5.9 自动回复
```
GET    /api/reply/status                          # 获取各店铺自动回复状态（在线/离线）
POST   /api/reply/{shop_id}/start                 # 启动店铺自动回复（建立 WebSocket 连接）
POST   /api/reply/{shop_id}/stop                  # 停止店铺自动回复（断开 WebSocket）
GET    /api/reply/{shop_id}/conversations          # 获取会话列表
GET    /api/reply/{shop_id}/conversations/{uid}    # 获取指定用户的对话历史
POST   /api/reply/{shop_id}/conversations/{uid}/takeover  # 切换人工接管
POST   /api/reply/{shop_id}/send                   # 手动发送消息给买家
GET    /api/reply/rules                            # 获取关键词回复规则
POST   /api/reply/rules                            # 添加关键词回复规则
PUT    /api/reply/rules/{id}                       # 更新规则
DELETE /api/reply/rules/{id}                       # 删除规则
GET    /api/reply/experts/prompts                  # 获取各专家 Prompt 模板
PUT    /api/reply/experts/prompts                  # 更新专家 Prompt 模板
WS     /ws/reply/{shop_id}                         # WebSocket 实时推送收到的消息和回复内容
```

### 5.10 自动发货
```
GET    /api/delivery/configs                       # 获取发货配置列表
POST   /api/delivery/configs                       # 添加发货配置
PUT    /api/delivery/configs/{id}                  # 更新发货配置
DELETE /api/delivery/configs/{id}                  # 删除发货配置
GET    /api/delivery/configs/{product_id}          # 获取指定商品的发货配置
GET    /api/delivery/orders                        # 获取待发货订单列表
GET    /api/delivery/orders/{id}                   # 订单详情
POST   /api/delivery/orders/{id}/ship              # 手动触发发货
POST   /api/delivery/orders/{id}/retry             # 重试发货
GET    /api/delivery/logs                          # 发货日志列表
GET    /api/delivery/logs/summary                  # 发货汇总统计
GET    /api/delivery/cards/{product_id}            # 查看商品卡池库存
POST   /api/delivery/cards/{product_id}            # 补充卡池（批量导入）
```

### 5.11 系统
```
GET    /api/system/status            # 系统状态（运行中的任务数、浏览器实例数等）
POST   /api/system/browser/check     # 检查 Playwright 浏览器是否安装
POST   /api/system/browser/install   # 安装 Playwright 浏览器
```

---

## 六、UI 设计要求

### 6.1 整体风格
- **设计语言：** 简约现代风，类似 Linear / Vercel Dashboard 的设计感
- **主色调：** 深色主题为主（`#1a1a2e` 背景），配合品牌色点缀
- **布局：** 左侧导航栏 + 右侧主内容区，响应式
- **字体：** 系统默认无衬线字体，中文用 "PingFang SC" / "Microsoft YaHei"
- **间距：** 充足留白，卡片间距 16-24px，内边距 20-24px
- **圆角：** 卡片 8-12px 圆角，按钮 6-8px 圆角
- **阴影：** 轻微阴影，不过度使用
- **动画：** 微交互动画（hover、状态切换），transition 200-300ms

### 6.2 页面设计

#### 仪表盘（Dashboard）
- 顶部统计卡片：今日上架数、累计上架数、运行中任务数、待处理消息数
- 中部：任务进度概览（进行中的任务卡片，显示进度条）
- 底部：最近活动日志摘要

#### 店铺管理（Shops）
- 卡片式展示每个店铺：闲鱼头像 + 昵称 + 店铺名称 + 授权状态徽章 + 授权时间 + 最近活跃时间
- 授权状态徽章：绿色「已授权」/ 灰色「未授权」/ 橙色「已过期」
- 每张卡片操作按钮（根据状态动态显示）：
  - 未授权 → [授权登录]
  - 已授权 → [进入任务] [取消授权] [重命名] [删除]
  - 已过期 → [重新授权] [取消授权] [删除]
- 添加店铺按钮（醒目的虚线框卡片）
- 删除有运行中任务的店铺时弹窗提示先停止任务

#### 任务管理（Tasks）
- 任务列表表格或卡片视图（可切换）
- 每个任务显示：名称、关联店铺、进度条（current/target）、状态标签、创建时间
- 操作按钮根据状态动态显示：
  - pending → [启动] [取消] [删除]
  - running → [暂停] [取消]
  - paused → [继续] [取消]
  - cancelled → [删除]
  - completed → [删除] [重新创建]
  - failed → [删除] [重试]
- 创建任务弹窗：选择店铺、输入 1688 采集关键词/URL、设置目标数量、选择 LLM 配置、选择图片处理方案
- 目标数量默认填充全局设置中的 `target_success_count`，可手动修改

#### LLM 配置（LLMConfig）
- 配置列表：每条配置显示名称、提供商类型（带 logo 图标）、模型名、激活状态
- 添加/编辑表单：
  - 提供商选择（下拉：OpenAI / Anthropic / DeepSeek / Ollama / 自定义）
  - 选择提供商后自动填充默认 API Base
  - API Key 输入框（密码模式，可切换显示）
  - 模型名称（下拉选择或手动输入）
  - 高级参数：temperature、max_tokens
  - 图片生成模型（可选）
  - 「测试连接」按钮
- 同时只能有一个配置处于激活状态

#### 上架日志（ListingLogs）
- 顶部筛选栏：店铺下拉选择（支持「全部店铺」）+ 时间范围选择器（今日/近7天/近30天/自定义）
- 统计卡片行：总尝试 | 成功数（绿色） | 失败数（红色） | 成功率（百分比）
- 工具栏：[刷新] [清空当前店铺日志（二次确认）] [导出 Excel]
- 数据表格：上架时间 | 店铺 | 商品标题 | 来源供应商 | 采集价 | 上架价 | 状态（彩色标签） | 失败原因 | 操作
- 操作列：[查看详情]（弹窗展示完整商品信息、图片预览、失败截图）
- 分页：每页 20/50/100 条可选
- 空状态：「暂无上架记录，去创建一个上架任务吧」

#### 下架日志（DelistingLogs）
- 结构与上架日志一致
- 统计卡片行：总下架数 | 自动下架 | 手动下架 | 售罄下架
- 数据表格：下架时间 | 店铺 | 商品标题 | 闲鱼商品ID | 下架原因（彩色标签） | 下架类型 | 操作
- 下架原因标签颜色：售罄=灰色、违规=红色、手动=蓝色、过期=橙色、策略=紫色

#### 任务策略日志（TaskLogs）
- 顶部筛选栏：店铺下拉 + 状态筛选（全部/运行中/已完成/已中断/已取消）+ 时间范围
- 统计卡片行：总任务数 | 运行中 | 已完成 | 已中断/取消
- 数据表格：任务名称 | 店铺 | 商品类别 | 目标数 | 成功（绿色） | 失败（红色） | 状态（彩色标签） | 开始时间 | 耗时 | 操作
- 操作列：[查看详情]（弹窗展示策略配置快照 + 关联上架日志列表 + 执行时间线）

#### 全局设置（Settings）
- 使用折叠面板分 5 个区域：
  - 📐 图片与视频设置：AI主图视频(Switch) | 智能裁剪3:4(Switch) | AI导购短标题(Switch)
  - 💰 价格设置：加价比例(InputNumber, 1.0-5.0, step 0.1) | 加价金额(InputNumber, 0-500, step 1)
  - 🚫 过滤与屏蔽：供应商黑名单(Tag Input) | 关键词屏蔽(Tag Input)
  - ⏱️ 节奏控制：上货后延迟秒数(InputNumber, 5-120) | 暂停触发数量(InputNumber, 5-50) | 暂停休息分钟(InputNumber, 5-60)
  - 🎯 目标控制：目标成功个数(InputNumber, 1-500)
- 每个设置项下方有灰色说明文字
- 底部：[保存设置] [恢复默认] 按钮

#### 实时运行日志（Logs — 底部抽屉）
- 可在任何页面通过底部抽屉展开
- 日志流式展示，带时间戳和级别颜色
- 顶部工具栏：级别过滤、搜索框、暂停滚动、清空、导出
- 日志量大时虚拟滚动（使用 vue-virtual-scroller）

#### 自动回复（AutoReply）
- 左右分栏布局：左侧会话列表 + 右侧对话窗口
- 会话列表：买家头像 + 昵称 + 最后一条消息 + 时间 + 接管状态标签
- 对话窗口：聊天气泡展示（买家左侧白色 / AI回复右侧品牌色），支持图片消息预览
- 顶部工具栏：[切换人工接管] [手动发送消息]
- 底部：消息输入框 + [发送] 按钮
- 右侧抽屉：会话设置（关联商品信息、当前专家、接管状态）
- 页面顶部：各店铺 WebSocket 连接状态指示灯（绿色=已连接/红色=已断开）+ [启动] [停止] 按钮
- 子页面：关键词回复规则管理（表格 + 添加/编辑弹窗）
- 子页面：专家 Prompt 模板编辑（代码编辑器风格，5 个 Tab 切换不同专家）

#### 自动发货（Delivery）
- 顶部：发货统计卡片（今日发货数 / 待发货数 / 发货失败数 / 卡池告警数）
- Tab 切换：[待发货订单] [发货配置] [发货日志] [卡池管理]
- 待发货订单 Tab：订单表格（订单号 | 商品 | 买家 | 金额 | 类型 | 状态 | 操作[手动发货][重试]）
- 发货配置 Tab：配置列表（商品 | 发货类型 | 发货内容摘要 | 自动发货开关 | 操作）
  - 添加配置弹窗：选择商品 → 选择发货类型（卡券/链接/文本/代发）→ 填写对应内容
- 发货日志 Tab：与上架日志结构类似，发货时间 | 商品 | 买家 | 类型 | 物流单号 | 状态 | 操作
- 卡池管理 Tab：选择商品 → 查看剩余卡密数量 → 批量导入（文本框粘贴，每行一个）
- 顶部工具栏：级别过滤、搜索框、暂停滚动、清空、导出
- 日志量大时虚拟滚动（使用 vue-virtual-scroller）

### 6.3 组件细节
- 状态标签：圆点 + 文字，颜色对应（蓝=running、黄=paused、灰=pending、红=cancelled/error、绿=completed）
- 进度条：带百分比和数字（如 `15/50`）
- 弹窗：居中模态框，遮罩层半透明
- 表单：行内验证，错误提示红色文字
- 按钮：主要操作用品牌色实心按钮，次要操作用描边按钮，危险操作用红色
- 空状态：插画 + 引导文字 + 行动按钮

---

## 七、跨平台兼容

### 7.1 路径处理
- 所有文件路径使用 `pathlib.Path`，不硬编码分隔符
- 浏览器 user_data_dir、数据库路径、日志路径都基于系统用户目录动态拼接
- 前端不拼接文件路径，所有路径由后端返回

### 7.2 启动脚本
- **macOS/Linux（start.sh）：** 激活 Python venv → 启动 uvicorn → 启动 vite dev server
- **Windows（start.bat）：** 同上逻辑，使用 Windows 语法
- 安装脚本自动检测 Python/Node.js 版本，安装依赖，执行 `playwright install chromium`

### 7.3 浏览器路径
- Playwright 在两个平台上都能自动管理 Chromium 安装
- 不依赖系统浏览器，避免版本差异

---

## 八、数据安全

- API Key 在数据库中加密存储（使用 Fernet 对称加密，密钥基于机器特征生成）
- 会话文件（Cookie）存储在用户目录下，不随项目分发
- 日志中不记录 API Key 等敏感信息（自动脱敏）
- `.env` 文件管理加密密钥，不提交到 Git

---

## 九、实现步骤（按顺序执行）

### Phase 1：项目初始化
1. 创建项目目录结构（按第三节的目录结构）
2. 初始化前端：`npm create vite@latest frontend -- --template vue`，安装 Element Plus、Pinia、Vue Router、Axios
3. 初始化后端：创建 `requirements.txt`，安装 FastAPI、Uvicorn、Playwright、SQLAlchemy、httpx、openai、anthropic
4. 配置 Vite 代理：将 `/api` 和 `/ws` 代理到后端 `localhost:8000`
5. 配置前端基础布局：左侧导航 + 右侧内容区，路由配置

### Phase 2：后端基础设施
6. 实现 FastAPI 应用入口、CORS 配置
7. 实现数据库初始化（SQLAlchemy + SQLite），创建所有数据模型表
8. 实现配置管理（Pydantic Settings）
9. 实现日志系统：标准 logging + 文件 Handler + WebSocket Handler + 数据库 Handler
10. 实现 WebSocket 管理器（连接管理 + 广播）

### Phase 3：店铺管理
11. 实现店铺 CRUD API
12. 实现 BrowserManager（Playwright 持久化上下文管理）
13. 实现会话管理（storage_state 持久化/加载）
14. 实现登录检测逻辑
15. 实现前端店铺管理页面

### Phase 4：LLM 集成
16. 实现 LLMProvider 抽象基类
17. 实现 OpenAI / Anthropic / DeepSeek / Ollama 四个 Provider
18. 实现 LLMFactory 工厂
19. 实现 LLM 配置 CRUD API + 连接测试 API
20. 实现内容生成服务（标题、描述、图片）
21. 实现前端 LLM 配置页面

### Phase 5：1688 采集
22. 实现 1688 搜索/商品页采集逻辑
23. 实现采集结果数据模型和存储
24. 实现采集 API
25. 采集结果列表前端展示

### Phase 6：任务系统
26. 实现任务数据模型
27. 实现任务状态机
28. 实现 TaskRunner（含暂停/继续/取消逻辑）
29. 实现任务 CRUD + 控制 API
30. 实现前端任务管理页面

### Phase 7：上架流程
31. 实现闲鱼发布商品页面自动化操作
32. 实现上架流程编排（采集→生成→上传→发布），集成全局设置中的各项参数
33. 实现进度持久化
34. 实现图片智能裁剪 3:4（Pillow）
35. 实现供应商黑名单过滤 + 关键词屏蔽检查
36. 实现价格计算逻辑（加价比例 + 加价金额）
37. 实现上架后延迟 + 模拟暂停休息逻辑
38. 端到端测试完整上架流程

### Phase 8：日志系统（三类日志）
39. 实现上架日志数据模型 + CRUD API + 汇总统计 API
40. 实现下架日志数据模型 + CRUD API + 汇总统计 API
41. 实现任务策略日志数据模型 + CRUD API + 汇总统计 API
42. 实现日志持久化（SQLite）+ 历史查询 + 分页
43. 实现前端上架日志页面（ListingLogs.vue）
44. 实现前端下架日志页面（DelistingLogs.vue）
45. 实现前端任务策略日志页面（TaskLogs.vue）
46. 实现日志导出功能（Excel/CSV）

### Phase 9：自动下架
47. 实现闲鱼商品列表页面自动化操作
48. 实现自动下架触发逻辑（售罄检测、策略下架、手动批量下架）
49. 下架操作写入下架日志

### Phase 10：实时日志前端
50. 实现 WebSocket 连接管理 composable
51. 实现 LogViewer 组件（虚拟滚动、过滤、搜索、导出）
52. 实现日志底部抽屉面板
53. 日志与任务关联展示

### Phase 11：闲鱼 WebSocket 通信层
54. 实现 sign 签名引擎（Node.js 子进程执行逆向 JS）
55. 实现闲鱼 WebSocket 客户端（连接、认证、心跳保活、断线重连）
56. 实现 Protobuf 消息编解码（base64 + Protobuf 解析）
57. 实现多店铺 WebSocket 连接管理器
58. 实现消息类型定义（文本/图片/音频/系统卡片）

### Phase 12：自动回复引擎
59. 实现会话上下文管理器（按店铺+用户隔离，历史对话管理）
60. 实现意图分类器（LLM 驱动，5 类意图：议价/技术/物流/售后/通用）
61. 实现多专家回复引擎（议价专家/技术专家/物流专家/售后专家/默认客服）
62. 实现专家 Prompt 模板（可前端编辑）
63. 实现商品信息注入（通过 HTTP API 获取商品详情注入 LLM 上下文）
64. 实现人工接管模式（关键词切换 + 前端状态展示）
65. 实现关键词回复规则（LLM 降级方案）
66. 实现模拟人工回复延迟
67. 实现前端自动回复页面（会话列表 + 对话窗口 + 规则配置 + 专家 Prompt 编辑）

### Phase 13：自动发货系统
68. 实现订单轮询器（APScheduler + 闲鱼 HTTP API）
69. 实现订单分类器（虚拟商品 / 实物代发）
70. 实现虚拟商品发货器（卡券/网盘链接/纯文本）
71. 实现卡池管理（前端批量导入 + 库存监控）
72. 实现实物代发发货器（1688 下单 → 物流单号获取 → 闲鱼回填）
73. 实现发货重试与异常处理
74. 实现发货配置 CRUD（前端页面）
75. 实现发货日志记录与统计

### Phase 14：AI 增强功能
76. 实现 AI 主图视频生成（调用文生视频 API）
77. 实现 AI 导购短标题生成
78. 实现视频上传到闲鱼

### Phase 15：收尾
79. 实现仪表盘统计页面（汇总上架/下架/任务/回复/发货数据）
80. 实现系统设置页面完善
81. 编写跨平台启动脚本
82. 编写 README 文档
83. 整体 UI 走查和优化

---

## 十、注意事项

1. **反爬策略：** 所有浏览器操作加随机延迟，模拟人类行为。不要高频请求，每个操作间隔 1-5 秒随机。
2. **错误处理：** 所有 API 返回统一格式 `{code: 0, data: {}, message: ""}`，错误时 code 非 0。
3. **异步设计：** 后端全部使用 async/await，浏览器操作不阻塞主线程。任务在独立的 asyncio Task 中运行。
4. **资源管理：** 浏览器实例及时关闭，使用 async context manager 管理生命周期。
5. **前端代理：** 开发时 Vite 代理 `/api` 和 `/ws` 到后端。生产环境可用 Nginx 反代或 FastAPI 托管静态文件。
6. **敏感信息：** API Key 加密存储，日志脱敏，不提交 `.env` 和 `data/` 目录到 Git。
7. **闲鱼页面结构变化：** 选择器可能随闲鱼更新而失效，选择器集中管理在配置文件中，便于维护更新。
8. **图片上传：** 闲鱼图片上传可能使用特殊组件，需处理文件选择对话框（Playwright `set_input_files`）或拖拽上传。
9. **任务并发：** 同一店铺同一时间只能有一个上架任务在运行，避免浏览器冲突。不同店铺可并行。
10. **程序重启恢复：** 程序异常退出后重启，处于 `running` 状态的任务自动降级为 `interrupted`，等待用户手动恢复。
11. **三类日志的区别：** 运行日志（4.7）= 事件流（WebSocket 实时推送）；上架日志（4.11）= 商品维度记录（每个商品上架结果）；任务策略日志（4.13）= 任务维度记录（任务级汇总）。三者独立存储，互不依赖。
12. **日志持久化：** 所有日志存储在 SQLite，程序重启后可查询历史日志。清空操作需二次确认，清空后不可恢复。
13. **全局设置生效时机：** 设置保存后立即写入数据库。正在运行中的任务不会实时感知设置变更（避免任务中途行为不一致），下一个任务创建/启动时读取最新配置。
14. **价格计算公式：** `闲鱼价格 = ceil(1688价格 × 加价比例 + 加价金额)`，结果取整数或保留一位小数（可配置）。
15. **供应商黑名单与关键词屏蔽：** 在采集阶段就进行过滤，不等到上架阶段才跳过，节省 LLM 调用成本。
16. **模拟暂停不改变任务状态：** 模拟休息期间任务状态仍为 `running`，前端进度条显示「休息中...」提示，不显示暂停按钮。
17. **AI 主图视频为可选增强功能：** 如文生视频 API 不可用或失败，降级为仅上传图片，不阻塞上架流程。
18. **双通道架构：** 系统同时使用两种通信方式与闲鱼交互——WebSocket 直连用于消息实时收发（自动回复），浏览器自动化（Playwright）用于页面表单操作（登录/上架/下架）。两者共享同一份 Cookie，但运行在不同模块中，互不干扰。
19. **Sign 签名依赖 Node.js：** 闲鱼 sign 签名算法是逆向 JS，必须通过 Node.js 子进程执行。部署环境需预装 Node.js 18+。签名 JS 文件放在 `backend/static/goofish_js/` 目录。
20. **Cookie 有效性是 WebSocket 生命线：** WebSocket 连接和 HTTP API 都依赖有效 Cookie。APScheduler 定时刷新 Cookie（通过 Playwright 重新加载页面获取最新 Cookie）。Cookie 过期时 WebSocket 自动断开，前端提示重新授权。
21. **Protobuf 协议可能变化：** 闲鱼可能更新消息协议，Protobuf 字段定义需要可配置（不硬编码字段序号），便于后续维护更新。
22. **多专家 Prompt 可编辑：** 议价/技术/物流/售后/默认五个专家的 Prompt 模板存储在数据库，前端可在线编辑，无需改代码。
23. **人工接管安全机制：** 人工接管模式下不自动回复，防止 AI 回复干扰人工沟通。切换关键词默认为句号「。」，前端可修改。
24. **虚拟商品发货为即时发货：** 买家付款后立即通过 WebSocket 发送卡密/链接，无需等待。实物代发需要等待 1688 发货后回填物流单号。
25. **会话上下文内存管理：** 每个会话最多保留 20 轮对话历史，超出自动丢弃最早的。长时间无消息的会话（超过 2 小时）自动清理释放内存。

---

## 十一、开源参考项目

本项目的设计参考了以下开源项目的核心原理（代码自行实现，不直接使用）：

| 项目 | 参考内容 |
|------|----------|
| [XianYuApis](https://github.com/cv-cat/XianYuApis) | 闲鱼 WebSocket 私信协议逆向（sign 签名 + base64 + Protobuf）、HTTP API 封装、Cookie 管理、消息类型定义 |
| [XianyuAutoAgent](https://github.com/shaxiu/XianyuAutoAgent) | 多专家协同决策架构、意图分类路由、会话上下文管理、商品信息注入、人工接管模式、模拟人工回复延迟 |
| [xianyu-auto-reply](https://github.com/zhinianboke/xianyu-auto-reply) | 微服务拆分思路、定时任务调度（APScheduler）、自动发货（卡券/虚拟商品）、Cookie 定时刷新、多账号管理 |

**参考原则：** 学习其架构设计和核心原理，代码全部自行编写，不复制开源项目代码。

---

## 十二、开发约定

- 后端 Python 代码遵循 PEP 8，使用 `black` 格式化 + `ruff` 检查
- 前端 JS 代码使用 ESLint + Prettier
- 所有函数和类添加 docstring / JSDoc 注释
- API 接口添加 Pydantic 请求/响应模型，自动生成 OpenAPI 文档
- 前端 API 调用统一在 `api/` 目录封装，组件不直接调用 Axios
- 组件命名用 PascalCase，文件名与组件名一致
- 后端模块间通过依赖注入解耦，不直接 import 具体实现

---

## 给 Claude Code 的指令

请按照以上设计文档，从 Phase 1 开始逐步实现。每个 Phase 完成后暂停，让我确认后再继续下一个 Phase。代码要求：

1. 完整可运行，不要省略任何文件
2. 每个文件写完整实现，不用 `// ... 其余代码` 这样的省略
3. 关键逻辑添加注释
4. 先实现核心骨架，再填充细节
5. 遇到设计文档中未明确的细节，做出合理假设并在代码注释中标注
6. 前端页面要求实际可用，不是占位符
7. 后端 API 要求实际可调用，返回真实数据

**特别提醒：**
- 闲鱼 WebSocket 协议层（4.8）涉及 sign 签名算法（逆向 JS）和 Protobuf 编解码，这是整个自动回复功能的技术基础。sign 签名 JS 文件需要单独提供，代码中预留接口和调用逻辑即可，JS 文件路径配置在 `backend/static/goofish_js/goofish_sign.js`
- Playwright 仅用于：扫码登录、Cookie 获取/刷新、商品上架/下架表单操作。消息收发走 WebSocket 直连，不走浏览器自动化
- 开源参考项目（第十一节）仅用于理解原理，所有代码自行编写
