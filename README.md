# Multi-Agents Workspace

An intelligent multi-agent collaboration platform powered by OpenClaw, featuring 5 specialized agents for software development lifecycle automation.

## 🌟 Overview

This workspace integrates a complete multi-agent system with OpenClaw framework, enabling AI-powered software development through collaborative agents.

### Key Features

- 🤖 **5 Specialized Agents**: Product, Architect, Developer, Reviewer, Tester
- 🧠 **198K Context Support**: Advanced context management with layered memory
- 💾 **Dual Memory System**: Redis short-term + ChromaDB long-term memory
- 🌐 **Web Console**: Real-time multi-agent chat interface
- 🔌 **REST API**: Complete HTTP/WebSocket interfaces
- 🛠️ **69+ Skills**: Extensible skill system for various tasks

## 📁 Project Structure

```
multi-agents/
├── AGENTS.md              # Agent workspace configuration
├── SOUL.md                # Agent personality and behavior
├── USER.md                # User preferences
├── TOOLS.md               # Tool usage guidelines
├── IDENTITY.md            # Agent identity
├── HEARTBEAT.md           # Periodic task configuration
│
├── projects/              # Project files
│   ├── multi-agent-system/    # Core multi-agent system
│   └── multi-agent-2c/        # 2C variant
│
├── skills/                # 69+ agent skills
│   ├── agent_reach/           # Web scraping & search
│   ├── daily-hot-news/        # Daily news aggregation
│   ├── feishu-*/              # Feishu integration
│   ├── meitu-skills/          # Image processing
│   └── ...                    # More skills
│
├── memory/                # Session memory
├── logs/                  # System logs
└── repo/                  # Git repositories
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for OpenClaw)
- Redis (optional, for memory)
- LLM API (OpenAI/Azure/智谱AI)

### Installation

```bash
# Clone the repository
git clone https://github.com/wm-nn-lxj/multi-agents.git
cd multi-agents

# Install dependencies
pip install -r projects/multi-agent-system/requirements.txt

# Configure environment
cp projects/multi-agent-system/.env.example .env
# Edit .env with your API keys

# Start the system
python projects/multi-agent-system/run_console.py
```

### Access Web Console

Open browser: http://localhost:9000

## 🤖 Agents

| Agent | Role | Capabilities |
|-------|------|--------------|
| 📋 **Product** | Product Manager | PRD generation, task breakdown, coordination |
| 🏗️ **Architect** | System Architect | Architecture design, tech selection, review |
| 💻 **Developer** | Developer | Code implementation, refactoring, documentation |
| 🔍 **Reviewer** | Code Reviewer | Code review, security audit, standards check |
| 🧪 **Tester** | QA Engineer | Test case generation, defect analysis, reports |

## 🛠️ Skills Included

### Productivity
- `daily-hot-news` - Daily trending news from 54+ platforms
- `daily-tech-broadcast` - Tech news summaries
- `alphaear-news` - Financial news and predictions

### Development
- `agent_reach` - Web scraping for 15+ platforms
- `test-case-generator` - Generate test cases from requirements
- `prd-writer` - PRD generation with prototypes

### Content Creation
- `meitu-skills` - AI image processing suite
- `claw-art` - AI art generation
- `excalidraw-diagram` - Diagram generation
- `pptx` - PowerPoint generation

### Integration
- `feishu-*` - Feishu/Lark integration suite
- `vercel-deploy` - Vercel deployment

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Console                          │
│                  (localhost:9000)                       │
└─────────────────────┬───────────────────────────────────┘
                      │ WebSocket
┌─────────────────────▼───────────────────────────────────┐
│                   API Layer                             │
│              (FastAPI + WebSocket)                      │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│               Message Bus                               │
└───────┬───────┬───────┬───────┬───────┬─────────────────┘
        │       │       │       │       │
   ┌────▼───┐ ┌─▼───┐ ┌─▼───┐ ┌─▼───┐ ┌─▼───┐
   │Product │ │Arch │ │ Dev │ │ Rev │ │Test │
   │ Agent  │ │Agent│ │Agent│ │Agent│ │Agent│
   └────┬───┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
        │       │       │       │       │
   ┌────▼───────────────▼───────────────▼────┐
   │         Context Manager (198K)          │
   └───────────────────┬─────────────────────┘
                       │
   ┌───────────────────▼─────────────────────┐
   │            Memory System                │
   │  ┌─────────┐      ┌──────────────┐     │
   │  │  Redis  │      │   ChromaDB   │     │
   │  │(Short)  │      │    (Long)    │     │
   │  └─────────┘      └──────────────┘     │
   └─────────────────────────────────────────┘
                       │
   ┌───────────────────▼─────────────────────┐
   │            LLM Client                   │
   │    (OpenAI / Azure / 智谱AI)            │
   └─────────────────────────────────────────┘
```

## 📖 Documentation

- [Multi-Agent System README](projects/multi-agent-system/README.md)
- [PRD Document](projects/multi-agent-system/PRD.md)
- [Test Cases](projects/multi-agent-system/TestCases.md)
- [Test Report](projects/multi-agent-system/TestReport.md)

## 🔧 Configuration

### Environment Variables

```bash
# LLM Configuration
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# System Configuration
API_PORT=9000
LOG_LEVEL=INFO

# Memory Configuration
REDIS_URL=redis://localhost:6379/0
VECTOR_DB_PATH=./data/chroma

# Context Configuration
MAX_CONTEXT_TOKENS=198000
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| Context Limit | 198K tokens |
| Response Time | < 30s |
| Concurrent Sessions | 10+ |
| Agent Success Rate | > 80% |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

MIT License

## 🙏 Acknowledgments

- [OpenClaw](https://github.com/openclaw/openclaw) - AI Agent Framework
- [ClawHub](https://clawhub.com) - Skills Marketplace

---

**Made with ❤️ by wm-nn-lxj**
