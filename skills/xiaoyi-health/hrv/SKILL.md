---
name: hrv-cli
description: "通过 CLI 获取用户心率变异性（HRV）数据。当用户询问 HRV、心率变异性、自主神经恢复状态相关问题时，使用此 CLI 命令获取数据后再分析。"
metadata:
  {
    "pha": {
      "emoji": "📈",
      "category": "health-data-cli",
      "tags": ["cli", "hrv", "recovery", "autonomic"],
      "requires": { "tools": ["get_hrv"] }
    }
  }
---

# HRV 数据 CLI 获取指南

## 命令示例

### 获取今日 HRV
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_hrv --date today
```

### 获取指定日期 HRV
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_hrv --date 2024-01-15
```

### 获取最近 7 天 HRV 趋势（推荐，观察恢复规律）
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_hrv --last-days 7
```

### 获取最近 30 天 HRV 趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_hrv --last-days 30
```

### 获取指定日期范围 HRV 数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_hrv --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `rmssd` | 最新一次 HRV 值（ms，RMSSD 指标） |
| `avg` | 当日平均 HRV（ms） |
| `max` | 当日最高 HRV（ms） |
| `min` | 当日最低 HRV（ms） |
| `readings[]` | 全天各时段 HRV 读数 |

## 解读提示

- HRV 个体差异大，**趋势比绝对值更重要**
- 一般成人 RMSSD 在 20–100 ms 之间
- 连续低于个人基线 5 天以上，提示恢复不足或压力过大
