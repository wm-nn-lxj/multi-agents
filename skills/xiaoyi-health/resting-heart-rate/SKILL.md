---
name: resting-heart-rate-cli
description: "通过 CLI 获取用户静息心率数据。当用户明确询问静息心率、晨起心率时，使用此 CLI 命令获取数据后再分析。普通心率问题请使用 heart-rate-cli。"
metadata:
  {
    "pha": {
      "emoji": "❤️",
      "category": "health-data-cli",
      "tags": ["cli", "resting-heart-rate", "cardiovascular"],
      "requires": { "tools": ["get_resting_heart_rate"] }
    }
  }
---

# 静息心率 CLI 获取指南

静息心率是身体完全放松时的心率，是心血管健康的重要长期指标。

## 命令示例

### 获取今日静息心率
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_resting_heart_rate --date today
```

### 获取指定日期静息心率
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_resting_heart_rate --date 2024-01-15
```

### 获取最近 7 天静息心率趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_resting_heart_rate --last-days 7
```

### 获取最近 30 天趋势（观察长期心血管变化）
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_resting_heart_rate --last-days 30
```

### 获取指定日期范围静息心率数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_resting_heart_rate --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `avg` | 平均静息心率（bpm） |
| `max` | 当日最高静息心率（bpm） |
| `min` | 当日最低静息心率（bpm） |
| `readings[]` | 各时段静息心率读数 |

## 参考范围

- **60–80 bpm**：一般成人正常范围
- **<60 bpm**：运动员或心肺功能良好
- **>80 bpm**：偏高，长期如此建议关注
