# 📡 通讯配置：sessions_spawn 调用方式

> **OpenClaw 主 Agent 与 invoice-agent 的通讯配置**

---

## 🔗 通讯方式

### 调用模式

使用 `sessions_spawn` 的 **run 模式**进行通讯：

```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",                    # 一次性任务模式
    task="识别这张发票...",       # 任务描述
    cwd="~/.openclaw/workspace-invoice-agent"  # 工作目录
)
```

---

## 📋 参数说明

### agentId

```python
agentId="invoice-agent"
```

**说明**：子 Agent 的唯一标识符

**可选值**：
- `"invoice-agent"` - 发票处理专员的 ID

---

### mode

```python
mode="run"
```

**说明**：运行模式

**可选值**：
- `"run"` - **推荐**：一次性任务，完成后自动结束
- `"session"` - 会话模式，保持连接（不推荐用于发票处理）

**为什么使用 run 模式**：
- ✅ 独立进程处理任务
- ✅ 任务完成自动结束
- ✅ 资源自动释放
- ✅ 适合发票识别这种一次性工作

---

### task

```python
task="识别这张发票..."
```

**说明**：任务描述，会传递给子 Agent

**支持的值**：

#### 任务 1：process_invoice（处理单张发票）

```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="process_invoice",
    params={
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)
```

#### 任务 2：batch_process（批量处理）

```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="batch_process",
    params={
        "image_paths": [
            "/path/to/invoice1.png",
            "/path/to/invoice2.png",
            "/path/to/invoice3.png"
        ],
        "output_format": "csv"
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)
```

#### 任务 3：classify_invoice（单独分类）

```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="classify_invoice",
    params={
        "image_path": "/path/to/invoice.png"
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)
```

#### 任务 4：learn_new_type（学习新类型）

```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="learn_new_type",
    params={
        "type_name": "机动车销售统一发票",
        "ocr_text": "发票OCR识别的完整文本...",
        "field_examples": {
            "invoice_no": ["12345"],
            "vehicle_type": ["轿车"]
        }
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)
```

---

### cwd

```python
cwd="~/.openclaw/workspace-invoice-agent"
```

**说明**：子 Agent 的工作目录

**必须指向**：
- `~/.openclaw/workspace-invoice-agent`（子 Agent 工作空间）

**重要**：这个目录包含：
- `SOUL.md` - Agent 定义
- `config.json` - Agent 配置
- `skills/` - 技能目录
- `memory/` - 学习数据
- `logs/` - 日志目录

---

## 🎯 完整调用示例

### 示例 1：处理单张发票

```python
# 主 Agent 代码
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="process_invoice",
    params={
        "image_path": "/Users/daodao/dsl/PaddleOCR-VL/test_image.png",
        "output_format": "json"
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)

# 返回结果
print(result)
# {
#   "success": true,
#   "invoice_type": "vat_special",
#   "fields": {...},
#   "output_file": "~/invoices_output/2026-03-11_invoices.csv"
# }
```

### 示例 2：批量处理

```python
# 用户提供发票
invoices = [
    "/path/to/invoice1.png",
    "/path/to/invoice2.png",
    "/path/to/invoice3.png"
]

# 调用子 Agent
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="batch_process",
    params={
        "image_paths": invoices,
        "output_format": "csv"
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)

# 返回结果
# {
#   "success": true,
#   "processed_count": 3,
#   "output_file": "~/invoices_output/2026-03-11_invoices.csv"
# }
```

### 示例 3：包含决策的完整流程

```python
# 主 Agent 的处理逻辑
def handle_invoice_request(user_message, invoice_images):
    # 1. 分析任务
    invoice_count = len(invoice_images)

    # 2. 决策
    if invoice_count >= 3:
        # 批量任务，推荐使用子 Agent
        user_choice = ask_user(
            f"检测到您需要处理{invoice_count}张发票。\n"
            "我建议使用我的子 Agent '发票处理专员' 处理，因为：\n"
            "  • 支持批量处理\n"
            "  • 提取详细字段\n"
            "  • 生成表格文件\n\n"
            "如何处理？\n"
            "选项 1：使用'发票处理专员'（推荐）\n"
            "选项 2：由我直接处理\n\n"
            "请选择 1 或 2："
        )

        if user_choice == "1":
            # 使用子 Agent
            result = sessions_spawn(
                agentId="invoice-agent",
                mode="run",
                task="batch_process",
                params={
                    "image_paths": invoice_images,
                    "output_format": "csv"
                },
                cwd="~/.openclaw/workspace-invoice-agent"
            )

            return {
                "message": "正在使用'发票处理专员'为您处理发票...",
                "result": result
            }
        else:
            # 主 Agent 自己处理
            return process_with_main_agent(invoice_images)

    else:
        # 简单任务，主 Agent 处理
        return process_with_main_agent(invoice_images)
```

---

## 🔄 通讯流程

### 完整流程

```
用户请求
  ↓
主 Agent 分析任务
  ↓
决定使用子 Agent
  ↓
调用 sessions_spawn
  ├─ agentId: "invoice-agent"
  ├─ mode: "run"
  ├─ task: "process_invoice"
  └─ cwd: "~/.openclaw/workspace-invoice-agent"
  ↓
子 Agent 启动（独立进程）
  ├─ 加载 SOUL.md
  ├─ 检查技能（paddleocr-vl）
  ├─ 执行任务
  │   ├─→ OCR 识别
  │   ├─→ 分类发票
  │   ├─→ 提取字段
  │   ├─→ 生成表格
  │   └─→ 如果是未知类型 → 学习
  └─→ 返回结果
  ↓
主 Agent 接收结果
  ↓
主 Agent 返回给用户
```

---

## ⚙️ 配置要求

### 主 Agent 需要配置的通讯方式

```json
{
  "agent": {
    "id": "main-agent",
    "name": "主 Agent"
  },
  "subagents": [
    {
      "agentId": "invoice-agent",
      "name": "发票处理专员",
      "workspace": "~/.openclaw/workspace-invoice-agent",
      "communication": {
        "method": "sessions_spawn",
        "default_mode": "run",
        "timeout": 300
      },
      "tasks": {
        "process_invoice": {
          "task": "process_invoice",
          "params": ["image_path", "output_format"]
        },
        "batch_process": {
          "task": "batch_process",
          "params": ["image_paths", "output_format"]
        },
        "classify_invoice": {
          "task": "classify_invoice",
          "params": ["image_path"]
        },
        "learn_new_type": {
          "task": "learn_new_type",
          "params": ["type_name", "ocr_text", "field_examples"]
        }
      }
    }
  ]
}
```

---

## 📊 返回结果格式

### 成功返回

```json
{
  "success": true,
  "task": "process_invoice",
  "agent": "invoice-agent",
  "result": {
    "filename": "invoice.png",
    "invoice_type": "vat_special",
    "invoice_type_name": "增值税专用发票",
    "confidence": 0.95,
    "fields": {
      "invoice_code": "1100XXXXXXXX",
      "invoice_no": "12345678",
      "invoice_date": "2026-03-11",
      "buyer_name": "北京科技有限公司",
      "seller_name": "上海贸易有限公司",
      "amount": "1000.00",
      "tax_amount": "130.00",
      "total_amount": "1130.00"
    },
    "output_file": "/Users/xxx/invoices_output/2026-03-11_invoices.csv",
    "processing_time": 7.2
  }
}
```

### 技能不可用返回

```json
{
  "success": false,
  "error": "skill_unavailable",
  "agent": "invoice-agent",
  "skill_name": "paddleocr-vl",
  "message": "PaddleOCR-VL 技能未配置或服务未启动",
  "action_required": "configure_skill",
  "instructions": {
    "step_1": "确认项目路径: /Users/daodao/dsl/PaddleOCR-VL",
    "step_2": "检查配置文件: openclaw_config.json",
    "step_3": "启动服务: ./start_services.sh",
    "step_4": "验证服务: curl http://localhost:8001/health"
  }
}
```

---

## 🎯 关键要点

### 为什么使用 run 模式

1. **独立进程**：子 Agent 在独立进程中运行
2. **自动结束**：任务完成后进程自动结束，释放资源
3. **一次性任务**：发票识别是典型的一次性任务
4. **资源高效**：不需要保持长连接

### cwd 参数的重要性

- **必须指向子 Agent 的工作空间**
- **包含所有必需文件**：SOUL.md、config.json、skills、memory
- **路径可以是相对路径**：`~/.openclaw/workspace-invoice-agent`

### timeout 设置

```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="batch_process",
    params={...},
    cwd="~/.openclaw/workspace-invoice-agent",
    timeout=300  # 5分钟超时
)
```

**建议超时时间**：
- 单张发票：60 秒
- 批量处理（3-10张）：300 秒（5 分钟）
- 学习任务：120 秒

---

## 🔍 调试技巧

### 检查子 Agent 是否正常

```python
# 健康检查
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="health_check",
    params={},
    cwd="~/.openclaw/workspace-invoice-agent"
)
```

### 查看子 Agent 日志

```bash
# 日志位置
tail -f ~/.openclaw/workspace-invoice-agent/logs/latest.log
```

---

## ✅ 配置完成检查清单

通讯配置完成后，确认：

- [ ] 子 Agent 已创建
- [ ] 工作空间路径正确
- [ ] SOUL.md 和 config.json 存在
- [ ] PaddleOCR-VL 技能已配置
- [ ] PaddleOCR-VL 服务正在运行
- [ ] 能够通过 sessions_spawn 调用
- [ ] 能够接收处理结果
- [ ] 能够接收技能不可用的汇报

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| **QUICKSTART_FOR_OPENCLAW.md** | 快速开始指南 |
| **DECISION_GUIDE.md** | 决策机制详解 |
| **MAIN_AGENT_SETUP_GUIDE.md** | 完整配置指南 |

---

**通讯配置版本**: 1.0.0
**最后更新**: 2026-03-11
**核心方法**: sessions_spawn(agentId="invoice-agent", mode="run")
