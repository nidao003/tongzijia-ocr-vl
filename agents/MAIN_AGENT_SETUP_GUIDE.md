# 🤖 OpenClaw 主 Agent 配置指南

> **主 Agent 请阅读本文档来配置 invoice-agent 子 Agent**

---

## 📋 配置目标

配置一个名为 `invoice-agent` 的子 Agent，它能：
- 识别和处理发票
- 提取详细的字段信息
- 生成表格文件（CSV/JSON）
- 持续学习新的发票类型

---

## ⚙️ 配置步骤

### 第 1 步：创建工作空间

```bash
mkdir -p ~/.openclaw/workspace-invoice-agent/{skills/invoice-processor/learning,memory,logs}
```

### 第 2 步：复制核心文件

```bash
SRC="/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
DST="$HOME/.openclaw/workspace-invoice-agent"

# 复制配置文件
cp "$SRC/SOUL.md" "$DST/"
cp "$SRC/config_single_skill.json" "$DST/config.json"
cp "$SRC/skills/invoice-processor/SKILL.md" "$DST/skills/invoice-processor/"
```

### 第 3 步：初始化学习系统

```bash
python3 "$SRC/learning/init_learning_system.py"
```

预期输出：
```
🧠 初始化发票处理 Agent 学习系统...
✅ 初始化已知发票类型数据库...
   - 已支持 4 种发票类型
✅ 初始化提取规则配置...
✅ 初始化性能指标追踪...
✅ 初始化学习配置...
🎉 学习系统初始化完成！
```

### 第 4 步：配置 PaddleOCR-VL 技能引用

```bash
cat > "$DST/skills/paddleocr-vl/SKILL.md" << 'EOF'
---
name: paddleocr-vl
external: true
source: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
---

# PaddleOCR-VL OCR 服务

这是 invoice-agent 唯一依赖的外部技能。

## 配置

- 项目路径: /Users/daodao/dsl/PaddleOCR-VL
- 配置文件: openclaw_config.json
- 服务端点: http://localhost:8001

## 工具

- `recognize_document(image_path)` - 识别单张图片
- `batch_recognize(image_paths)` - 批量识别
- `health_check()` - 健康检查
EOF
```

### 第 5 步：注册子 Agent

```bash
cat > ~/.openclaw/agents/invoice-agent.json << EOF
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "workspace": "$DST",
  "skills": ["paddleocr-vl"],
  "skill_dependencies": ["paddleocr-vl"],
  "requires_skill": "paddleocr-vl",
  "auto_learning": true,
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
```

---

## ✅ 验证配置

### 验证文件结构

```bash
ls -l ~/.openclaw/workspace-invoice-agent/
```

预期输出：
```
SOUL.md
config.json
memory/
skills/
  ├── invoice-processor/
  │   └── SKILL.md
  └── paddleocr-vl/
      └── SKILL.md
```

### 验证学习数据

```bash
jq '.total_types' ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json
```

预期输出：
```
4
```

### 验证技能配置

```bash
cat ~/.openclaw/workspace-invoice-agent/config.json | jq '.skills | length'
```

预期输出：
```
1
```

---

## 🔧 配置 PaddleOCR-VL 技能

### 配置技能到主 Agent

```bash
# 在你的配置中添加
{
  "skills": [
    {
      "id": "paddleocr-vl",
      "name": "PaddleOCR-VL OCR 服务",
      "type": "service",
      "source": "local",
      "config": {
        "project_path": "/Users/daodao/dsl/PaddleOCR-VL",
        "config_file": "/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json",
        "service_endpoint": "http://localhost:8001",
        "health_check": "/health"
      },
      "tools": ["recognize_document", "batch_recognize", "health_check"],
      "authorized_for": ["invoice-agent"]
    }
  ]
}
```

### 启动 PaddleOCR-VL 服务

```bash
cd /Users/daodao/dsl/PaddleOCR-VL
./start_services.sh
```

### 验证服务运行

```bash
curl http://localhost:8001/health
```

预期输出：
```json
{"status": "ok"}
```

---

## 📡 使用子 Agent

### 决策机制：何时使用子 Agent

当遇到发票相关任务时，需要决定是使用子 Agent 还是自己处理。

**详细决策指南**: 请参考 `DECISION_GUIDE.md`

#### 快速决策

| 场景 | 推荐 | 说明 |
|------|------|------|
| 1-2张发票，简单查看 | 主 Agent 自己处理 | 快速 |
| 3+张发票 | invoice-agent（推荐） | 批量处理 |
| 需要详细字段 | invoice-agent（推荐） | 10-15个字段 |
| 需要生成表格 | invoice-agent（必须） | CSV/JSON/Excel |
| 未知发票类型 | invoice-agent（推荐） | 可以学习 |

#### 询问用户的方式

当任务适合使用子 Agent 时，询问用户：

```
检测到您的请求涉及发票处理。

如何处理？
选项 1：使用"发票处理专员"处理（推荐）
  • 支持批量处理
  • 提取详细字段（发票号码、金额、税额等）
  • 生成表格文件（CSV/JSON）

选项 2：由我直接处理
  • 快速查看基本信息

请选择 1 或 2：
```

**重要**：总是使用子 Agent 的中文名称"**发票处理专员**"，这样用户更清楚。

### 调用方式

```python
# 通过 sessions_spawn 调用
result = sessions_spawn(
    agent="invoice-agent",
    task="process_invoice",
    params={
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    }
)
```

### 返回结果

#### 成功

```json
{
  "success": true,
  "invoice_type": "vat_special",
  "fields": {
    "invoice_no": "12345678",
    "invoice_date": "2026-03-11",
    "amount": "1000.00",
    ...
  },
  "output_file": "~/invoices_output/2026-03-11_invoices.csv"
}
```

#### 技能不可用

```json
{
  "report_type": "skill_unavailable",
  "skill_name": "paddleocr-vl",
  "action_required": "configure_skill",
  "message": "❌ 无法执行任务：PaddleOCR-VL 技能未配置或服务未启动",
  "instructions": {
    "step_1": "确认项目路径: /Users/daodao/dsl/PaddleOCR-VL",
    "step_2": "检查配置文件: openclaw_config.json",
    "step_3": "启动服务: ./start_services.sh",
    "step_4": "验证服务: curl http://localhost:8001/health"
  }
}
```

---

## 🎯 配置完成后的能力

### 初始能力

- ✅ 识别 4 种发票类型（专票、普票、电子、定额）
- ✅ 提取详细字段（10-15个字段）
- ✅ 生成表格文件（CSV/JSON/Excel）
- ✅ 批量处理支持

### 学习能力

- 🔄 自动学习新发票类型（3个样本触发）
- 🔄 优化字段提取规则（3次失败触发）
- 🔄 学习用户反馈
- 🔄 定期自我升级（24小时检查）

### 汇报能力

- 📊 任务完成汇报
- 📊 学习内容汇报
- 📊 规则更新汇报
- 📊 性能指标汇报
- 📊 升级可用汇报

---

## ⚠️ 重要提示

### 技能依赖

- invoice-agent **只依赖一个技能**：PaddleOCR-VL
- 如果这个技能不可用，会主动向你汇报
- 汇报会包含详细的配置指引

### 技能检查

- 子 Agent 会在每次任务前检查技能
- 如果技能不可用，不会执行任务
- 会发送 `skill_unavailable` 汇报

### 配置要求

1. **项目路径存在**: `/Users/daodao/dsl/PaddleOCR-VL`
2. **配置文件存在**: `openclaw_config.json`
3. **服务正在运行**: `http://localhost:8001`
4. **子 Agent 已授权**: 允许使用 paddleocr-vl 技能

---

## 📚 相关文档

| 文档 | 说明 | 优先级 |
|------|------|--------|
| **MAIN_AGENT_SETUP_GUIDE.md** | ⭐ 主 Agent 配置指南（本文档） | 必读 |
| **DECISION_GUIDE.md** | ⭐ 决策机制：何时使用子 Agent | 必读 |
| `SOUL.md` | Agent 行为规范 | 参考 |
| `config_single_skill.json` | 单技能配置文件 | 参考 |
| `SKILL_REQUIREMENTS.md` | 技能检查详解 | 参考 |
| `FIELD_DEFINITIONS.md` | 字段定义详情 | 参考 |
| `REPORTING_GUIDE.md` | 汇报机制详解 | 参考 |

### 文档阅读顺序

1. **MAIN_AGENT_SETUP_GUIDE.md**（本文档）- 配置子 Agent
2. **DECISION_GUIDE.md** - 学习如何决定使用子 Agent
3. 其他文档 - 参考和深入了解

---

## 🆘 遇到问题？

### 问题 1：技能不可用

**解决**：
1. 检查 PaddleOCR-VL 项目路径
2. 检查配置文件是否存在
3. 启动 OCR 服务
4. 验证服务运行

### 问题 2：学习系统未初始化

**解决**：
```bash
python3 /Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/learning/init_learning_system.py
```

### 问题 3：无法调用子 Agent

**解决**：
1. 确认子 Agent 已注册
2. 确认技能已配置
3. 检查工作空间路径

---

**配置完成后，子 Agent 将具备完整的发票处理能力！** 🎉

---

**文档版本**: 1.0.0
**适用对象**: OpenClaw 主 Agent
**最后更新**: 2026-03-11
