---
name: body-composition-cli
description: "通过 CLI 获取用户体成分数据（体重、BMI、体脂率等）。当用户询问体重、BMI、体脂、肌肉量相关问题时，使用此 CLI 命令获取数据后再分析。"
metadata:
  {
    "pha": {
      "emoji": "⚖️",
      "category": "health-data-cli",
      "tags": ["cli", "body-composition", "weight", "bmi"],
      "requires": { "tools": ["get_body_composition"] }
    }
  }
---

# 体成分数据 CLI 获取指南

## 命令示例

### 获取今日体成分
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_body_composition --date today
```

### 获取指定日期
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_body_composition --date 2024-01-15
```

### 获取最近 7 天体成分趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_body_composition --last-days 7
```

### 获取最近 30 天趋势（观察体重变化）
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_body_composition --last-days 30
```

### 获取指定日期范围体成分数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_body_composition --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `weight` | 体重（kg） |
| `height` | 身高（cm） |
| `bmi` | 体质指数 |
| `bodyFatPercent` | 体脂率（%） |
| `bodyScore` | 综合体成分评分 |

## BMI 参考范围

| 分类 | BMI |
|------|-----|
| 偏瘦 | <18.5 |
| 正常 | 18.5–23.9 |
| 超重 | 24.0–27.9 |
| 肥胖 | ≥28.0 |
