---
name: heart-rhythm-cli
description: "通过 CLI 获取用户心律数据。当用户询问心律、心律不齐、心房颤动、房颤相关问题时，使用此 CLI 命令获取数据后再分析。"
metadata:
  {
    "pha": {
      "emoji": "💗",
      "category": "health-data-cli",
      "tags": ["cli", "heart-rhythm", "arrhythmia", "afib"],
      "requires": { "tools": ["get_heart_rhythm"] }
    }
  }
---

# 心律数据 CLI 获取指南

心律数据记录心跳节律是否规则，可用于检测心律不齐等异常情况。

## 命令示例

### 获取今日心律数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rhythm --date today
```

### 获取指定日期心律数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rhythm --date 2024-01-15
```

### 获取最近 7 天心律趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rhythm --last-days 7
```

### 获取最近 30 天心律趋势
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rhythm --last-days 30
```

### 获取指定日期范围心律数据
```bash
node ./skills/xiaoyi-health/bin/pha-claw.js get_heart_rhythm --start-date 2024-01-01 --end-date 2024-01-31
```

## 返回字段说明

| 字段 | 说明 |
|------|------|
| `status` | 心律状态（正常/异常） |
| `afibDetected` | 是否检测到房颤 |
| `readings[]` | 各时段心律检测记录 |
| `abnormalCount` | 当日异常次数 |

## 注意事项

- 心律异常（尤其是房颤）可能增加脑卒中风险，建议及时就医确认
- 可穿戴设备检测仅供参考，不能替代专业医疗诊断
