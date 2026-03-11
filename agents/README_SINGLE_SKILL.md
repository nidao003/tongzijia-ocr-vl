# 🤖 OpenClaw 主 Agent 快速参考（单技能版本）

> **发票处理专员子 Agent 创建指南**

---

## 📋 给主 Agent 的重要信息

### 子 Agent 概况

```
Agent ID: invoice-agent
角色: 发票处理专员（户部·发票司）
核心能力: 发票识别 + 智能分类 + 字段提取 + 持续学习
依赖技能: PaddleOCR-VL（唯一外部技能）
```

### 🎯 一句话说明

这是一个专门处理发票的子 Agent，**只依赖一个技能：PaddleOCR-VL**。如果没有这个技能，会主动向你汇报并请求配置。

---

## ⚠️ 技能依赖说明

### 唯一依赖：PaddleOCR-VL

```yaml
技能名称: paddleocr-vl
技能类型: 外部服务
必需性: 必需
用途: OCR 文字识别
配置路径: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
服务端点: http://localhost:8001
```

### 技能不可用时

如果技能不可用，invoice-agent 会向你汇报：

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

## ⚡ 快速创建

### 步骤 1：创建工作空间

```bash
mkdir -p ~/.openclaw/workspace-invoice-agent/{skills/invoice-processor/learning,memory,logs}
```

### 步骤 2：复制核心文件

```bash
SRC="/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
DST="$HOME/.openclaw/workspace-invoice-agent"

# 复制配置（使用单技能版本配置）
cp "$SRC/config_single_skill.json" "$DST/config.json"
cp "$SRC/SOUL.md" "$DST/"
cp "$SRC/skills/invoice-processor/SKILL.md" "$DST/skills/invoice-processor/"
```

### 步骤 3：初始化学习系统

```bash
python3 "$SRC/learning/init_learning_system.py"
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

这是 invoice-agent 唯一依赖的外部技能。

## 配置

- 项目路径: /Users/daodao/dsl/PaddleOCR-VL
- 配置文件: openclaw_config.json
- 服务端点: http://localhost:8001

## 工具

- `recognize_document(image_path)` - 识别单张图片
- `batch_recognize(image_paths)` - 批量识别
- `health_check()` - 健康检查

## 性能

- 平均速度: 7秒/张
- 支持格式: PNG, JPEG, WebP
- 支持语言: 109种
EOF
```

### 步骤 5：注册 Agent

```bash
cat > ~/.openclaw/agents/invoice-agent.json << EOF
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "workspace": "$DST",
  "skills": ["paddleocr-vl"],
  "skill_dependencies": ["paddleocr-vl"],
  "auto_learning": true,
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
```

---

## 🔧 技能配置

### 主 Agent 需要配置的技能

```json
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

---

## 📡 使用方式

### 调用示例

```python
# 主 Agent 调用
result = sessions_spawn(
    agent="invoice-agent",
    task="process_invoice",
    params={
        "image_path": "/path/to/invoice.png",
        "output_format": "json"
    }
)
```

### 可能的响应

#### 成功

```json
{
  "success": true,
  "invoice_type": "vat_special",
  "fields": {
    "invoice_no": "12345678",
    "amount": "1000.00",
    ...
  }
}
```

#### 技能不可用

```json
{
  "report_type": "skill_unavailable",
  "skill_name": "paddleocr-vl",
  "action_required": "configure_skill",
  "message": "❌ 无法执行任务：PaddleOCR-VL 技能未配置或服务未启动"
}
```

---

## ✅ 验证清单

创建完成后验证：

```bash
# 1. 文件结构
ls -l ~/.openclaw/workspace-invoice-agent/
# ✅ config.json, SOUL.md, memory/, skills/

# 2. 配置文件（只包含一个技能）
cat ~/.openclaw/workspace-invoice-agent/config.json | jq '.skills | length'
# ✅ 输出: 1

# 3. 学习数据
jq '.total_types' ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json
# ✅ 输出: 4

# 4. 技能链接
ls -l ~/.openclaw/workspace-invoice-agent/skills/
# ✅ invoice-processor/, paddleocr-vl/
```

---

## 🆘 故障排除

### 问题：子 Agent 报告技能不可用

**解决步骤**：

1. **检查项目目录**
   ```bash
   ls -la /Users/daodao/dsl/PaddleOCR-VL
   ```

2. **检查配置文件**
   ```bash
   cat /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
   ```

3. **启动服务**
   ```bash
   cd /Users/daodao/dsl/PaddleOCR-VL
   ./start_services.sh
   ```

4. **验证服务**
   ```bash
   curl http://localhost:8001/health
   ```

5. **在主 Agent 中配置技能**
   ```python
   configure_skill(
       skill_id="paddleocr-vl",
       source="local",
       config_path="/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json"
   )
   ```

---

## 📊 技能依赖总结

```
invoice-agent
    │
    └──→ paddleocr-vl (唯一外部技能)
            │
            ├──→ OCR 文字识别
            └──→ 返回识别文本

invoice-agent 内置能力：
    ├──→ 发票分类
    ├──→ 字段提取
    ├──→ 数据格式化
    └──→ 持续学习
```

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| `SOUL.md` | Agent 行为规范（包含技能检查） |
| `config_single_skill.json` | 单技能配置文件 |
| `SKILL_REQUIREMENTS.md` | 技能检查和汇报详解 |

---

**版本**: 1.0.0 (单技能版本)
**更新日期**: 2026-03-11
**核心原则**: 只依赖 PaddleOCR-VL 一个外部技能，其他都是内置能力
