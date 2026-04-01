---
name: stress-cli
description: "通过 CLI 获取用户压力数据。当用户询问压力、焦虑、紧张状态相关问题时，使用此 CLI 命令获取数据后再分析。"
metadata:
  {
    "pha": {
      "emoji": "🧠",
      "category": "health-data-cli",
      "tags": ["cli", "stress", "mental-health"],
      "requires": { "tools": ["get_stress"] }
    }
  }
---

# 压力数据 CLI 获取指南

## 命令示例

### 获取今日压力
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_stress --date today
```

### 获取指定日期压力
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_stress --date 2024-01-15
```

### 获取最近 7 天压力趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_stress --last-days 7
```

### 获取最近 30 天压力趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_stress --last-days 30
```

### 获取指定日期范围压力数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_stress --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `current` | 当前压力值（1–99） |
| `avg` | 当日平均压力 |
| `max` | 当日最高压力 |
| `min` | 当日最低压力 |
| `readings[]` | 全天各时段压力读数 |

## 压力等级参考

| 分值 | 等级 | 建议 |
|------|------|------|
| 1–29 | 放松 | 状态良好 |
| 30–59 | 正常 | 无需特别关注 |
| 60–79 | 中等压力 | 建议适当放松 |
| 80–99 | 高压力 | 建议及时缓解，注意休息 |
