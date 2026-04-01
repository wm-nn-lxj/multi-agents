---
name: naps-cli
description: "通过 CLI 获取用户小睡/午休数据。当用户询问午睡、小睡、短暂休息相关问题时，使用此 CLI 命令获取数据后再分析。普通夜间睡眠请使用 sleep-cli。"
metadata:
  {
    "pha": {
      "emoji": "😴",
      "category": "health-data-cli",
      "tags": ["cli", "naps", "sleep", "rest"],
      "requires": { "tools": ["get_naps"] }
    }
  }
---

# 小睡数据 CLI 获取指南

小睡数据记录白天短暂睡眠（午睡、小憩）情况，与夜间睡眠数据分开记录。

## 命令示例

### 获取今日小睡记录
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_naps --date today
```

### 获取指定日期小睡记录
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_naps --date 2024-01-15
```

### 获取最近 7 天小睡趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_naps --last-days 7
```

### 获取最近 30 天小睡趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_naps --last-days 30
```

### 获取指定日期范围小睡数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_naps --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `count` | 当日小睡次数 |
| `totalMinutes` | 当日小睡总时长（分钟） |
| `naps[]` | 各次小睡记录 |
| `naps[].startTime` | 小睡开始时间 |
| `naps[].durationMinutes` | 小睡时长（分钟） |

## 小睡时长参考

| 时长 | 效果 |
|------|------|
| 10–20 分钟 | 短暂恢复精力，不影响夜间睡眠（推荐） |
| 30 分钟 | 可能产生睡眠惰性（醒后短暂迷糊） |
| 60–90 分钟 | 深度休息，但可能影响夜间入睡 |
