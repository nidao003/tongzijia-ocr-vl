# 🤖 主 Agent 使用指南

> **如何让主 Agent 使用 invoice-agent**

---

## 📋 前提条件

1. ✅ PaddleOCR-VL 服务已启动（http://localhost:8001）
2. ✅ 主 Agent 已安装并运行
3. ✅ 已执行创建流程（见 README.md）

---

## ⚡ 方法 1：让主 Agent 自动创建（推荐）

### 步骤 1：提供指令给主 Agent

将以下内容发送给主 Agent：

```
请阅读 /Users/daodao/dsl/PaddleOCR-VL/agents/README.md
然后按照文档中的步骤创建 invoice-agent 子 Agent
```

### 步骤 2：主 Agent 执行创建

主 Agent 会：
1. 阅读 README.md
2. 执行 bash 命令创建工作空间
3. 复制文件并初始化学习系统
4. 验证创建结果

### 步骤 3：验证创建

让主 Agent 执行验证命令：

```bash
# 验证文件结构
ls -l ~/.openclaw/workspace-invoice-agent/

# 验证学习数据
jq '.total_types' ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json

# 验证技能链接
ls -l ~/.openclaw/workspace-invoice-agent/skills/
```

---

## ⚡ 方法 2：手动创建后让主 Agent 使用

### 步骤 1：手动创建

```bash
# 执行测试脚本（自动完成所有步骤）
/Users/daodao/dsl/PaddleOCR-VL/agents/test_agent_creation.sh
```

### 步骤 2：通知主 Agent

告诉主 Agent：

```
invoice-agent 子 Agent 已创建完成
工作空间: ~/.openclaw/workspace-invoice-agent
能力: 发票识别、分类、字段提取、持续学习
通讯端口: 8002
```

---

## 📡 主 Agent 如何使用子 Agent

### 方式 1：通过 HTTP API 调用

```python
# 主 Agent 代码示例
import requests

# 处理单张发票
response = requests.post(
    "http://localhost:8002/process",
    json={
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    }
)
result = response.json()

# 批量处理
response = requests.post(
    "http://localhost:8002/batch",
    json={
        "image_paths": [
            "/path/to/invoice1.png",
            "/path/to/invoice2.png"
        ],
        "output_format": "csv"
    }
)
result = response.json()
```

### 方式 2：通过配置文件调用

主 Agent 的配置文件中添加：

```json
{
  "agent": {
    "id": "main-agent",
    "name": "主 Agent"
  },
  "subagents": [
    {
      "id": "invoice-agent",
      "name": "发票处理专员",
      "endpoint": "http://localhost:8002",
      "actions": {
        "process_invoice": "POST /process",
        "batch_process": "POST /batch",
        "classify_invoice": "POST /classify",
        "teach_invoice": "POST /learn",
        "health_check": "GET /health"
      }
    }
  ]
}
```

然后主 Agent 可以这样调用：

```python
# 主 Agent 代码
result = main_agent.call_subagent(
    agent_id="invoice-agent",
    action="process_invoice",
    params={
        "image_path": "/path/to/invoice.png"
    }
)
```

### 方式 3：通过命令行调用

```bash
# 处理单张发票
curl -X POST http://localhost:8002/process \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/invoice.png",
    "output_format": "json"
  }'

# 批量处理
curl -X POST http://localhost:8002/batch \
  -H "Content-Type: application/json" \
  -d '{
    "image_paths": ["/path/to/invoice1.png", "/path/to/invoice2.png"],
    "output_format": "csv"
  }'

# 健康检查
curl http://localhost:8002/health
```

---

## 🎯 使用场景示例

### 场景 1：用户要求处理发票

```
用户: "帮我处理这几张发票"

主 Agent 的处理流程:
1. 接收用户请求
2. 调用 invoice-agent 处理发票
3. 接收处理结果
4. 将结果返回给用户

伪代码:
invoices = get_invoice_paths()
result = call_subagent(
    "invoice-agent",
    "batch_process",
    {"image_paths": invoices, "output_format": "csv"}
)
return result["output_file"]
```

### 场景 2：子 Agent 学习新类型

```
invoice-agent: "主 Agent，我发现了一种新发票类型"
主 Agent: "请详细说明"
invoice-agent: {
  "type_name": "机动车销售统一发票",
  "confidence": 0.75,
  "sample_count": 3,
  "features": {...}
}
主 Agent: "批准，请学习并更新知识库"
invoice-agent: "✅ 已学习，现在支持 5 种发票类型"
```

### 场景 3：子 Agent 请求升级

```
invoice-agent: "主 Agent，检测到新版本可用"
主 Agent: "有什么更新？"
invoice-agent: {
  "version": "1.1.0",
  "changes": [
    "新增 2 种发票类型",
    "优化字段提取规则",
    "提升识别准确率"
  ]
}
主 Agent: "批准升级"
invoice-agent: "✅ 升级完成，学习数据已保留"
```

---

## 📊 返回结果格式

### 处理单张发票

```json
{
  "success": true,
  "filename": "invoice.png",
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
  "processing_time": 7.2
}
```

### 批量处理

```json
{
  "success": true,
  "processed_count": 5,
  "failed_count": 0,
  "output_file": "/Users/xxx/invoices_output/2026-03-11_invoices.csv",
  "statistics": {
    "by_type": {
      "vat_special": 2,
      "vat_common": 3
    },
    "avg_confidence": 0.92,
    "total_processing_time": 35.0
  },
  "invoices": [...]
}
```

---

## ⚠️ 注意事项

### 1. 通讯超时

```python
# 设置合理的超时时间
response = requests.post(
    "http://localhost:8002/process",
    json={...},
    timeout=60  # 单张发票 60 秒
)
```

### 2. 错误处理

```python
try:
    response = requests.post(...)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            # 处理成功
            pass
        else:
            # 处理失败，查看错误
            error = result.get("error")
    else:
        # HTTP 错误
        pass
except requests.Timeout:
    # 超时处理
    pass
```

### 3. 批量处理大小

```python
# 建议每批不超过 10 张
batch_size = 10
for i in range(0, len(invoices), batch_size):
    batch = invoices[i:i+batch_size]
    result = call_subagent("batch_process", {"image_paths": batch})
```

---

## 🧪 测试创建流程

### 运行测试脚本

```bash
# 测试整个创建流程
/Users/daodao/dsl/PaddleOCR-VL/agents/test_agent_creation.sh
```

测试脚本会：
1. ✅ 验证源文件存在
2. ✅ 创建工作空间
3. ✅ 复制核心文件
4. ✅ 初始化学习系统
5. ✅ 创建技能链接
6. ✅ 注册 Agent
7. ✅ 验证创建结果

---

## 📞 获取帮助

如果遇到问题：

1. **查看日志**: `~/.openclaw/workspace-invoice-agent/logs/`
2. **检查配置**: `~/.openclaw/workspace-invoice-agent/config.json`
3. **验证服务**: `curl http://localhost:8001/health`
4. **查看文档**: `/Users/daodao/dsl/PaddleOCR-VL/agents/`

---

**总结**：

1. **主 Agent 阅读 README.md** → 了解子 Agent
2. **执行创建命令** → 建立 workspace
3. **配置通讯** → 通过 API 或配置文件
4. **开始使用** → 处理发票、自动学习

🎉 创建完成后，子 Agent 会自动学习和优化！
