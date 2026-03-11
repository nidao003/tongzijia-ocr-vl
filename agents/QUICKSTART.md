# 发票处理 Agent 快速开始

## 🚀 一键安装

```bash
# 进入项目目录
cd /Users/daodao/dsl/PaddleOCR-VL

# 运行安装脚本
./agents/install_invoice_agent.sh
```

安装脚本会自动：
- ✅ 创建 OpenClaw 工作空间
- ✅ 复制 SOUL.md 和配置文件
- ✅ 注册 invoice-agent
- ✅ 创建技能链接

## 📋 安装后的文件结构

```
~/.openclaw/
├── workspace-invoice-agent/          # Agent 工作空间
│   ├── SOUL.md                       # Agent 定义
│   ├── config.json                   # Agent 配置
│   ├── skills/
│   │   ├── paddleocr-vl/             # OCR 技能（链接）
│   │   └── invoice-processor/        # 发票处理技能
│   ├── logs/                         # 日志目录
│   └── output/                       # 临时输出
├── agents/
│   └── invoice-agent.json            # Agent 注册文件
```

## 💡 快速使用

### 步骤 1：启动 OCR 服务

```bash
cd /Users/daodao/dsl/PaddleOCR-VL
./start_services.sh
```

### 步骤 2：使用 Agent

#### 方式 A：通过主 Agent 调用

```python
# 在主 Agent 中调用
result = call_subagent(
    agent="invoice-agent",
    task="process_invoice",
    params={
        "image_path": "/path/to/invoice.png"
    }
)
```

#### 方式 B：独立运行

```python
# 直接使用发票处理功能
import sys
sys.path.append('/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent')

# 加载配置并处理
from invoice_agent import InvoiceAgent

agent = InvoiceAgent()
result = agent.process({
    "images": ["invoice1.png", "invoice2.png"],
    "output": "csv"
})
```

## 📊 支持的发票类型

- ✅ 增值税专用发票
- ✅ 增值税普通发票
- ✅ 电子发票
- ✅ 定额发票

## 📖 详细文档

- 完整使用指南: [README.md](invoice-agent/README.md)
- Agent 定义: [SOUL.md](invoice-agent/SOUL.md)
- 技能说明: [invoice-processor/SKILL.md](invoice-agent/skills/invoice-processor/SKILL.md)

## ⚠️ 故障排查

### 问题：Agent 无法找到 paddleocr-vl 技能

**解决**：
```bash
# 检查 PaddleOCR-VL 配置文件
cat /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json

# 测试 OCR 服务
curl http://localhost:8001/health
```

### 问题：安装失败

**解决**：
```bash
# 手动创建目录
mkdir -p ~/.openclaw/workspace-invoice-agent/skills

# 手动复制文件
cp agents/invoice-agent/SOUL.md ~/.openclaw/workspace-invoice-agent/
cp -r agents/invoice-agent/skills/* ~/.openclaw/workspace-invoice-agent/skills/
```

## 🎯 示例输出

处理后的发票数据会保存到 `~/invoices_output/`：

```csv
文件名,发票类型,发票号码,开票日期,购买方,销售方,金额,税额,价税合计,置信度
invoice1.png,增值税专用发票,12345678,2026-03-11,公司A,公司B,1000.00,130.00,1130.00,0.95
```

## 📞 获取帮助

查看详细文档或运行：
```bash
cat /Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/README.md
```
