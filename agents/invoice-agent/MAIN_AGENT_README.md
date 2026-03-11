# 🤖 主 Agent 创建指令：发票处理专员

> **创建子 Agent 的完整指令包**

---

## 📦 内容概述

本指令包包含创建"发票处理专员"子 Agent 所需的所有文件和配置。

### 📁 源文件位置

```
/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/
├── SOUL.md                      # Agent 行为定义
├── config.json                  # Agent 配置
├── AGENT_CREATION.md            # 详细创建步骤（本文档）
└── learning/
    ├── init_learning_system.py  # 学习系统初始化脚本
    └── learning_engine.py       # 学习引擎实现
```

---

## ⚡ 快速创建（3 步）

### 1️⃣ 创建工作空间

```bash
mkdir -p ~/.openclaw/workspace-invoice-agent/skills/invoice-processor/learning
mkdir -p ~/.openclaw/workspace-invoice-agent/memory
mkdir -p ~/.openclaw/workspace-invoice-agent/logs
```

### 2️⃣ 复制核心文件

```bash
# 设置变量
SRC="/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
DST="$HOME/.openclaw/workspace-invoice-agent"

# 复制文件
cp "$SRC/SOUL.md" "$DST/"
cp "$SRC/config.json" "$DST/"
cp "$SRC/skills/invoice-processor/SKILL.md" "$DST/skills/invoice-processor/"
```

### 3️⃣ 初始化学习系统

```bash
python3 /Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/learning/init_learning_system.py
```

输出示例：
```
🧠 初始化发票处理 Agent 学习系统...
📁 工作空间: /Users/daodao/.openclaw/workspace-invoice-agent
✅ 初始化已知发票类型数据库...
   - 已支持 4 种发票类型
✅ 初始化提取规则配置...
   - 4 种提取策略已配置
✅ 初始化性能指标追踪...
   - 指标追踪已启用
✅ 初始化学习配置...
   - 自动学习已启用
   - 升级检查已配置（24小时间隔）
🎉 学习系统初始化完成！
```

---

## 🔗 配置技能

### 创建 PaddleOCR-VL 技能链接

```bash
cat > "$DST/skills/paddleocr-vl/SKILL.md" << 'EOF'
---
name: paddleocr-vl
external: true
source: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
---

# PaddleOCR-VL OCR 服务

高精度文档识别服务。

工具：recognize_document, batch_recognize, health_check
端点：http://localhost:8001
EOF
```

### 注册 Agent

```bash
cat > ~/.openclaw/agents/invoice-agent.json << EOF
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "workspace": "$HOME/.openclaw/workspace-invoice-agent",
  "skills": ["paddleocr-vl", "invoice-processor"],
  "auto_learning": true,
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
```

---

## 🧠 子 Agent 能力

### 初始能力
- ✅ 识别 4 种发票类型（专票、普票、电子、定额）
- ✅ 智能字段提取（15+ 字段）
- ✅ 批量处理（每批 10 张）
- ✅ 多格式输出（CSV/JSON/Excel）

### 学习能力
- 🔄 自动学习新发票类型（3 个样本触发）
- 🔄 优化字段提取规则（失败 3 次触发）
- 🔄 学习用户反馈
- 🔄 定期自我升级（24 小时检查）

### 通讯接口

```yaml
# 主 Agent → 子 Agent
endpoint: http://localhost:8002
actions:
  - POST /process          # 处理单张发票
  - POST /batch            # 批量处理
  - POST /classify         # 单独分类
  - POST /learn            # 主动教学
  - GET  /health           # 健康检查

# 子 Agent → 主 Agent
events:
  - task_completed         # 任务完成
  - new_type_learned       # 学习了新类型
  - rules_optimized        # 规则优化完成
```

---

## ✅ 验证清单

创建完成后验证：

```bash
# 1. 检查文件
ls -l ~/.openclaw/workspace-invoice-agent/
# 应包含：SOUL.md, config.json, memory/, skills/

# 2. 检查学习数据
cat ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json | jq '.total_types'
# 应输出：4

# 3. 检查技能
ls -l ~/.openclaw/workspace-invoice-agent/skills/
# 应包含：invoice-processor/, paddleocr-vl/
```

---

## 🚀 使用示例

### 通过主 Agent 调用

```python
# 处理单张发票
result = main_agent.call_subagent(
    agent_id="invoice-agent",
    action="process",
    params={
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    }
)

# 批量处理
result = main_agent.call_subagent(
    agent_id="invoice-agent",
    action="batch",
    params={
        "image_paths": [
            "/path/to/invoice1.png",
            "/path/to/invoice2.png"
        ],
        "output_format": "csv"
    }
)
```

### 教学新类型

```python
# 当遇到未知类型时，可以主动教学
result = main_agent.call_subagent(
    agent_id="invoice-agent",
    action="learn",
    params={
        "type_name": "机动车销售统一发票",
        "ocr_text": "...完整文本...",
        "fields": {
            "invoice_no": ["12345"],
            "vehicle_type": ["轿车"],
            "vin": ["LSV..."]
        }
    }
)
```

---

## 📊 预期输出

处理后的发票数据会保存到 `~/invoices_output/`：

```csv
filename,invoice_type,invoice_no,invoice_date,buyer,seller,amount,tax_amount,total,confidence
invoice1.png,增值税专用发票,12345678,2026-03-11,公司A,公司B,1000.00,130.00,1130.00,0.95
```

---

## 🔄 自我升级机制

子 Agent 会自动：

1. **每 24 小时检查更新**
   - 对比源码版本
   - 评估变更影响
   - 请求主 Agent 批准升级

2. **持续学习优化**
   - 新发票类型 → 自动添加到知识库
   - 字段提取失败 → 自动优化规则
   - 用户反馈 → 立即应用纠正

3. **性能追踪**
   - 记录处理统计
   - 计算准确率
   - 追踪学习进度

---

## 📖 详细文档

如需更多细节，查看：

- **完整创建步骤**: `AGENT_CREATION.md`
- **Agent 行为规范**: `SOUL.md`
- **技能定义**: `skills/invoice-processor/SKILL.md`
- **学习系统**: `learning/learning_engine.py`

---

## 🆘 故障排除

| 问题 | 解决方案 |
|------|----------|
| 初始化失败 | 检查 Python 是否安装 |
| 技能找不到 | 验证 PaddleOCR-VL 路径 |
| 无法学习 | 检查 memory 目录权限 |
| 通讯失败 | 检查端口 8002 是否可用 |

---

**版本**: 1.0.0
**创建日期**: 2026-03-11
**适用于**: OpenClaw 主 Agent

创建完成后，子 Agent 将具备：发票识别 + 持续学习 + 自我升级能力 🎉
