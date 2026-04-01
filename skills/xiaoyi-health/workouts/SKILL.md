---
name: workouts-cli
description: "通过 CLI 获取用户运动记录。当用户询问运动、锻炼、跑步、游泳、健身等运动相关问题时，使用此 CLI 命令获取数据后再分析。"
metadata:
  {
    "pha": {
      "emoji": "🏃",
      "category": "health-data-cli",
      "tags": ["cli", "workouts", "exercise", "fitness"],
      "requires": { "tools": ["get_workouts"] }
    }
  }
---

# 运动数据 CLI 获取指南

## 命令示例

### 获取今日运动记录
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_workouts --date today
```

### 获取指定日期运动记录
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_workouts --date 2024-01-15
```

### 获取最近 7 天运动记录
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_workouts --last-days 7
```

### 获取最近 30 天运动记录
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_workouts --last-days 30
```

### 获取指定日期范围运动记录
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_workouts --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `type` | 运动类型（如跑步、游泳、骑行） |
| `durationMinutes` | 运动时长（分钟） |
| `caloriesBurned` | 消耗卡路里（千卡） |
| `distanceKm` | 运动距离（公里，部分运动有） |
| `avgHeartRate` | 平均心率（bpm） |
| `startTime` / `endTime` | 开始/结束时间 |
| `count` | 当日运动次数 |
