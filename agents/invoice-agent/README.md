# 发票处理 Agent 使用指南

这个目录包含了发票处理子 Agent 的完整配置，可以直接被 OpenClaw 使用来创建专门的发票处理 Agent。

## 📁 文件结构

```
invoice-agent/
├── SOUL.md                          # Agent 灵魂定义（行为规范和职责）
├── config.json                      # Agent 配置文件（技能、通信、存储）
├── skills/
│   └── invoice-processor/
│       └── SKILL.md                 # 发票处理技能定义
└── README.md                        # 本文件
```

## 📥 给 OpenClaw 的安装/升级指令

**复制以下指令发送给 OpenClaw 主系统**：

```
请帮我安装/升级发票处理智能体（invoice-agent）v3.0：

配置来源：/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/

功能说明：
- 专职发票识别、分类和归档处理
- 支持 PDF 和批量处理（最多 50 个文件）
- 自动归档到 archive/{年}/{月}/{类型}/ 目录
- 智能命名格式：YYYYMMDD_金额(分)_发票号码_类型简称_开票方简称

技能依赖：
1. paddleocr-vl（必需）- 本地技能，路径：/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
2. email（可选）- OpenClaw 主系统技能，用于邮箱监控

工作空间：~/.openclaw/workspace-invoice-agent/

请按照 agents/invoice-agent/config.json 进行完整配置。
```

---

## 🚀 快速开始

### 前置条件

1. **PaddleOCR-VL 服务已配置为 OpenClaw 技能**
   - 配置文件位于: `/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json`
   - 服务运行在: `http://localhost:8001`

2. **OpenClaw 已安装并运行**

### 方法 1：通过 OpenClaw CLI 创建 Agent

```bash
# 使用 OpenClaw CLI 创建发票处理 Agent
openclaw agent create \
  --name invoice-agent \
  --soul agents/invoice-agent/SOUL.md \
  --config agents/invoice-agent/config.json \
  --workspace ~/.openclaw/workspace-invoice-agent

# 启用技能
openclaw agent enable-skill \
  --agent invoice-agent \
  --skill paddleocr-vl \
  --source /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json

openclaw agent enable-skill \
  --agent invoice-agent \
  --skill invoice-processor \
  --source agents/invoice-agent/skills/invoice-processor/SKILL.md
```

### 方法 2：手动复制配置文件

```bash
# 1. 创建 Agent 工作空间
mkdir -p ~/.openclaw/workspace-invoice-agent/skills/invoice-processor

# 2. 复制 SOUL.md
cp agents/invoice-agent/SOUL.md ~/.openclaw/workspace-invoice-agent/

# 3. 复制技能文件
cp agents/invoice-agent/skills/invoice-processor/SKILL.md \
   ~/.openclaw/workspace-invoice-agent/skills/invoice-processor/

# 4. 在 OpenClaw 配置中注册 Agent
# 编辑 ~/.openclaw/agents.json，添加：
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "soul_path": "~/.openclaw/workspace-invoice-agent/SOUL.md",
  "skills": ["paddleocr-vl", "invoice-processor"]
}
```

### 方法 3：通过主 Agent 调用

如果主 Agent 需要调用发票处理 Agent：

```python
# 在主 Agent 的配置中添加
{
  "agent": {
    "id": "main-agent",
    "allowAgents": ["invoice-agent"]
  },
  "subagents": [
    {
      "id": "invoice-agent",
      "endpoint": "http://localhost:8002",
      "tasks": ["invoice_processing", "document_ocr"]
    }
  ]
}
```

## 💡 使用示例

### 示例 1：处理单张发票

```python
# 通过主 Agent 调用
result = main_agent.call_subagent(
    agent_id="invoice-agent",
    task="process_invoice",
    params={
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    }
)

# 结果
{
    "success": true,
    "filename": "invoice.png",
    "type": "vat_special",
    "type_name": "增值税专用发票",
    "fields": {
        "invoice_no": "12345678",
        "invoice_date": "2026-03-11",
        "buyer_name": "公司A",
        "seller_name": "公司B",
        "amount": "1000.00",
        "tax_amount": "130.00",
        "total_amount": "1130.00"
    },
    "confidence": 0.95
}
```

### 示例 2：批量处理发票

```python
result = main_agent.call_subagent(
    agent_id="invoice-agent",
    task="batch_process",
    params={
        "image_paths": [
            "/path/to/invoice1.png",
            "/path/to/invoice2.png",
            "/path/to/invoice3.png"
        ],
        "output_format": "csv",
        "merge_output": true
    }
)

# 结果
{
    "success": true,
    "processed": 3,
    "failed": 0,
    "output_file": "./invoices_output/2026-03-11_invoices.csv",
    "statistics": {
        "by_type": {
            "vat_special": 2,
            "vat_common": 1
        },
        "avg_confidence": 0.92
    }
}
```

### 示例 3：独立运行（不通过主 Agent）

```python
import sys
sys.path.append('/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent')

from invoice_agent import InvoiceAgent

# 创建 Agent 实例
agent = InvoiceAgent()
agent.load_config('config.json')

# 处理发票
result = agent.process_invoice({
    "image_path": "/path/to/invoice.png"
})

print(result)
```

## 🔧 配置说明

### config.json 关键配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `agent.id` | Agent 唯一标识 | invoice-agent |
| `agent.type` | Agent 类型（subagent） | subagent |
| `agent.mode` | 运行模式（standalone/managed） | standalone |
| `skills` | 可用技能列表 | [paddleocr-vl, invoice-processor] |
| `storage.output_dir` | 输出目录 | ./invoices_output |
| `processing.batch_size` | 批处理大小 | 10 |
| `processing.confidence_threshold` | 置信度阈值 | 0.7 |

### 技能配置

**paddleocr-vl**（OCR 服务技能）
- 来源: 本地 PaddleOCR-VL 项目
- 端点: http://localhost:8001
- 工具: recognize_document, batch_recognize, health_check

**invoice-processor**（发票处理技能）
- 来源: 本地技能文件
- 功能: 发票分类、字段提取、数据验证

## 📊 支持的发票类型

| 类型 | 代码 | 名称 | 关键字段 |
|------|------|------|----------|
| 增值税专用发票 | vat_special | 增值税专用发票 | 发票号码、日期、购买方、销售方、金额、税额、价税合计 |
| 增值税普通发票 | vat_common | 增值税普通发票 | 发票号码、日期、购买方、销售方、价税合计 |
| 电子发票 | electronic | 电子发票 | 发票号码、日期、购买方、销售方、价税合计、校验码 |
| 定额发票 | quota | 定额发票 | 发票代码、号码、金额、省份 |

## 🔍 监控和调试

### 查看日志
```bash
# Agent 日志位置
~/.openclaw/workspace-invoice-agent/logs/
```

### 健康检查
```bash
# 检查 OCR 服务
curl http://localhost:8001/health

# 检查 Agent API（如果启用）
curl http://localhost:8002/health
```

### 查看输出文件
```bash
# CSV 输出
ls -lh ./invoices_output/*.csv

# JSON 输出
ls -lh ./invoices_output/*.json
```

## ⚠️ 常见问题

### Q1: Agent 创建后无法使用 paddleocr-vl 技能

**A:** 检查技能路径是否正确：
```bash
# 验证配置文件存在
cat /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json

# 测试 OCR 服务
curl http://localhost:8001/health
```

### Q2: 发票识别结果为空

**A:** 可能原因：
1. OCR 服务未启动 → 启动服务
2. 图片质量差 → 使用高清图片
3. 图片格式不支持 → 转换为 PNG/JPEG

### Q3: 字段提取不准确

**A:** 可以：
1. 调整 `confidence_threshold` 阈值
2. 自定义字段提取规则（修改 SKILL.md）
3. 提供标准发票模板进行匹配

### Q4: 批量处理速度慢

**A:** 优化方案：
1. 减小 `batch_size`（每批处理数量）
2. 增加 `parallel_workers`（并发数）
3. 使用更快的模型（如 Haiku）

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| 单张识别速度 | ~1.2 秒 |
| 批量处理（10张） | ~12 秒 |
| 识别准确率 | 95%+（标准发票） |
| 字段提取准确率 | 90%+ |
| 内存占用 | ~3GB |

## 🔄 更新和维护

### 更新技能定义
```bash
# 编辑技能文件
vim agents/invoice-agent/skills/invoice-processor/SKILL.md

# 重新加载 Agent
openclaw agent reload --agent invoice-agent
```

### 更新配置
```bash
# 编辑配置文件
vim agents/invoice-agent/config.json

# 应用配置
openclaw agent apply-config --agent invoice-agent
```

## 📚 相关文档

- [PaddleOCR-VL 项目文档](../../README.md)
- [OpenClaw 集成指南](../../OPENCLAW_QUICKSTART.md)
- [发票处理技能详解](skills/invoice-processor/SKILL.md)

## 🤝 贡献

如需添加新的发票类型或优化字段提取规则，请：
1. 修改 `skills/invoice-processor/SKILL.md`
2. 更新 `config.json` 中的 `capabilities`
3. 提交 PR

---

**版本**: 1.0.0
**更新日期**: 2026-03-11
**维护者**: PaddleOCR-VL Integration Team
