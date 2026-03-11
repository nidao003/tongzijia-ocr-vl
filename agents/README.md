# 🤖 OpenClaw 主 Agent 快速参考

> **发票处理专员子 Agent 创建指南**

---

## 📋 给主 Agent 的重要信息

### 子 Agent 概况

```
Agent ID: invoice-agent
角色: 发票处理专员（户部·发票司）
核心能力: 发票识别 + 智能分类 + 字段提取 + 持续学习
```

### 🎯 一句话说明

这是一个专门处理发票的子 Agent，能自动识别发票类型、提取字段，并且可以从处理过程中不断学习新的发票类型，优化识别规则。

---

## ⚡ 快速创建（复制这个给主 Agent）

主 Agent，请执行以下步骤创建 `invoice-agent`：

```bash
# 1. 创建工作空间
mkdir -p ~/.openclaw/workspace-invoice-agent/{skills/invoice-processor/learning,memory,logs}

# 2. 复制核心文件
SRC="/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
DST="$HOME/.openclaw/workspace-invoice-agent"
cp "$SRC/SOUL.md" "$DST/"
cp "$SRC/config.json" "$DST/"
cp "$SRC/skills/invoice-processor/SKILL.md" "$DST/skills/invoice-processor/"

# 3. 初始化学习系统
python3 "$SRC/learning/init_learning_system.py"

# 4. 创建技能链接
mkdir -p "$DST/skills/paddleocr-vl"
cat > "$DST/skills/paddleocr-vl/SKILL.md" << 'EOF'
---
name: paddleocr-vl
external: true
source: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
---
# PaddleOCR-VL OCR 服务
EOF

# 5. 注册 Agent
cat > ~/.openclaw/agents/invoice-agent.json << EOF
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "workspace": "$DST",
  "skills": ["paddleocr-vl", "invoice-processor"],
  "auto_learning": true
}
EOF
```

**创建完成后，子 Agent 将具备：**
- ✅ 识别 4 种初始发票类型
- ✅ 智能字段提取（15+ 字段）
- ✅ 持续学习能力（学习新类型、优化规则）
- ✅ 自我升级机制（24 小时检查）

---

## 📡 通讯配置

### 主 Agent → 子 Agent

```yaml
endpoint: http://localhost:8002
actions:
  process: POST /process          # 处理单张发票
  batch: POST /batch              # 批量处理
  classify: POST /classify        # 单独分类
  learn: POST /learn              # 主动教学
  health: GET /health             # 健康检查
```

### 子 Agent → 主 Agent

```yaml
events:
  task_completed: 上报处理结果
  new_type_learned: 通知学习了新类型
  rules_optimized: 通知规则优化完成
  upgrade_available: 请求升级批准
```

---

## 💡 核心特性

### 1. 初始能力
```yaml
invoice_types:
  - 增值税专用发票 (置信度 95%)
  - 增值税普通发票 (置信度 92%)
  - 电子发票 (置信度 90%)
  - 定额发票 (置信度 85%)

field_extraction:
  - 发票号码、日期
  - 购买方、销售方
  - 金额、税额、价税合计
  - 等 15+ 字段
```

### 2. 学习能力
```yaml
learning_triggers:
  - 遇到未知类型（3 个样本触发学习）
  - 字段提取失败（3 次触发优化）
  - 用户反馈（立即应用）

learning_capabilities:
  - 自动识别新发票类型
  - 学习字段提取模式
  - 优化正则表达式规则
  - 更新知识库
```

### 3. 自我升级
```yaml
upgrade:
  check_interval: 24 小时
  auto_upgrade: false (需主 Agent 批准)
  preserve_learning: true
```

---

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| `invoice-agent/MAIN_AGENT_README.md` | ⭐ **主 Agent 快速参考** |
| `invoice-agent/SOUL.md` | Agent 行为规范和能力定义 |
| `invoice-agent/config.json` | 完整配置参数 |
| `invoice-agent/AGENT_CREATION.md` | 详细创建步骤和验证 |

---

## 🔄 工作流程示例

```
主 Agent
  │
  ├─→ 发送发票处理任务
  │   └─→ invoice-agent
  │       │
  │       ├─→ 1. 调用 PaddleOCR-VL 识别文字
  │       ├─→ 2. 分类发票类型
  │       ├─→ 3. 提取字段
  │       ├─→ 4. 如果是未知类型 → 触发学习
  │       ├─→ 5. 整理数据
  │       └─→ 6. 上报结果
  │
  └─← 接收结果
      - JSON/CSV 格式数据
      - 处理统计
      - 如果学习了新类型 → 同时通知
```

---

## 🎯 使用场景

### 场景 1：日常发票处理
```python
主 Agent: "处理这 5 张发票"
子 Agent: 识别 → 分类 → 提取 → 生成 CSV
```

### 场景 2：遇到新类型
```python
主 Agent: "这是什么发票？"
子 Agent: "置信度低，触发学习流程"
       → 分析特征 → 创建新类型 → 通知主 Agent
```

### 场景 3：持续优化
```python
主 Agent: "上次提取的金额字段有误"
子 Agent: "记录反馈 → 优化规则 → 下次改进"
```

---

## ✅ 验证清单

创建后请验证：

```bash
# 1. 文件结构
ls -l ~/.openclaw/workspace-invoice-agent/
# ✅ SOUL.md, config.json, memory/, skills/

# 2. 学习数据
jq '.total_types' ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json
# ✅ 输出: 4

# 3. 技能链接
ls -l ~/.openclaw/workspace-invoice-agent/skills/
# ✅ invoice-processor/, paddleocr-vl/
```

---

## 🆘 常见问题

**Q: 子 Agent 会自己升级吗？**
A: 不会自动升级，会先请求主 Agent 批准。但会自动学习新发票类型和优化规则。

**Q: 学习数据会丢失吗？**
A: 不会。所有学习数据存储在 `memory/` 目录，升级时会保留。

**Q: 如何教子 Agent 新类型？**
A: 调用 `/learn` 接口，提供发票文本和字段示例。

---

**关键文件位置**:
```
/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/
```

**主 Agent 请首先阅读**: `invoice-agent/MAIN_AGENT_README.md`
