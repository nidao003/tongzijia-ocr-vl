# 🚀 OpenClaw 快速开始：创建和使用 invoice-agent

> **OpenClaw 主 Agent 请完整阅读本文档**

---

## 📋 任务概述

你需要创建一个名为 `invoice-agent`（发票处理专员）的子 Agent，它能：
- 识别和处理发票
- 提取详细字段（10-15个字段）
- 生成表格文件（CSV/JSON/Excel）
- 持续学习新的发票类型

**唯一依赖**：PaddleOCR-VL 技能

---

## ⚡ 5 步配置（必须按顺序执行）

### 步骤 1：创建工作空间

```bash
mkdir -p ~/.openclaw/workspace-invoice-agent/{skills/invoice-processor/learning,memory,logs}
```

### 步骤 2：复制核心文件

```bash
SRC="/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
DST="$HOME/.openclaw/workspace-invoice-agent"

# 复制配置
cp "$SRC/SOUL.md" "$DST/"
cp "$SRC/config_single_skill.json" "$DST/config.json"
cp "$SRC/skills/invoice-processor/SKILL.md" "$DST/skills/invoice-processor/"
```

### 步骤 3：初始化学习系统

```bash
python3 "$SRC/learning/init_learning_system.py"
```

**预期输出**：
```
✅ 已支持 4 种发票类型
✅ 学习系统已启用
```

### 步骤 4：创建技能引用

```bash
cat > "$DST/skills/paddleocr-vl/SKILL.md" << 'EOF'
---
name: paddleocr-vl
external: true
source: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
---
# PaddleOCR-VL OCR 服务
EOF
```

### 步骤 5：注册子 Agent

```bash
cat > ~/.openclaw/agents/invoice-agent.json << EOF
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "workspace": "$DST",
  "skills": ["paddleocr-vl"],
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
```

---

## ✅ 验证配置

### 检查文件结构

```bash
ls -l ~/.openclaw/workspace-invoice-agent/
```

**应该看到**：
```
SOUL.md
config.json
memory/
skills/
```

### 检查学习数据

```bash
jq '.total_types' ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json
```

**应该输出**：
```
4
```

---

## 🔧 配置 PaddleOCR-VL 技能

### 启动服务

```bash
cd /Users/daodao/dsl/PaddleOCR-VL
./start_services.sh
```

### 验证服务

```bash
curl http://localhost:8001/health
```

**应该输出**：
```json
{"status": "ok"}
```

---

## 📡 如何使用子 Agent

### 通讯方式：sessions_spawn

**使用 `sessions_spawn` 的 `run` 模式**调用子 Agent：

```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",                           # 一次性任务模式（推荐）
    task="process_invoice",               # 任务名称
    params={                              # 任务参数
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    },
    cwd="~/.openclaw/workspace-invoice-agent"  # 子 Agent 工作目录
)
```

**为什么使用 run 模式**：
- ✅ 独立进程处理任务
- ✅ 任务完成自动结束
- ✅ 资源自动释放
- ✅ 适合发票识别这种一次性工作

### 调用示例

#### 示例 1：处理单张发票

```python
result = sessions_spawn(
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

#### 示例 2：批量处理

```python
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="batch_process",
    params={
        "image_paths": [
            "/path/to/invoice1.png",
            "/path/to/invoice2.png"
        ],
        "output_format": "csv"
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)
```

#### 示例 3：学习新发票类型

```python
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="learn_new_type",
    params={
        "type_name": "机动车销售统一发票",
        "ocr_text": "发票识别的完整文本...",
        "field_examples": {...}
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)
```

### 返回结果

**成功**：
```json
{
  "success": true,
  "invoice_type": "vat_special",
  "fields": {
    "invoice_no": "12345678",
    "amount": "1000.00",
    ...
  },
  "output_file": "~/invoices_output/2026-03-11_invoices.csv"
}
```

**技能不可用**：
```json
{
  "report_type": "skill_unavailable",
  "skill_name": "paddleocr-vl",
  "action_required": "configure_skill",
  "message": "PaddleOCR-VL 技能未配置或服务未启动"
}
```

### 返回结果

**成功**：
```json
{
  "success": true,
  "invoice_type": "vat_special",
  "fields": {
    "invoice_no": "12345678",
    "amount": "1000.00"
  },
  "output_file": "~/invoices_output/2026-03-11_invoices.csv"
}
```

**技能不可用**：
```json
{
  "report_type": "skill_unavailable",
  "skill_name": "paddleocr-vl",
  "action_required": "configure_skill",
  "message": "PaddleOCR-VL 技能未配置或服务未启动"
}
```

---

## 🎯 何时使用子 Agent

### 决策流程

```
用户请求处理发票
  │
  ├─→ 1-2张，简单查看？
  │   └─→ 自己处理
  │
  ├─→ 3+张？
  │   └─→ 询问用户
  │
  ├─→ 需要详细字段？
  │   └─→ 询问用户
  │
  └─→ 需要表格文件？
      └─→ 必须用子 Agent
```

### 询问用户的话术

```
检测到您需要处理多张发票。

如何处理？
选项 1：使用"发票处理专员"处理（推荐）
  • 支持批量处理
  • 提取详细字段（发票号码、金额、税额等）
  • 生成表格文件

选项 2：由我直接处理
  • 快速查看基本信息

请选择 1 或 2：
```

**重要**：
- 总是使用子 Agent 的中文名称："**发票处理专员**"
- 说明子 Agent 的能力
- 让用户明确选择

---

## 📊 子 Agent 能力

### 初始能力

- ✅ 识别 4 种发票类型
  - 增值税专用发票
  - 增值税普通发票
  - 电子发票
  - 定额发票
- ✅ 提取 10-15 个详细字段
- ✅ 生成 CSV/JSON/Excel 表格

### 学习能力

- 🔄 自动学习新发票类型（3个样本）
- 🔄 优化字段提取规则（3次失败）
- 🔄 学习用户反馈

### 汇报能力

- 📊 任务完成汇报
- 📊 学习新内容汇报
- 📊 规则更新汇报
- 📊 性能指标汇报

---

## ⚠️ 重要提示

### 技能依赖

- invoice-agent **只依赖** PaddleOCR-VL 技能
- 如果技能不可用，会主动向你汇报
- 汇报包含配置指引

### 任务前检查

- 每次任务前会检查技能可用性
- 技能不可用时不执行任务
- 等待你配置技能后重试

---

## 🎉 完成后

配置完成后，你应该能够：

1. ✅ 识别发票任务
2. ✅ 向用户推荐使用子 Agent
3. ✅ 调用 invoice-agent
4. ✅ 接收处理结果
5. ✅ 接收学习汇报

---

## 🆘 遇到问题？

### 技能不可用

```bash
# 检查项目路径
ls -la /Users/daodao/dsl/PaddleOCR-VL

# 检查配置文件
cat /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json

# 启动服务
cd /Users/daodao/dsl/PaddleOCR-VL
./start_services.sh

# 验证服务
curl http://localhost:8001/health
```

### 配置问题

参考：`/Users/daodao/dsl/PaddleOCR-VL/agents/MAIN_AGENT_SETUP_GUIDE.md`

---

## 📚 需要更多信息？

如果需要更详细的说明，请阅读：

1. **MAIN_AGENT_SETUP_GUIDE.md** - 详细配置指南
2. **DECISION_GUIDE.md** - 决策机制详解
3. **DOCS_INDEX.md** - 文档索引

---

**配置完成后请告诉我**：
- [ ] 配置是否成功
- [ ] 验证是否通过
- [ ] 是否有问题

**版本**: 1.0.0
**文档**: OpenClaw 快速开始指南
**适用**: OpenClaw 主 Agent
