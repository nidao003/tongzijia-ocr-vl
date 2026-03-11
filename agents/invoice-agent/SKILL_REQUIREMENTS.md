# 技能检查和汇报机制

本文档说明 invoice-agent 如何检查 PaddleOCR-VL 技能的可用性，以及如何向主 Agent 汇报技能问题。

---

## 🔍 技能检查机制

### 每次任务前检查

```
收到任务
  ↓
检查 PaddleOCR-VL 技能
  ↓
┌─────────────────────────┐
│ 调用 health_check()      │
└────────┬────────────────┘
         │
    可用？
    ├─ 是 → 继续执行任务
    │
    └─ 否 → 向主 Agent 汇报
```

---

## ⚠️ 技能不可用的汇报

### 汇报场景 1：技能未配置

```json
{
  "report_type": "skill_unavailable",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "severity": "critical",
  "content": {
    "skill_name": "paddleocr-vl",
    "issue": "skill_not_configured",
    "description": "PaddleOCR-VL 技能未在主 Agent 中配置",
    "impact": {
      "affected_tasks": ["process_invoice", "batch_process", "classify_invoice", "learn_new_type"],
      "cannot_process": true,
      "alternative": null
    }
  },
  "action_required": {
    "type": "configure_skill",
    "urgency": "high",
    "instructions": {
      "step_1": "确认 PaddleOCR-VL 项目存在",
      "path": "/Users/daodao/dsl/PaddleOCR-VL",
      "step_2": "检查配置文件",
      "file": "/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json",
      "step_3": "配置技能到主 Agent",
      "config": {
        "skill_id": "paddleocr-vl",
        "source": "local",
        "config_path": "/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json"
      }
    }
  },
  "message": "❌ 无法执行任务：PaddleOCR-VL 技能未配置，请主 Agent 配置该技能"
}
```

### 汇报场景 2：服务未启动

```json
{
  "report_type": "skill_unavailable",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "severity": "critical",
  "content": {
    "skill_name": "paddleocr-vl",
    "issue": "service_not_running",
    "description": "PaddleOCR-VL 服务未启动或无法连接",
    "checked_endpoint": "http://localhost:8001/health",
    "error": "Connection refused",
    "impact": {
      "affected_tasks": ["all_invoice_tasks"],
      "cannot_process": true
    }
  },
  "action_required": {
    "type": "start_service",
    "urgency": "high",
    "instructions": {
      "step_1": "进入项目目录",
      "command": "cd /Users/daodao/dsl/PaddleOCR-VL",
      "step_2": "启动服务",
      "command": "./start_services.sh",
      "step_3": "验证服务",
      "command": "curl http://localhost:8001/health",
      "expected_output": "{\"status\": \"ok\"}"
    }
  },
  "message": "❌ 无法执行任务：PaddleOCR-VL 服务未启动，请启动服务"
}
```

### 汇报场景 3：配置文件缺失

```json
{
  "report_type": "skill_unavailable",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "severity": "critical",
  "content": {
    "skill_name": "paddleocr-vl",
    "issue": "config_file_missing",
    "description": "PaddleOCR-VL 配置文件不存在",
    "expected_path": "/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json",
    "impact": {
      "affected_tasks": ["all_invoice_tasks"],
      "cannot_process": true
    }
  },
  "action_required": {
    "type": "verify_installation",
    "urgency": "high",
    "instructions": {
      "step_1": "验证项目目录存在",
      "check": "ls -la /Users/daodao/dsl/PaddleOCR-VL",
      "step_2": "验证配置文件",
      "check": "cat /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json",
      "step_3": "如果配置文件缺失，需要重新配置 PaddleOCR-VL"
    }
  },
  "message": "❌ 无法执行任务：PaddleOCR-VL 配置文件缺失，请验证安装"
}
```

---

## ✅ 技能可用时

### 汇报技能状态（可选）

```json
{
  "report_type": "skill_status",
  "timestamp": "2026-03-11T23:30:00Z",
  "agent": "invoice-agent",
  "content": {
    "skill_name": "paddleocr-vl",
    "status": "available",
    "health_check": {
      "endpoint": "http://localhost:8001/health",
      "response": "{\"status\": \"ok\"}",
      "response_time": "50ms"
    },
    "capabilities": {
      "recognize_document": true,
      "batch_recognize": true,
      "supported_formats": ["PNG", "JPEG", "WebP"],
      "performance": "7秒/张"
    }
  },
  "message": "✅ PaddleOCR-VL 技能可用，准备执行任务"
}
```

---

## 🔧 主 Agent 的响应

### 配置技能

主 Agent 收到技能不可用的汇报后，应该：

```python
# 主 Agent 代码
if report["report_type"] == "skill_unavailable":
    skill_name = report["content"]["skill_name"]
    issue = report["content"]["issue"]

    if issue == "skill_not_configured":
        # 配置技能
        configure_skill(
            skill_id="paddleocr-vl",
            source="local",
            config_path="/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json",
            service_endpoint="http://localhost:8001"
        )

    elif issue == "service_not_running":
        # 启动服务
        start_service(
            working_dir="/Users/daodao/dsl/PaddleOCR-VL",
            command="./start_services.sh"
        )

    elif issue == "config_file_missing":
        # 通知用户需要安装/配置 PaddleOCR-VL
        notify_user("PaddleOCR-VL 配置文件缺失，请验证安装")

    # 技能配置完成后，通知子 Agent 重试任务
    notify_subagent("invoice-agent", "skill_configured", "retry_task")
```

---

## 📋 技能配置检查清单

主 Agent 应该确保：

- [ ] PaddleOCR-VL 项目目录存在
- [ ] 配置文件 `openclaw_config.json` 存在
- [ ] OCR 服务正在运行（http://localhost:8001）
- [ ] 子 Agent 已授权使用该技能
- [ ] 技能配置正确

---

## 🔄 完整流程

```
用户请求处理发票
  ↓
主 Agent 调用 invoice-agent
  ↓
invoice-agent 检查技能
  ↓
调用 health_check()
  ↓
┌──────────────────┐
│ 技能可用？        │
└────┬─────────┬───┘
     │         │
    是        否
     │         │
     │         ├─→ 向主 Agent 汇报技能不可用
     │         │   {
     │         │     "report_type": "skill_unavailable",
     │         │     "action_required": "configure_skill"
     │         │   }
     │         │
     │         ├─→ 主 Agent 配置技能
     │         │
     │         └─→ 通知 invoice-agent 重试
     │
     ├─→ 正常处理任务
     │   ├─→ OCR 识别
     │   ├─→ 提取字段
     │   └─→ 返回结果
     │
     └─→ 向主 Agent 汇报完成
```

---

## 📊 技能依赖声明

### invoice-agent 的技能依赖

```yaml
required_skills:
  paddleocr-vl:
    type: external_service
    required: true
    purpose: "OCR 文字识别"
    fallback: "report_to_parent"

internal_capabilities:
  - invoice_classification
  - field_extraction
  - data_formatting
  - continuous_learning
```

### 技能配置模板

主 Agent 需要配置的技能格式：

```json
{
  "skill_id": "paddleocr-vl",
  "skill_name": "PaddleOCR-VL OCR 服务",
  "type": "service",
  "source": "local",
  "config": {
    "project_path": "/Users/daodao/dsl/PaddleOCR-VL",
    "config_file": "/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json",
    "service_endpoint": "http://localhost:8001",
    "health_check": "/health"
  },
  "tools": ["recognize_document", "batch_recognize", "health_check"],
  "authorized_agents": ["invoice-agent"]
}
```

---

**技能依赖版本**: 1.0.0
**最后更新**: 2026-03-11
**关键原则**: 只依赖一个外部技能（PaddleOCR-VL），其他都是内置能力
