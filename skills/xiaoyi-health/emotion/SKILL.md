---
name: emotion-cli
description: "通过 CLI 获取用户情绪数据。当用户询问情绪状态、心情、情绪波动相关问题时，使用此 CLI 命令获取数据后再分析。"
metadata:
  {
    "pha": {
      "emoji": "😊",
      "category": "health-data-cli",
      "tags": ["cli", "emotion", "mood", "mental-health"],
      "requires": { "tools": ["get_emotion"] }
    }
  }
---

# 情绪数据 CLI 获取指南

## 命令示例

### 获取今日情绪
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_emotion --date today
```

### 获取指定日期情绪数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_emotion --date 2024-01-15
```

### 获取最近 7 天情绪趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_emotion --last-days 7
```

### 获取最近 30 天情绪趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_emotion --last-days 30
```

### 获取指定日期范围情绪数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_emotion --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `current` | 当前情绪状态 |
| `score` | 情绪评分（越高越积极） |
| `avg` | 当日平均情绪评分 |
| `readings[]` | 全天各时段情绪记录 |

## 情绪等级参考

| 等级 | 说明 | 建议 |
|------|------|------|
| 非常好 | 情绪积极愉快 | 保持当前状态 |
| 良好 | 情绪平稳正常 | 无需特别关注 |
| 一般 | 情绪略有波动 | 适当放松调节 |
| 较差 | 情绪低落或焦虑 | 建议休息或倾诉 |
| 很差 | 情绪明显异常 | 建议关注心理健康 |
