# 任务001 - 多Agent协作系统业务流程图

## 1. 整体架构流程

```mermaid
flowchart TB
    subgraph 用户层
        U[👤 用户]
        WC[🖥️ 网页控制台]
    end
    
    subgraph 接入层
        API[⚡ API网关<br/>FastAPI:9000]
        WS[🔌 WebSocket]
    end
    
    subgraph 协调层
        PA[📋 Product Agent<br/>协调者]
        COORD[🔄 任务协调器]
        EVAL[📊 任务评估器]
    end
    
    subgraph 执行层
        AA[🏗️ Architect]
        DA[💻 Developer]
        RA[🔍 Reviewer]
        TA[🧪 Tester]
    end
    
    subgraph 支撑层
        CTX[📦 上下文<br/>198K]
        MEM[🧠 记忆<br/>Redis+Chroma]
        LLM[🤖 LLM<br/>GLM5]
    end
    
    U -->|访问| WC
    WC <-->|WS| WS
    WS --> API
    API --> PA
    PA --> COORD --> EVAL
    EVAL --> AA & DA & RA & TA
    AA & DA & RA & TA --> COORD --> PA --> API --> WC --> U
    
    PA & AA & DA & RA & TA <--> CTX & MEM
    PA & AA & DA & RA & TA --> LLM
```

---

## 2. 四阶段交付流程

```mermaid
flowchart LR
    subgraph 阶段1
        S1[需求输入] --> P1[PRD生成] --> R1{人工审核}
    end
    
    subgraph 阶段2
        R1 -->|通过| S2[PRD提交] --> P2[测试用例] --> R2{人工审核}
    end
    
    subgraph 阶段3
        R2 -->|通过| S3[启动开发] --> P3[多Agent协作] --> R3{测试通过}
    end
    
    subgraph 阶段4
        R3 -->|通过| S4[生成报告] --> P4[PDF报告] --> END[✅ 交付完成]
    end
    
    R1 -->|修改| P1
    R2 -->|修改| P2
    R3 -->|修复| P3
```

---

## 3. 多Agent协作开发流程

```mermaid
flowchart TB
    START([开始])
    
    subgraph 任务分解
        A1[Product Agent<br/>接收需求]
        A2[任务分解]
        A3[任务评估]
        A4{评估通过?}
    end
    
    subgraph 架构设计
        B1[Architect Agent]
        B2[架构设计]
        B3[技术选型]
        B4[方案评审]
    end
    
    subgraph 代码开发
        C1[Developer Agent]
        C2[代码实现]
        C3[单元测试]
        C4[文档编写]
    end
    
    subgraph 代码审查
        D1[Reviewer Agent]
        D2[代码审查]
        D3[安全审计]
        D4[性能分析]
    end
    
    subgraph 测试验证
        E1[Tester Agent]
        E2[测试执行]
        E3[缺陷分析]
        E4[测试报告]
    end
    
    subgraph 质量门禁
        F1{质量通过?}
        F2[修复问题]
    end
    
    END([交付完成])
    
    START --> A1 --> A2 --> A3 --> A4
    A4 -->|否| H[人工决策]
    H --> A4
    A4 -->|是| B1
    
    B1 --> B2 --> B3 --> B4 --> C1
    C1 --> C2 --> C3 --> C4 --> D1
    D1 --> D2 --> D3 --> D4 --> E1
    E1 --> E2 --> E3 --> E4 --> F1
    
    F1 -->|否| F2 --> C1
    F1 -->|是| END
```

---

## 4. 任务评估决策流程

```mermaid
flowchart TB
    TASK[📥 接收任务]
    
    subgraph 评估
        E1[完成概率]
        E2[Token消耗]
        E3[时间预估]
    end
    
    subgraph 判断
        C1{概率>70%?}
        C2{Token<预算?}
        C3{时间<截止?}
    end
    
    subgraph 结果
        R1[✅ 批准执行]
        R2[❌ 拒绝执行]
        R3[👤 人工决策]
    end
    
    TASK --> E1 & E2 & E3
    E1 --> C1
    E2 --> C2
    E3 --> C3
    
    C1 -->|是| C2
    C1 -->|否| R2
    C2 -->|是| C3
    C2 -->|否| R2
    C3 -->|是| R1
    C3 -->|否| R3
    
    R2 --> R3
    R3 -->|确认| R1
    R3 -->|取消| END([结束])
    R1 --> RUN[🚀 执行任务]
```

---

## 5. 上下文管理流程

```mermaid
flowchart LR
    subgraph 分层存储
        L1[全局层<br/>10K tokens<br/>系统配置]
        L2[会话层<br/>100K tokens<br/>对话历史]
        L3[任务层<br/>50K tokens<br/>当前任务]
        L4[记忆层<br/>38K tokens<br/>检索记忆]
    end
    
    subgraph 管理
        M1[Token估算]
        M2{超限检查}
        M3[自动压缩]
        M4[摘要生成]
    end
    
    subgraph 输出
        O1[组合上下文]
        O2[发送LLM]
    end
    
    L1 & L2 & L3 & L4 --> M1 --> M2
    M2 -->|超限| M3 --> M4 --> M2
    M2 -->|正常| O1 --> O2
```

---

## 6. Agent消息流转时序

```mermaid
sequenceDiagram
    participant U as 用户
    participant PA as Product
    participant AA as Architect
    participant DA as Developer
    participant RA as Reviewer
    participant TA as Tester
    
    U->>PA: 提交需求
    PA->>PA: 任务分解
    PA->>AA: 分发架构任务
    AA->>AA: 设计架构
    AA-->>PA: 返回架构方案
    
    PA->>DA: 分发开发任务
    DA->>DA: 实现代码
    DA-->>PA: 返回代码
    
    PA->>RA: 分发审查任务
    RA->>RA: 代码审查
    RA-->>PA: 返回审查报告
    
    PA->>TA: 分发测试任务
    TA->>TA: 执行测试
    TA-->>PA: 返回测试报告
    
    PA->>PA: 汇总结果
    PA-->>U: 交付完成
```

---

## 7. 网页控制台交互流程

```mermaid
sequenceDiagram
    participant B as 浏览器
    participant WC as 控制台
    participant WS as WebSocket
    participant AG as Agent
    
    B->>WC: 打开页面
    WC->>WS: 建立连接
    WS-->>WC: 连接成功
    
    B->>WC: 输入消息
    WC->>WS: 发送 {type:msg, agent:developer}
    WS->>AG: 路由到Agent
    
    AG->>WS: 状态更新 {status:working}
    WS->>WC: 更新UI
    
    AG->>AG: 处理+调用LLM
    AG->>WS: 返回响应
    WS->>WC: 显示结果
    
    AG->>WS: 状态更新 {status:idle}
    WS->>WC: 更新UI
    WC-->>B: 实时展示
```

---

## 8. 记忆管理流程

```mermaid
flowchart TB
    subgraph 写入
        W1[Agent产生记忆]
        W2[短期存储<br/>Redis 24h]
        W3{永久保存?}
        W4[长期存储<br/>ChromaDB]
    end
    
    subgraph 检索
        R1[检索请求]
        R2[语义检索]
        R3[关键词检索]
        R4[时间衰减]
        R5[合并排序]
    end
    
    W1 --> W2 --> W3
    W3 -->|是| W4
    W3 -->|否| E1([完成])
    W4 --> E1
    
    R1 --> R2 & R3
    R2 & R3 --> R4 --> R5 --> E2([返回])
```

---

## 9. 数据流架构

```mermaid
flowchart TB
    subgraph 前端
        UI[网页控制台]
    end
    
    subgraph 网关
        WS[WebSocket]
        API[REST API]
    end
    
    subgraph Agent集群
        PA[Product]
        AA[Architect]
        DA[Developer]
        RA[Reviewer]
        TA[Tester]
    end
    
    subgraph 上下文
        CTX[Context Manager<br/>198K tokens]
    end
    
    subgraph 存储
        R[(Redis)]
        C[(ChromaDB)]
        F[(Files)]
    end
    
    subgraph LLM
        L[LLM API]
    end
    
    UI <--> WS & API
    WS & API --> PA
    PA --> AA & DA & RA & TA
    
    PA & AA & DA & RA & TA <--> CTX
    PA & AA & DA & RA & TA <--> R & C & F
    PA & AA & DA & RA & TA --> L
```

---

## 10. 质量监控流程

```mermaid
flowchart LR
    subgraph 监控指标
        M1[上下文<198K]
        M2[Token<预算]
        M3[响应<30s]
        M4[成功率>80%]
    end
    
    subgraph 判断
        C{超限?}
    end
    
    subgraph 处理
        H1[压缩上下文]
        H2[拒绝任务]
        H3[人工介入]
    end
    
    M1 & M2 & M3 & M4 --> C
    C -->|是| H1 & H2 & H3
    C -->|否| OK([继续])
```

---

## 流程图说明

| 图表 | 说明 |
|------|------|
| 整体架构流程 | 系统各层组件交互关系 |
| 四阶段交付流程 | PRD→测试用例→开发→报告 |
| 多Agent协作流程 | 5个Agent协作开发完整流程 |
| 任务评估决策 | 自动评估+人工决策机制 |
| 上下文管理 | 198K分层管理+自动压缩 |
| Agent消息流转 | Agent间任务分发时序 |
| 网页控制台交互 | WebSocket实时通信 |
| 记忆管理 | 短期+长期记忆读写 |
| 数据流架构 | 完整数据流转路径 |
| 质量监控 | 关键指标监控告警 |

---

**所有流程图支持Mermaid渲染**（GitHub、Typora、VS Code等）
