# OpenClaw 子 Agent 创建指令：发票处理专员

> 📋 **文档类型**: Agent 创建指令
> 🎯 **目标读者**: OpenClaw 主 Agent
> 📅 **版本**: 1.0.0
> 🔄 **最后更新**: 2026-03-11

---

## 📌 指令概述

本指令文档包含创建"发票处理专员"子 Agent 的完整信息。主 Agent 阅读后应能够：

1. ✅ 创建子 Agent 工作空间
2. ✅ 复制必要的配置文件
3. ✅ 配置技能授权（PaddleOCR-VL + invoice-processor）
4. ✅ 配置通讯路由
5. ✅ 启动自我学习机制

---

## 🏗️ 子 Agent 架构

### 基本信息

```yaml
agent_id: invoice-agent
agent_name: 发票处理专员
agent_role: 户部·发票司
agent_type: subagent
version: 1.0.0
capabilities:
  - invoice_classification
  - field_extraction
  - batch_processing
  - continuous_learning
```

### 文件结构

```
~/.openclaw/workspace-invoice-agent/
├── SOUL.md                           # Agent 灵魂定义（必需）
├── config.json                       # Agent 配置（必需）
├── skills/
│   ├── paddleocr-vl/                 # OCR 技能（外部引用）
│   │   └── SKILL.md                  # 指向 PaddleOCR-VL 项目
│   └── invoice-processor/            # 发票处理技能（本地）
│       ├── SKILL.md                  # 技能定义
│       └── learning/                 # 学习数据目录
│           ├── invoice_templates/    # 发票模板库
│           ├── field_patterns/       # 字段模式库
│           └── feedback/             # 用户反馈数据
├── memory/
│   ├── known_invoices.json           # 已知发票类型
│   ├── extraction_rules.json         # 提取规则
│   └── performance_metrics.json      # 性能指标
└── logs/                             # 运行日志
```

---

## 📋 创建步骤

### Step 1: 创建工作空间

```bash
# 执行以下命令创建目录结构
mkdir -p ~/.openclaw/workspace-invoice-agent/skills/invoice-processor/learning
mkdir -p ~/.openclaw/workspace-invoice-agent/memory
mkdir -p ~/.openclaw/workspace-invoice-agent/logs
```

### Step 2: 复制核心文件

```bash
# 从项目目录复制文件
PROJECT_SRC="/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
WORKSPACE_DST="$HOME/.openclaw/workspace-invoice-agent"

# 复制 SOUL.md
cp "$PROJECT_SRC/SOUL.md" "$WORKSPACE_DST/"

# 复制配置文件
cp "$PROJECT_SRC/config.json" "$WORKSPACE_DST/"

# 复制技能文件
cp "$PROJECT_SRC/skills/invoice-processor/SKILL.md" \
   "$WORKSPACE_DST/skills/invoice-processor/"
```

### Step 3: 创建 OCR 技能链接

```bash
# 创建指向 PaddleOCR-VL 的技能文件
cat > "$WORKSPACE_DST/skills/paddleocr-vl/SKILL.md" << 'EOF'
---
name: paddleocr-vl
description: PaddleOCR-VL 高性能文档识别服务
version: 1.0.0
external: true
source: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
---

# PaddleOCR-VL OCR 服务

提供高精度文档文字识别能力。

## 工具

- `recognize_document(image_path)` - 识别单张图片
- `batch_recognize(image_paths)` - 批量识别
- `health_check()` - 健康检查

## 配置

- 端点: http://localhost:8001
- 详细配置: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
EOF
```

### Step 4: 初始化学习系统

```bash
# 使用 Python 脚本初始化学习数据库
python3 /Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/learning/init_learning_system.py
```

这个脚本会自动创建：
- `memory/known_invoices.json` - 已知发票类型库（含详细字段配置）
- `memory/extraction_rules.json` - 提取规则配置
- `memory/performance_metrics.json` - 性能指标追踪
- `memory/learning_config.json` - 学习和升级配置
- `learning/invoice_templates/` - 发票模板库
- `learning/field_patterns/` - 字段模式学习样本
- `learning/feedback/` - 用户反馈数据

初始化后的配置包含：

**已支持 4 种发票类型**：
1. 增值税专用发票（vat_special）- 置信度 95%
2. 增值税普通发票（vat_common）- 置信度 92%
3. 电子发票（electronic）- 置信度 90%
4. 定额发票（quota）- 置信度 85%

**每种类型包含**：
- 关键词列表
- 版式特征
- 字段定义（含正则模式）
- 提取策略
- 位置提示

**学习能力**：
- 自动识别新发票类型（最少 3 个样本）
- 从失败案例中优化规则
- 学习用户反馈的纠正
- 定期检查更新（24 小时）

### Step 5: 注册 Agent

```bash
# 在 OpenClaw 中注册此 Agent
cat > ~/.openclaw/agents/invoice-agent.json << 'EOF'
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "role": "户部·发票司",
  "version": "1.0.0",
  "soul_path": "$HOME/.openclaw/workspace-invoice-agent/SOUL.md",
  "config_path": "$HOME/.openclaw/workspace-invoice-agent/config.json",
  "workspace": "$HOME/.openclaw/workspace-invoice-agent",
  "skills": [
    {
      "name": "paddleocr-vl",
      "type": "external",
      "path": "$HOME/.openclaw/workspace-invoice-agent/skills/paddleocr-vl/SKILL.md",
      "enabled": true
    },
    {
      "name": "invoice-processor",
      "type": "local",
      "path": "$HOME/.openclaw/workspace-invoice-agent/skills/invoice-processor/SKILL.md",
      "enabled": true
    }
  ],
  "communication": {
    "api_enabled": true,
    "port": 8002,
    "endpoints": {
      "process": "POST /process",
      "batch": "POST /batch",
      "classify": "POST /classify",
      "learn": "POST /learn",
      "health": "GET /health"
    }
  },
  "auto_learning": true,
  "created_at": "2026-03-11T00:00:00Z"
}
EOF
```

---

## 🔗 通讯路由配置

### 主 Agent → 子 Agent

```json
{
  "from": "main-agent",
  "to": "invoice-agent",
  "protocol": "http",
  "endpoint": "http://localhost:8002",
  "actions": {
    "process_invoice": {
      "method": "POST",
      "path": "/process",
      "timeout": 60
    },
    "batch_process": {
      "method": "POST",
      "path": "/batch",
      "timeout": 300
    },
    "classify_invoice": {
      "method": "POST",
      "path": "/classify",
      "timeout": 30
    },
    "teach_invoice": {
      "method": "POST",
      "path": "/learn",
      "timeout": 60
    }
  }
}
```

### 子 Agent → 主 Agent（结果上报）

```json
{
  "from": "invoice-agent",
  "to": "main-agent",
  "protocol": "callback",
  "events": {
    "task_completed": {
      "data": {
        "task_id": "{{task_id}}",
        "status": "completed",
        "result": {...}
      }
    },
    "task_failed": {
      "data": {
        "task_id": "{{task_id}}",
        "status": "failed",
        "error": "..."
      }
    },
    "new_invoice_learned": {
      "data": {
        "invoice_type": "new_type",
        "confidence": 0.8,
        "sample_count": 10
      }
    }
  }
}
```

---

## 🧠 自我学习和升级机制

### 学习触发条件

1. **遇到未知发票类型**
   - 分类置信度 < 0.6
   - 不匹配任何已知类型

2. **字段提取失败率高**
   - 必填字段缺失率 > 30%
   - 连续 5 张相同类型发票提取失败

3. **用户主动反馈**
   - 接收用户纠正的标注数据
   - 接收用户提供的模板

### 学习流程

```
┌─────────────────┐
│  处理新发票      │
└────────┬────────┘
         │
         ├─→ 匹配已知类型？
         │   ├─ 是 → 按已知规则处理
         │   └─ 否 → 触发学习流程
         │
┌────────▼────────┐
│  特征提取        │
│  - 版式分析      │
│  - 关键词提取    │
│  - 字段定位      │
└────────┬────────┘
         │
┌────────▼────────┐
│  模式匹配        │
│  - 相似度计算    │
│  - 聚类分析      │
└────────┬────────┘
         │
┌────────▼────────┐
│  规则生成        │
│  - 字段映射      │
│  - 提取规则      │
└────────┬────────┘
         │
┌────────▼────────┐
│  验证与迭代      │
│  - 准确率测试    │
│  - 规则优化      │
└────────┬────────┘
         │
┌────────▼────────┐
│  知识库更新      │
│  - 存储新类型    │
│  - 更新规则      │
└─────────────────┘
```

### 知识库更新

```python
# 当学习到新发票类型时
def learn_new_invoice_type(invoice_data):
    # 1. 分析特征
    features = extract_features(invoice_data)

    # 2. 检查是否为新类型
    if is_new_type(features):
        # 3. 创建新类型定义
        new_type = {
            "id": f"custom_{uuid}",
            "name": invoice_data.get("type_name", "未知类型"),
            "confidence": 0.7,
            "sample_count": 1,
            "learned_at": datetime.now().isoformat(),
            "fields": infer_fields(invoice_data)
        }

        # 4. 更新知识库
        memory = load_memory("known_invoices.json")
        memory["invoice_types"][new_type["id"]] = new_type
        save_memory(memory)

        # 5. 通知主 Agent
        notify_main_agent("new_type_learned", new_type)

        return new_type
```

### 持续优化

```python
# 定期优化提取规则
def optimize_extraction_rules():
    # 1. 加载历史数据
    history = load_processing_history()

    # 2. 分析失败案例
    failures = [h for h in history if h["confidence"] < 0.7]

    # 3. 调整规则参数
    for invoice_type, failures_in_type in group_by_type(failures):
        # 分析失败原因
        issues = analyze_failures(failures_in_type)

        # 优化规则
        for issue in issues:
            if issue["type"] == "pattern_not_matched":
                # 学习新模式
                new_pattern = learn_pattern(issue["examples"])
                update_field_pattern(invoice_type, issue["field"], new_pattern)

            elif issue["type"] == "false_positive":
                # 添加排除规则
                add_exclusion_rule(invoice_type, issue["field"], issue["pattern"])

    # 4. 验证改进效果
    new_accuracy = test_accuracy(validation_set)

    # 5. 更新性能指标
    metrics = load_memory("performance_metrics.json")
    metrics["learning_progress"]["rules_refined"] += 1
    metrics["learning_progress"]["accuracy_improvement"] = \
        new_accuracy - metrics["statistics"]["success_rate"]
    save_memory(metrics)
```

---

## 🔄 升级机制

### 自动检查更新

```yaml
upgrade_config:
  check_interval: 86400  # 每 24 小时
  source:
    type: "git"
    repository: "/Users/daodao/dsl/PaddleOCR-VL"
    branch: "main"
  auto_upgrade: false  # 需要主 Agent 批准
  backup_before_upgrade: true
```

### 升级流程

1. **检查更新**
   - 对比本地和远程版本
   - 列出变更内容

2. **评估影响**
   - 检查是否影响现有学习数据
   - 验证向后兼容性

3. **创建备份**
   - 备份当前知识库
   - 备份配置文件

4. **执行升级**
   - 更新核心文件
   - 迁移学习数据

5. **验证升级**
   - 运行测试用例
   - 确认功能正常

---

## ✅ 验证检查清单

创建完成后，主 Agent 应验证：

- [ ] 工作空间目录结构完整
- [ ] SOUL.md 文件存在且有效
- [ ] config.json 配置正确
- [ ] 技能文件已链接
- [ ] 学习数据库已初始化
- [ ] 通讯路由已配置
- [ ] 可以处理测试发票

### 验证命令

```bash
# 测试 Agent 是否可用
curl http://localhost:8002/health

# 测试发票处理
curl -X POST http://localhost:8002/process \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/path/to/test_invoice.png"}'

# 检查学习数据
cat ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json
```

---

## 📞 故障排除

| 问题 | 解决方案 |
|------|----------|
| 技能文件找不到 | 检查 paddleocr-vl 路径是否正确 |
| 无法学习新类型 | 检查 memory 目录权限 |
| 通讯失败 | 检查端口 8002 是否被占用 |
| 配置加载失败 | 验证 JSON 格式是否正确 |

---

## 📚 相关文档

- SOUL.md: Agent 行为规范
- invoice-processor/SKILL.md: 发票处理技能详情
- README.md: 完整使用文档

---

**文档版本**: 1.0.0
**创建日期**: 2026-03-11
**适用于**: OpenClaw 主 Agent
