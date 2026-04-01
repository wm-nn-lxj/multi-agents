# 多Agent协作系统 - 部署指南

**版本**: v1.0.0  
**更新日期**: 2026-03-31

---

## 📋 目录

1. [系统概述](#系统概述)
2. [环境要求](#环境要求)
3. [快速部署](#快速部署)
4. [配置说明](#配置说明)
5. [启动服务](#启动服务)
6. [网页控制台](#网页控制台)
7. [API接口](#api接口)
8. [常见问题](#常见问题)

---

## 系统概述

多Agent协作系统是一个面向软件产品开发的多Agent协作平台，包含5个专业化Agent：

| Agent | 角色 | 核心能力 |
|-------|------|----------|
| 📋 **Product Agent** | 产品管理 | PRD生成、任务分解、协调调度 |
| 🏗️ **Architect Agent** | 架构设计 | 架构设计、技术选型、方案评审 |
| 💻 **Developer Agent** | 代码开发 | 代码实现、重构、文档编写 |
| 🔍 **Reviewer Agent** | 代码审查 | 代码Review、安全审计、规范检查 |
| 🧪 **Tester Agent** | 测试验证 | 测试用例生成、缺陷分析、质量报告 |

### 核心特性

- ✅ **上下文管理**: 支持198K tokens上下文
- ✅ **分层记忆**: Redis短期记忆 + ChromaDB长期记忆
- ✅ **任务评估**: 自动评估任务完成概率和Token消耗
- ✅ **网页控制台**: 实时多Agent消息窗口
- ✅ **REST API**: 完整的HTTP接口

---

## 环境要求

### 必需环境

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.10+ | 核心运行环境 |
| pip | 21.0+ | 包管理器 |

### 可选组件

| 组件 | 用途 | 安装命令 |
|------|------|----------|
| Redis | 短期记忆存储 | `docker run -d -p 6379:6379 redis` |
| ChromaDB | 长期记忆存储 | 自动安装（pip） |

### LLM API

支持OpenAI API兼容接口：
- OpenAI GPT-4
- Azure OpenAI
- 智谱AI (GLM)
- 其他兼容接口

---

## 快速部署

### 方式一：本地部署（推荐）

```bash
# 1. 克隆/下载项目
cd multi-agent-system

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量
cp .env.example .env
# 编辑.env文件，设置OPENAI_API_KEY

# 6. 启动服务
python run_console.py
```

### 方式二：Docker部署

```bash
# 构建镜像
docker build -t multi-agent-system .

# 运行容器
docker run -d \
  -p 9000:9000 \
  -e OPENAI_API_KEY=your-api-key \
  -e OPENAI_BASE_URL=https://api.openai.com/v1 \
  --name agent-console \
  multi-agent-system
```

### 方式三：一键启动

```bash
# Linux/macOS
chmod +x start.sh
./start.sh

# Windows
start.bat
```

---

## 配置说明

### 环境变量配置

创建 `.env` 文件：

```bash
# ============ LLM配置 (必填) ============
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# ============ 系统配置 ============
API_PORT=9000
LOG_LEVEL=INFO

# ============ 记忆配置 (可选) ============
REDIS_URL=redis://localhost:6379/0
VECTOR_DB_PATH=./data/chroma

# ============ 上下文配置 ============
MAX_CONTEXT_TOKENS=198000
```

### LLM配置示例

**OpenAI官方**:
```bash
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

**智谱AI**:
```bash
OPENAI_API_KEY=your-zhipu-api-key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4
```

**Azure OpenAI**:
```bash
OPENAI_API_KEY=your-azure-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
LLM_MODEL=gpt-4
```

### 上下文配置

系统支持198K tokens上下文，分层配置：

| 层级 | 默认大小 | 说明 |
|------|----------|------|
| 全局层 | 10K | 系统配置、项目信息 |
| 会话层 | 100K | 对话历史 |
| 任务层 | 50K | 当前任务上下文 |
| 记忆层 | 38K | 检索到的相关记忆 |

---

## 启动服务

### 启动API服务

```bash
# 基础启动
python run_console.py

# 指定端口
python run_console.py --port 8080

# 后台运行
nohup python run_console.py > console.log 2>&1 &
```

### 启动网页控制台

```bash
# 启动控制台（端口9000）
python run_console.py

# 访问地址
# 本地: http://localhost:9000
# 局域网: http://your-ip:9000
```

### 检查服务状态

```bash
# 检查服务是否运行
curl http://localhost:9000

# 检查健康状态
curl http://localhost:9000/health
```

---

## 网页控制台

### 访问方式

1. **本地访问**: 打开浏览器访问 `http://localhost:9000`

2. **使用HTML文件**: 
   - 打开 `console.html` 文件
   - 输入服务器地址
   - 点击连接

### 控制台功能

```
┌─────────────────────────────────────────────────────┐
│           🤖 Multi-Agent Console                    │
├──────────────┬──────────────┬──────────────────────┤
│ 📋 Product   │ 🏗️ Architect │ 💻 Developer         │
│   [消息区]   │   [消息区]   │   [消息区]           │
│ [输入][发送] │ [输入][发送] │ [输入][发送]         │
├──────────────┼──────────────┼──────────────────────┤
│ 🔍 Reviewer  │ 🧪 Tester    │ 📊 System Log        │
│   [消息区]   │   [消息区]   │   [消息区]           │
│ [输入][发送] │ [输入][发送] │                      │
└──────────────┴──────────────┴──────────────────────┘
```

### 使用方法

1. 在Agent窗口的输入框中输入消息
2. 按 Enter 或点击 Send 发送
3. Agent会处理消息并返回结果
4. 所有消息实时显示在窗口中

### 示例对话

**Product Agent**:
```
用户: 生成一个用户登录功能的PRD
Agent: # 用户登录功能 PRD
       ## 1. 功能概述
       实现用户登录认证功能...
```

**Developer Agent**:
```
用户: 实现一个Python快速排序函数
Agent: ```python
       def quick_sort(arr):
           if len(arr) <= 1:
               return arr
           pivot = arr[len(arr) // 2]
           ...
       ```
```

---

## API接口

### 基础端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 控制台页面 |
| `/health` | GET | 健康检查 |
| `/ws` | WebSocket | 实时通信 |

### WebSocket协议

**发送消息**:
```json
{
  "type": "msg",
  "agent": "developer",
  "content": "写一个排序函数"
}
```

**接收消息**:
```json
{
  "type": "msg",
  "agent": "developer",
  "content": "这是排序函数的实现..."
}
```

**状态更新**:
```json
{
  "type": "status",
  "agent": "developer",
  "status": "working"
}
```

### JavaScript示例

```javascript
const ws = new WebSocket('ws://localhost:9000/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'msg',
    agent: 'developer',
    content: 'Hello'
  }));
};

ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log(data);
};
```

### Python示例

```python
import websockets
import asyncio
import json

async def chat():
    async with websockets.connect('ws://localhost:9000/ws') as ws:
        # 发送消息
        await ws.send(json.dumps({
            'type': 'msg',
            'agent': 'developer',
            'content': '写一个函数'
        }))
        
        # 接收响应
        response = await ws.recv()
        print(json.loads(response))

asyncio.run(chat())
```

---

## 项目结构

```
multi-agent-system/
├── README.md                 # 本文档
├── PRD.md                    # 产品需求文档
├── TestCases.md              # 测试用例文档
├── requirements.txt          # Python依赖
├── .env.example              # 环境变量模板
├── .env                      # 环境变量配置
├── run_console.py            # 控制台启动脚本
├── console.html              # 独立控制台页面
├── start.sh                  # Linux启动脚本
├── start.bat                 # Windows启动脚本
│
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py       # 全局配置
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_agent.py     # Agent基类
│   │   ├── llm_client.py     # LLM客户端
│   │   ├── context_manager.py# 上下文管理
│   │   ├── memory_manager.py # 记忆管理
│   │   └── message_bus.py    # 消息总线
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── product_agent.py  # 产品Agent
│   │   ├── architect_agent.py# 架构Agent
│   │   ├── developer_agent.py# 开发Agent
│   │   ├── reviewer_agent.py # 审查Agent
│   │   └── tester_agent.py   # 测试Agent
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py           # FastAPI应用
│   │
│   └── console/
│       ├── __init__.py
│       └── web_console.py    # 网页控制台
│
├── tests/
│   ├── __init__.py
│   └── test_system.py        # 系统测试
│
└── data/
    └── chroma/               # 向量数据库
```

---

## 常见问题

### Q1: 启动时报错 "LLM API Key未配置"

**解决方案**:
```bash
# 检查.env文件
cat .env

# 确保设置了API Key
echo 'OPENAI_API_KEY=your-key' >> .env
```

### Q2: 无法连接到网页控制台

**解决方案**:
```bash
# 1. 检查服务是否运行
ps aux | grep run_console

# 2. 检查端口是否被占用
lsof -i :9000

# 3. 尝试其他端口
python run_console.py --port 8080
```

### Q3: Agent响应很慢

**原因**: LLM API响应时间取决于模型和网络

**优化建议**:
- 使用更快的模型（如gpt-3.5-turbo）
- 减少上下文大小
- 使用本地部署的模型

### Q4: Redis连接失败

**解决方案**:
```bash
# 启动Redis
docker run -d -p 6379:6379 redis

# 或禁用Redis（使用内存存储）
# 系统会自动降级
```

### Q5: 如何查看日志

```bash
# 查看控制台日志
tail -f console.log

# 查看系统日志
tail -f logs/agent_system.log
```

### Q6: 如何更新系统

```bash
# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
```

---

## 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 上下文限制 | 198K tokens | 分层管理 |
| 单任务响应 | < 30秒 | 取决于LLM |
| 并发支持 | 10+ | 异步处理 |
| Agent成功率 | > 80% | 功能测试 |

---

## 技术支持

- **文档**: 查看 `PRD.md` 和 `TestCases.md`
- **问题反馈**: 提交 Issue
- **社区支持**: 加入讨论群

---

## 更新日志

### v1.0.0 (2026-03-31)
- ✅ 初始版本发布
- ✅ 5个Agent完整实现
- ✅ 198K上下文支持
- ✅ 网页控制台
- ✅ WebSocket实时通信
- ✅ 完整测试覆盖

---

## 许可证

MIT License

---

**部署完成后，访问 http://localhost:9000 开始使用！** 🎉
