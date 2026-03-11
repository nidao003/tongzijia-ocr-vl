# 子 Agent 向主 Agent 汇报机制

本文档详细说明 invoice-agent 如何向主 Agent 汇报学习和更新情况。

---

## 📡 汇报机制概览

子 Agent 必须**主动向主 Agent 汇报**以下事件：

| 事件类型 | 触发条件 | 汇报频率 | 重要性 |
|---------|---------|---------|--------|
| 任务完成 | 每次任务结束 | 每次 | ⭐⭐⭐ |
| 学习新内容 | 遇到未知类型 | 实时 | ⭐⭐⭐ |
| 规则更新 | 优化提取规则 | 实时 | ⭐⭐ |
| 性能变化 | 指标显著变化 | 实时 | ⭐⭐ |
| 升级可用 | 检查到新版本 | 24小时 | ⭐ |
| 学习摘要 | 每N次任务 | 每10次 | ⭐⭐ |

---

## 🎯 汇报格式详解

### 1. 任务完成汇报（必须）

**触发时机**：每次处理任务完成后

```json
{
  "report_type": "task_completed",
  "task_id": "task_20260311_233000",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "result": {
    "success": true,
    "task_type": "batch_process",
    "processed_count": 5,
    "success_count": 5,
    "failed_count": 0,
    "output_file": "/Users/xxx/invoices_output/2026-03-11_invoices.csv",
    "statistics": {
      "by_type": {
        "vat_special": 2,
        "vat_common": 3
      },
      "total_amount": 5230.00,
      "avg_confidence": 0.93,
      "processing_time": 35.2
    }
  },
  "learning_events": [],  // 本次任务中的学习事件
  "message": "已成功处理5张发票，生成CSV文件"
}
```

### 2. 学习新内容汇报（必须）

**触发时机**：学习了新的发票类型或模式时

```json
{
  "report_type": "new_content_learned",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "event": {
    "learned_type": "new_invoice_type",
    "details": {
      "type_id": "custom_1234567890",
      "type_name": "机动车销售统一发票",
      "confidence": 0.75,
      "sample_count": 3,
      "features": {
        "keywords": ["机动车", "销售统一发票", "车辆类型"],
        "layout": "special",
        "has_vin": true
      },
      "fields_learned": {
        "vin": {"pattern": r"[A-Z0-9]{17}", "examples": ["LSVAA123456789012"]},
        "vehicle_type": {"pattern": r"[\u4e00-\u9fa5]+", "examples": ["轿车", "SUV"]},
        "engine_no": {"pattern": r"[A-Z0-9]{8,12}"}
      },
      "triggered_by": "unknown_invoice_pattern",
      "trigger_file": "unknown_invoice_001.png"
    },
    "impact": {
      "known_types_before": 4,
      "known_types_after": 5,
      "total_types_now": 5,
      "affected_tasks": "future_classifications"
    },
    "validation": {
      "status": "pending",
      "min_samples_for_adoption": 5,
      "current_samples": 3,
      "confidence_threshold": 0.8,
      "current_confidence": 0.75
    },
    "message": "✅ 学习了新发票类型：机动车销售统一发票（3个样本，置信度75%）",
    "requires": "需要2个更多样本以达到稳定状态"
  }
}
```

### 3. 规则更新汇报

**触发时机**：优化了字段提取规则时

```json
{
  "report_type": "rules_updated",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "event": {
    "update_type": "field_extraction_optimization",
    "details": {
      "invoice_type": "vat_special",
      "field_name": "invoice_no",
      "change_description": "优化发票号码提取正则表达式",
      "before": {
        "pattern": "发票号码[：:]\\s*(\\d+)",
        "accuracy": 0.85,
        "failure_count": 15
      },
      "after": {
        "pattern": "发票号码[：:]\\s*(\\d{8})",
        "accuracy": 0.90,
        "expected_improvement": "+5%"
      },
      "triggered_by": "field_extraction_failure",
      "failure_samples": 5,
      "learning_source": "user_feedback"
    },
    "impact": {
      "affected_field": "invoice_no",
      "affected_types": ["vat_special", "vat_common"],
      "expected_improvement": "发票号码提取准确率从85%提升到90%"
    },
    "message": "✅ 优化了发票号码字段提取规则（基于5个失败样本）"
  }
}
```

### 4. 性能指标变化汇报

**触发时机**：性能指标有显著变化（>3%）时

```json
{
  "report_type": "performance_update",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "event": {
    "period": "last_24_hours",
    "before": {
      "success_rate": 0.85,
      "avg_confidence": 0.88,
      "known_types": 4,
      "total_processed": 50
    },
    "after": {
      "success_rate": 0.92,
      "avg_confidence": 0.91,
      "known_types": 5,
      "total_processed": 80
    },
    "changes": {
      "success_rate_change": "+7%",
      "avg_confidence_change": "+3%",
      "new_types_learned": 1,
      "rules_refined": 2,
      "tasks_delta": "+30"
    },
    "highlights": [
      "成功率提升7%（85% → 92%）",
      "平均置信度提升3%（88% → 91%）",
      "学习了1种新发票类型：机动车销售统一发票",
      "优化了2个字段的提取规则"
    ],
    "message": "📈 过去24小时性能显著提升：成功率+7%，置信度+3%"
  }
}
```

### 5. 升级可用汇报

**触发时机**：检查到新版本时（每24小时）

```json
{
  "report_type": "upgrade_available",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "event": {
    "current_version": "1.0.0",
    "available_version": "1.1.0",
    "changes": [
      "新增2种发票类型：机动车销售发票、二手车销售发票",
      "优化字段提取算法，准确率提升5%",
      "新增发票图像预处理功能",
      "修复已知的3个问题"
    ],
    "impact_assessment": {
      "preserves_learning_data": true,
      "requires_retraining": false,
      "backwards_compatible": true,
      "estimated_upgrade_time": "2分钟",
      "risk_level": "low"
    },
    "upgrade_details": {
      "file_changes": [
        "SOUL.md (更新)",
        "skills/invoice-processor/SKILL.md (新增字段)",
        "memory/known_invoices.json (保留+新增)"
      ]
    },
    "action_required": "approval",
    "message": "🔄 检测到新版本 1.1.0，请主Agent批准升级",
    "recommendation": "建议升级，新版本性能更好且保留所有学习数据"
  }
}
```

### 6. 定期学习摘要汇报

**触发时机**：每完成10次任务后

```json
{
  "report_type": "learning_summary",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "period": {
    "type": "tasks_completed",
    "count": 10,
    "start_time": "2026-03-11T20:00:00Z",
    "end_time": "2026-03-11T23:30:00Z"
  },
  "summary": {
    "tasks_processed": 10,
    "invoices_processed": 45,
    "success_rate": 0.93,
    "avg_confidence": 0.91,
    "learning_activities": {
      "new_types_learned": 1,
      "rules_refined": 3,
      "user_feedback_incorporated": 2
    },
    "highlights": [
      "✅ 学习了新类型：机动车销售统一发票",
      "✅ 优化了3个字段的提取规则（发票号码、金额、日期）",
      "✅ 应用了2条用户反馈",
      "✅ 整体准确率提升4.2%"
    ],
    "current_capabilities": {
      "supported_types": [
        "vat_special",
        "vat_common",
        "electronic",
        "quota",
        "custom_1234567890"
      ],
      "total_types": 5,
      "total_fields_configured": 52,
      "avg_confidence": 0.91,
      "success_rate": 0.93
    },
    "learning_progress": {
      "total_learned_items": 4,
      "accuracy_trend": "improving",
      "next_milestone": "达到98%准确率"
    },
    "message": "📊 过去10次任务学习摘要：学习了1种新类型，优化了3条规则，准确率提升4.2%"
  }
}
```

---

## 🔄 汇报流程

### 自动汇报流程

```
子 Agent 执行任务
    ↓
┌─────────────────────────────────┐
│ 检查汇报触发条件                 │
├─────────────────────────────────┤
│ • 任务完成？                    │ → 是 → 发送任务完成汇报
│ • 学习了新内容？                │ → 是 → 发送学习汇报
│ • 更新了规则？                  │ → 是 → 发送更新汇报
│ • 性能显著变化？                │ → 是 → 发送性能汇报
│ • 检查到升级？                  │ → 是 → 发送升级汇报
│ • 完成10次任务？                │ → 是 → 发送学习摘要
└─────────────────────────────────┘
    ↓
汇总所有汇报事件
    ↓
向主 Agent 发送
    ↓
等待主 Agent 确认（如需要）
```

### 汇报内容组织

单次汇报可能包含多个事件：

```json
{
  "report_batch": [
    {
      "report_type": "task_completed",
      "result": {...}
    },
    {
      "report_type": "new_content_learned",
      "event": {...}
    },
    {
      "report_type": "rules_updated",
      "event": {...}
    }
  ],
  "summary": {
    "total_events": 3,
    "importance": "high",
    "requires_attention": true
  }
}
```

---

## 📊 汇报数据存储

所有汇报都记录在日志中：

```bash
# 汇报日志位置
~/.openclaw/workspace-invoice-agent/logs/reports/

# 查看最近汇报
tail -f ~/.openclaw/workspace-invoice-agent/logs/reports/latest.log
```

---

## ✅ 汇报质量标准

### 必须包含的信息

每次汇报必须包含：

1. **timestamp** - 时间戳
2. **agent** - 发送者（invoice-agent）
3. **report_type** - 汇报类型
4. **message** - 人类可读的消息

### 可选但推荐的信息

1. **event_id** - 事件唯一ID
2. **impact** - 影响评估
3. **action_required** - 是否需要主Agent采取行动
4. **confidence** - 置信度（如适用）

---

## 🎯 示例：完整汇报流程

### 场景：处理一批发票，其中包含新类型

```
1. 子 Agent 开始处理
2. 识别到5张发票
3. 其中1张是未知类型（机动车销售发票）
4. 触发学习流程
5. 学习完成
6. 所有发票处理完成
7. 向主 Agent 发送汇报
```

### 发送的汇报

```json
{
  "report_batch": [
    {
      "report_type": "new_content_learned",
      "timestamp": "2026-03-11T23:28:00Z",
      "event": {
        "learned_type": "new_invoice_type",
        "details": {
          "type_name": "机动车销售统一发票",
          "sample_count": 1
        },
        "message": "✅ 学习了新发票类型：机动车销售统一发票"
      }
    },
    {
      "report_type": "task_completed",
      "timestamp": "2026-03-11T23:30:00Z",
      "result": {
        "processed_count": 5,
        "success_count": 5,
        "output_file": "/path/to/output.csv"
      },
      "message": "已成功处理5张发票（包含1种新类型）"
    }
  ],
  "summary": {
    "total_events": 2,
    "importance": "high",
    "requires_attention": false,
    "message": "处理完成并学习了新发票类型"
  }
}
```

---

## 📞 主 Agent 如何响应

### 接收汇报后的处理

```python
# 主 Agent 接收汇报
report = receive_report_from_subagent("invoice-agent")

# 根据汇报类型处理
if report["report_type"] == "new_content_learned":
    # 记录学习内容
    log_learning_event(report["event"])

    # 如果需要验证
    if report["event"].get("validation", {}).get("status") == "pending":
        # 可能需要人工确认
        notify_user(f"子Agent学习了新类型：{report['event']['details']['type_name']}")

elif report["report_type"] == "upgrade_available":
    # 评估升级
    if report["event"]["impact_assessment"]["risk_level"] == "low":
        # 自动批准
        approve_upgrade("invoice-agent")
    else:
        # 需要人工确认
        notify_user("子Agent请求升级，需要确认")

elif report["report_type"] == "task_completed":
    # 记录结果
    log_task_result(report["result"])
```

---

**汇报机制版本**: 1.0.0
**最后更新**: 2026-03-11
**适用于**: invoice-agent → main-agent 通讯
