---
name: vo2max-cli
description: "通过 CLI 获取用户最大摄氧量（VO2Max）数据。当用户询问有氧能力、心肺功能、VO2Max 相关问题时，使用此 CLI 命令获取数据后再分析。"
metadata:
  {
    "pha": {
      "emoji": "🫀",
      "category": "health-data-cli",
      "tags": ["cli", "vo2max", "cardio", "fitness"],
      "requires": { "tools": ["get_vo2max"] }
    }
  }
---

# VO2Max 数据 CLI 获取指南

VO2Max（最大摄氧量）是衡量心肺功能和有氧运动能力的重要指标，数值越高代表有氧能力越强。

## 命令示例

### 获取今日 VO2Max
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_vo2max --date today
```

### 获取指定日期 VO2Max
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_vo2max --date 2024-01-15
```

### 获取最近 30 天 VO2Max 趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_vo2max --last-days 30
```

### 获取最近 90 天趋势（观察长期变化）
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_vo2max --last-days 90
```

### 获取指定日期范围 VO2Max 数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_vo2max --start-date 2024-01-01 --end-date 2024-03-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `value` | 当前 VO2Max 值（mL/kg/min） |
| `level` | 能力等级（较差/一般/良好/优秀/精英） |
| `trend` | 近期变化趋势 |

## 参考范围（成年男性，单位 mL/kg/min）

| 等级 | 20–29岁 | 30–39岁 | 40–49岁 |
|------|---------|---------|---------|
| 较差 | <38 | <34 | <30 |
| 一般 | 38–47 | 34–43 | 30–38 |
| 良好 | 48–56 | 44–52 | 39–47 |
| 优秀 | >56 | >52 | >47 |

> 女性参考值通常比同龄男性低约 10–15%。VO2Max 受年龄影响，随年龄增长自然下降。
