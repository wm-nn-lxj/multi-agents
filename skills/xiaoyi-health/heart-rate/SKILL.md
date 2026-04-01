---
name: heart-rate-cli
description: "通过 CLI 获取用户心率数据。当用户询问心率、心跳、BPM 相关问题时，使用此 CLI 命令获取数据后再分析。静息心率请使用 resting-heart-rate-cli。"
metadata:
  {
    "pha": {
      "emoji": "💓",
      "category": "health-data-cli",
      "tags": ["cli", "heart-rate", "bpm"],
      "requires": { "tools": ["get_heart_rate"] }
    }
  }
---

# 心率数据 CLI 获取指南

## 命令示例

### 获取今日心率
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rate --date today
```

### 获取指定日期心率
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rate --date 2024-01-15
```

### 获取最近 7 天心率趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rate --last-days 7
```

### 获取最近 30 天心率趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rate --last-days 30
```

### 获取指定日期范围
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rate --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `avg` | 全天平均心率（bpm） |
| `maxToday` | 当日最高心率（bpm） |
| `minToday` | 当日最低心率（bpm） |
| `readings[]` | 各时段心率读数（时间 + bpm） |

## 参考范围（成人静息）

- **60–100 bpm**：正常范围
- **<60 bpm**：心动过缓（运动员可能正常）
- **>100 bpm**：心动过速，需关注

> 如需静息心率数据，请使用 `get_resting_heart_rate` 命令。
