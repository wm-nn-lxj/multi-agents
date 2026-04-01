---
name: sleep-cli
description: "通过 CLI 获取用户睡眠数据。当用户询问睡眠时长、质量、睡眠阶段、入睡/起床时间相关问题时，使用此 CLI 命令获取数据后再分析。"
metadata:
  {
    "pha": {
      "emoji": "🌙",
      "category": "health-data-cli",
      "tags": ["cli", "sleep", "sleep-quality"],
      "requires": { "tools": ["get_sleep"] }
    }
  }
---

# 睡眠数据 CLI 获取指南

## 日期偏移规则

睡眠数据记录在**醒来日期**下，查询时必须做日期偏移：

| 用户表述 | 应查询的日期 | 说明 |
|---------|-----------|------|
| "昨天 / 昨晚 / 今天的睡眠" | 今天 | 最近一次醒来（今天早上） |
| "前天的睡眠" | 前天 | 前天醒来 |
| "前天晚上的睡眠" | 昨天 | 前天入睡 → 昨天醒来（日期 +1） |
| "X 日晚上的睡眠" | X+1 日 | 当晚入睡，次日醒来（日期 +1） |
| "今晚的睡眠" | 不传时间参数 | 尚未发生 |

**核心规则**：表述含"晚上" → 日期 +1；不含"晚上" → 直接使用该日期。

**⚠️ 重要**：查询"昨天 / 昨晚 / 今天的睡眠"时，必须使用 `--date today` 而非推算具体日期（如 `2026-03-28`）。`today` 由服务端实时解析，避免模型日期判断偏差。

## 命令示例

### 获取今日睡眠
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_sleep --date today
```

### 获取指定日期睡眠
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_sleep --date 2024-01-15
```

### 获取最近 7 天睡眠趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_sleep --last-days 7
```

### 获取最近 30 天睡眠趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_sleep --last-days 30
```

### 获取指定日期范围
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_sleep --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `date` | **实际睡眠日期**（按起床时间归属，可能与查询日期不同，必须核对） |
| `durationHours` | 总睡眠时长（小时） |
| `qualityScore` | 睡眠质量综合评分（0–100，越高越好） |
| `bedTime` | 入睡时间（HH:MM） |
| `wakeTime` | 起床时间（HH:MM） |
| `stages.deep` | 深睡时长（分钟，参考占比 20–60%） |
| `stages.light` | 浅睡时长（分钟，参考占比 <55%） |
| `stages.rem` | REM 快速眼动时长（分钟，参考占比 10–30%） |
| `stages.awake` | 清醒时长（分钟） |

## ⚠️ 无数据处理规则

查询日期无睡眠记录时，接口直接返回 `null`，**不会自动回溯到其他日期**。

| 情况 | 如何处理 |
|------|---------|
| `data` 为 `null` | 告知用户"该日期暂无睡眠记录，可能数据未同步或未佩戴手表" |
| 有数据 | `date` 字段即为查询日期，正常分析 |

## 参考范围

- **成人推荐睡眠时长**：7–9 小时
- **qualityScore**：≥70 为良好
