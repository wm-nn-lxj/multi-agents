# 多智能体工作空间

基于 OpenClaw 的智能多智能体协作平台，包含 5 个专业化 Agent，实现软件开发生命周期全流程自动化。

## 🌟 项目概述

本工作空间整合了完整的多智能体系统与 OpenClaw 框架，通过协作式 AI 智能体实现智能化的软件开发流程。

### 核心特性

- 🤖 **5 个专业智能体**：产品、架构、开发、审查、测试
- 🧠 **198K 上下文支持**：先进的分层上下文管理
- 💾 **双记忆系统**：Redis 短期记忆 + ChromaDB 长期记忆
- 🌐 **网页控制台**：实时多智能体聊天界面
- 🔌 **REST API**：完整的 HTTP/WebSocket 接口
- 🛠️ **69+ 技能**：可扩展的技能系统

## 📁 项目结构

```
multi-agents/
├── AGENTS.md              # 智能体工作空间配置
├── SOUL.md                # 智能体个性与行为定义
├── USER.md                # 用户偏好设置
├── TOOLS.md               # 工具使用指南
├── IDENTITY.md            # 智能体身份
├── HEARTBEAT.md           # 定时任务配置
│
├── projects/              # 项目文件
│   ├── multi-agent-system/    # 核心多智能体系统
│   └── multi-agent-2c/        # 2C 变体版本
│
├── skills/                # 69+ 智能体技能
│   ├── agent_reach/           # 网页抓取与搜索
│   ├── daily-hot-news/        # 每日热榜聚合
│   ├── feishu-*/              # 飞书集成套件
│   ├── meitu-skills/          # 图像处理套件
│   └── ...                    # 更多技能
│
├── memory/                # 会话记忆
├── logs/                  # 系统日志
└── repo/                  # Git 仓库
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+（用于 OpenClaw）
- Redis（可选，用于记忆存储）
- LLM API（OpenAI/Azure/智谱AI）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/wm-nn-lxj/multi-agents.git
cd multi-agents

# 安装依赖
pip install -r projects/multi-agent-system/requirements.txt

# 配置环境变量
cp projects/multi-agent-system/.env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 启动系统
python projects/multi-agent-system/run_console.py
```

### 访问网页控制台

打开浏览器访问：http://localhost:9000

## 🤖 智能体介绍

| 智能体 | 角色 | 核心能力 |
|--------|------|----------|
| 📋 **产品智能体** | 产品经理 | PRD 生成、任务分解、协调调度 |
| 🏗️ **架构智能体** | 系统架构师 | 架构设计、技术选型、方案评审 |
| 💻 **开发智能体** | 开发工程师 | 代码实现、重构优化、文档编写 |
| 🔍 **审查智能体** | 代码审查员 | 代码 Review、安全审计、规范检查 |
| 🧪 **测试智能体** | 测试工程师 | 测试用例生成、缺陷分析、质量报告 |

## 🛠️ 内置技能

### 效率工具
- `daily-hot-news` - 54+ 平台每日热榜聚合
- `daily-tech-broadcast` - 科技新闻简报
- `alphaear-news` - 金融资讯与预测

### 开发工具
- `agent_reach` - 15+ 平台网页抓取
- `test-case-generator` - 需求文档生成测试用例
- `prd-writer` - PRD 生成与原型设计

### 内容创作
- `meitu-skills` - AI 图像处理套件
- `claw-art` - AI 艺术生成
- `excalidraw-diagram` - 流程图生成
- `pptx` - PPT 生成

### 集成工具
- `feishu-*` - 飞书/Lark 集成套件
- `vercel-deploy` - Vercel 部署

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    网页控制台                           │
│                  (localhost:9000)                       │
└─────────────────────┬───────────────────────────────────┘
                      │ WebSocket
┌─────────────────────▼───────────────────────────────────┐
│                   API 层                                │
│              (FastAPI + WebSocket)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│               消息总线                                  │
└───────┬───────┬───────┬───────┬───────┬─────────────────┘
        │       │       │       │       │
   ┌────▼───┐ ┌─▼───┐ ┌─▼───┐ ┌─▼───┐ ┌─▼───┐
   │ 产品   │ │架构 │ │开发 │ │审查 │ │测试 │
   │ 智能体 │ │智能体│ │智能体│ │智能体│ │智能体│
   └────┬───┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
        │       │       │       │       │
   ┌────▼───────────────▼───────────────▼────┐
   │         上下文管理器 (198K)             │
   └───────────────────┬─────────────────────┘
                       │
   ┌───────────────────▼─────────────────────┐
   │            记忆系统                     │
   │  ┌─────────┐      ┌──────────────┐     │
   │  │  Redis  │      │   ChromaDB   │     │
   │  │(短期)   │      │    (长期)    │     │
   │  └─────────┘      └──────────────┘     │
   └─────────────────────────────────────────┘
                       │
   ┌───────────────────▼─────────────────────┐
   │            LLM 客户端                   │
   │    (OpenAI / Azure / 智谱AI)            │
   └─────────────────────────────────────────┘
```

## 📖 文档

- [多智能体系统说明](projects/multi-agent-system/README.md)
- [产品需求文档](projects/multi-agent-system/PRD.md)
- [测试用例](projects/multi-agent-system/TestCases.md)
- [测试报告](projects/multi-agent-system/TestReport.md)

## 🔧 配置说明

### 环境变量

```bash
# LLM 配置
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# 系统配置
API_PORT=9000
LOG_LEVEL=INFO

# 记忆配置
REDIS_URL=redis://localhost:6379/0
VECTOR_DB_PATH=./data/chroma

# 上下文配置
MAX_CONTEXT_TOKENS=198000
```

### LLM 配置示例

**OpenAI 官方**:
```bash
OPENAI_API_KEY=sk-xxxxx
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

**智谱 AI**:
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

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| 上下文限制 | 198K tokens |
| 响应时间 | < 30秒 |
| 并发会话 | 10+ |
| 智能体成功率 | > 80% |

## 🌐 API 接口

### 基础端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 控制台页面 |
| `/health` | GET | 健康检查 |
| `/ws` | WebSocket | 实时通信 |

### WebSocket 示例

```javascript
const ws = new WebSocket('ws://localhost:9000/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'msg',
    agent: 'developer',
    content: '写一个排序函数'
  }));
};

ws.onmessage = (e) => {
  console.log(JSON.parse(e.data));
};
```

## ❓ 常见问题

### Q1: 启动时报错 "LLM API Key 未配置"

确保 `.env` 文件中设置了 `OPENAI_API_KEY`。

### Q2: 无法连接网页控制台

检查端口是否被占用：`lsof -i :9000`，或使用其他端口启动。

### Q3: Redis 连接失败

启动 Redis：`docker run -d -p 6379:6379 redis`，或系统会自动降级为内存存储。

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - AI 智能体框架
- [ClawHub](https://clawhub.com) - 技能市场

---

**Made with ❤️ by wm-nn-lxj**
