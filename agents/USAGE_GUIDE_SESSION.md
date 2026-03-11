# 📖 invoice-agent 使用指南（sessions_spawn 方式）

> **基于 OpenClaw sessions_spawn 的正确使用方式**

---

## 🎯 核心概念

OpenClaw 的 Agent 间通讯**不使用 HTTP API**，而是使用 **`sessions_spawn`** 调用。

### 架构对比

```
❌ 错误理解（HTTP 方式）:
主 Agent --HTTP--> 子 Agent API
     ↓
  需要启动 HTTP 服务

✅ 正确方式（session 方式）:
主 Agent --sessions_spawn--> 子 Agent Session
     ↓
  子 Agent 以 session 方式运行，完成后返回结果
```

---

## 📡 调用方式

### 基本调用格式

```python
# 主 Agent 代码
result = sessions_spawn(
    agent="invoice-agent",      # 子 Agent ID
    task="process_invoice",     # 任务名称
    params={                    # 参数
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    }
)
```

### 支持的任务

| 任务名称 | 说明 | 参数 |
|---------|------|------|
| `process_invoice` | 处理单张发票 | `image_path`, `output_format` |
| `batch_process` | 批量处理发票 | `image_paths`, `output_format` |
| `classify_invoice` | 单独分类发票 | `image_path` |
| `learn_new_type` | 学习新类型 | `type_name`, `ocr_text`, `field_examples` |

---

## 💡 使用示例

### 示例 1：处理单张发票

```python
# 用户请求
user_input = "帮我处理这张发票：/path/to/invoice.png"

# 主 Agent 处理
result = sessions_spawn(
    agent="invoice-agent",
    task="process_invoice",
    params={
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    }
)

# 返回结果
# {
#   "success": true,
#   "invoice_type": "vat_special",
#   "fields": {
#     "invoice_no": "12345678",
#     "amount": "1000.00",
#     ...
#   }
# }
```

### 示例 2：批量处理

```python
# 用户请求
user_input = "处理这几张发票：inv1.png, inv2.png, inv3.png"

# 主 Agent 处理
result = sessions_spawn(
    agent="invoice-agent",
    task="batch_process",
    params={
        "image_paths": [
            "/path/to/inv1.png",
            "/path/to/inv2.png",
            "/path/to/inv3.png"
        ],
        "output_format": "csv"
    }
)

# 返回结果
# {
#   "success": true,
#   "processed_count": 3,
#   "output_file": "~/invoices_output/2026-03-11_invoices.csv"
# }
```

### 示例 3：遇到新类型，主动教学

```python
# 子 Agent 发现新类型，通知主 Agent
# invoice-agent: "主 Agent，我发现了一种未知发票类型"

# 主 Agent 可以主动教学
result = sessions_spawn(
    agent="invoice-agent",
    task="learn_new_type",
    params={
        "type_name": "机动车销售统一发票",
        "ocr_text": "发票OCR识别的完整文本...",
        "field_examples": {
            "invoice_no": ["12345"],
            "vehicle_type": ["轿车"],
            "vin": ["LSVAA123456789"]
        }
    }
)

# 返回结果
# {
#   "success": true,
#   "type_id": "custom_12345",
#   "message": "已学习新类型：机动车销售统一发票"
# }
```

---

## 🔄 完整工作流程

```
用户请求
    ↓
主 Agent 接收
    ↓
解析任务
    ↓
调用子 Agent
    ↓
sessions_spawn(
    agent="invoice-agent",
    task="process_invoice",
    params={...}
)
    ↓
子 Agent 执行
    ├─→ 1. 调用 PaddleOCR-VL（OCR 服务）
    ├─→ 2. 分类发票类型
    ├─→ 3. 提取字段
    ├─→ 4. 如果未知类型 → 触发学习
    ├─→ 5. 生成输出文件
    └─→ 6. 返回结果
    ↓
主 Agent 接收结果
    ↓
返回给用户
```

---

## 📊 返回结果格式

### 处理单张发票

```json
{
  "success": true,
  "task_id": "task_12345",
  "invoice_type": "vat_special",
  "invoice_type_name": "增值税专用发票",
  "confidence": 0.95,
  "fields": {
    "invoice_code": "1100XXXXXXXX",
    "invoice_no": "12345678",
    "invoice_date": "2026-03-11",
    "buyer_name": "公司A",
    "seller_name": "公司B",
    "amount": "1000.00",
    "tax_amount": "130.00",
    "total_amount": "1130.00"
  },
  "validation": {
    "valid": true,
    "missing_fields": []
  },
  "processing_time": 7.2,
  "output_file": null
}
```

### 批量处理

```json
{
  "success": true,
  "task_id": "task_12346",
  "processed_count": 3,
  "failed_count": 0,
  "output_file": "/Users/xxx/invoices_output/2026-03-11_invoices.csv",
  "statistics": {
    "by_type": {
      "vat_special": 1,
      "vat_common": 2
    },
    "avg_confidence": 0.92
  },
  "invoices": [
    {
      "filename": "inv1.png",
      "type": "vat_special",
      "confidence": 0.95
    },
    {
      "filename": "inv2.png",
      "type": "vat_common",
      "confidence": 0.90
    },
    {
      "filename": "inv3.png",
      "type": "vat_common",
      "confidence": 0.91
    }
  ]
}
```

---

## 🧠 学习功能

### 自动学习

子 Agent 会自动：
- 遇到未知类型时触发学习（3 个样本）
- 字段提取失败时优化规则（3 次失败）
- 定期检查更新（24 小时）

### 主 Agent 可以主动触发学习

```python
# 用户纠正：这个发票分类错了
user_input = "这个不是增值税专用发票，是机动车销售发票"

# 主 Agent 可以主动教学
result = sessions_spawn(
    agent="invoice-agent",
    task="learn_new_type",
    params={
        "type_name": "机动车销售统一发票",
        "ocr_text": user_provided_text,
        "field_examples": {...}
    }
)
```

---

## ⚙️ 子 Agent 的 Session 行为

### 启动

```python
# 主 Agent 调用 sessions_spawn
# OpenClaw 自动：
# 1. 加载 invoice-agent 的 SOUL.md
# 2. 加载技能（paddleocr-vl, invoice-processor）
# 3. 创建 session
# 4. 执行任务
# 5. 返回结果
# 6. 清理 session
```

### 超时处理

```json
{
  "communication": {
    "session_timeout": 300  // 5 分钟
  }
}
```

如果任务超时，session 会自动终止。

---

## 🔍 调试和日志

### 查看子 Agent 日志

```bash
# 日志位置
~/.openclaw/workspace-invoice-agent/logs/

# 查看最新日志
tail -f ~/.openclaw/workspace-invoice-agent/logs/latest.log
```

### 查看学习数据

```bash
# 查看已学习的发票类型
cat ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json | jq .

# 查看性能指标
cat ~/.openclaw/workspace-invoice-agent/memory/performance_metrics.json | jq .
```

---

## ✅ 验证清单

子 Agent 创建完成后：

- [x] 文件结构完整（SOUL.md, config.json, memory/, skills/）
- [x] 支持 4 种初始发票类型
- [x] 学习系统已初始化
- [x] 可以通过 sessions_spawn 调用
- [x] PaddleOCR-VL 服务可访问（http://localhost:8001）

---

## 🎯 快速测试

### 测试 1：简单调用

```python
# 主 Agent 测试代码
result = sessions_spawn(
    agent="invoice-agent",
    task="process_invoice",
    params={
        "image_path": "/Users/daodao/dsl/PaddleOCR-VL/test_image.png"
    }
)
print(result)
```

### 测试 2：批量处理

```python
# 批量测试
invoices = [
    "/path/to/invoice1.png",
    "/path/to/invoice2.png"
]

result = sessions_spawn(
    agent="invoice-agent",
    task="batch_process",
    params={
        "image_paths": invoices,
        "output_format": "json"
    }
)
print(result)
```

---

## 📞 常见问题

**Q: 如何知道子 Agent 是否正常工作？**
A: 调用简单任务，查看返回结果。如果返回 `{"success": true}` 说明正常。

**Q: 子 Agent 学习了新类型，主 Agent 怎么知道？**
A: 子 Agent 会在返回结果中包含 `new_type_learned` 字段，或者在 session 中通知。

**Q: 如何重置子 Agent 的学习数据？**
A: 删除 `memory/` 目录下的 JSON 文件，重新运行初始化脚本。

---

**总结**：

✅ 使用 `sessions_spawn` 调用
✅ 不需要 HTTP 服务
✅ 子 Agent 以 session 方式运行
✅ 支持自动学习和优化

🎉 现在可以正常使用了！
