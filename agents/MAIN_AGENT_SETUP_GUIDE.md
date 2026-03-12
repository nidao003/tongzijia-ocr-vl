# 🤖 OpenClaw 主 Agent 配置指南（v3.0）

> **主 Agent 请阅读本文档来配置 invoice-agent 子 Agent**
> **版本**: v3.0 | **更新**: 2026-03-12

---

## 📋 配置目标

配置一个名为 **`发票童子甲`**（invoice-agent）的子 Agent，它能：
- ✅ 识别和处理发票（支持图片和PDF）
- ✅ 提取详细的字段信息
- ✅ 生成表格文件（CSV/JSON/Excel）
- ✅ 批量处理（最多50个文件）
- ✅ 持续学习新的发票类型

**v3.0 新能力**:
- ✨ PDF文件支持（自动转换）
- ✨ 批量处理50个文件
- ✨ 混合格式处理（图片+PDF）
- ⚡ 识别速度1.22秒/张

---

## ⚙️ 配置步骤

### 第 1 步：创建工作空间

```bash
mkdir -p ~/.openclaw/workspace-invoice-agent/{temp,output,skills/invoice-processor/learning,memory,logs}
```

### 第 2 步：复制核心文件

```bash
SRC="/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
DST="$HOME/.openclaw/workspace-invoice-agent"

# 复制配置文件
cp "$SRC/config.json" "$DST/"
cp "$SRC/SOUL.md" "$DST/"
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
version: 3.0.0
---

# PaddleOCR-VL OCR 服务（v3.0）

这是 invoice-agent 唯一依赖的外部技能。

## 配置

- 项目路径: /Users/daodao/dsl/PaddleOCR-VL
- 配置文件: openclaw_config.json
- 服务端点: http://localhost:8001
- 版本: v3.0.0

## v3.0 新能力

- ✅ PDF支持（自动转换）
- ✅ 批量处理（50文件/次）
- ✅ 混合格式（图片+PDF）
- ⚡ 速度1.22秒/张

## 工具

- `recognize_document(file_path, **kwargs)` - 识别单文件（支持图片和PDF）
  - 参数: `file_path`, `dpi`, `max_pages`, `merge_pdf_pages`
- `batch_recognize(file_paths, **kwargs)` - 批量识别（最多50个）
  - 参数: `file_paths`, `callback`, `dpi`, `max_pages`
- `health_check()` - 健康检查

## 支持格式

图片: PNG, JPG, JPEG, WebP, BMP, GIF, TIFF
文档: PDF（最多100页）
EOF
```

### 第 5 步：注册子 Agent

```bash
cat > ~/.openclaw/agents/invoice-agent.json << EOF
{
  "id": "invoice-agent",
  "name": "发票童子甲",
  "role": "户部·发票司",
  "workspace": "$HOME/.openclaw/workspace-invoice-agent",
  "skills": ["paddleocr-vl"],
  "skill_dependencies": ["paddleocr-vl"],
  "requires_skill": "paddleocr-vl",
  "version": "3.0.0",
  "auto_learning": true,
  "supported_formats": ["PNG", "JPEG", "JPG", "WebP", "BMP", "GIF", "TIFF", "PDF"],
  "batch_processing": true,
  "max_batch_size": 50,
  "pdf_support": true,
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "updated_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
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
temp/
output/
skills/
  ├── invoice-processor/
  │   └── SKILL.md
  └── paddleocr-vl/
      └── SKILL.md
```

### 验证子Agent注册

```bash
cat ~/.openclaw/agents/invoice-agent.json | jq '.name'
```

预期输出：
```
"发票童子甲"
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
      "version": "3.0.0",
      "config": {
        "project_path": "/Users/daodao/dsl/PaddleOCR-VL",
        "config_file": "/Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json",
        "service_endpoint": "http://localhost:8001",
        "health_check": "/health"
      },
      "tools": ["recognize_document", "batch_recognize", "health_check"],
      "authorized_for": ["invoice-agent"],
      "supported_formats": ["PNG", "JPEG", "JPG", "WebP", "BMP", "GIF", "TIFF", "PDF"],
      "batch_processing": true,
      "max_batch_size": 50
    }
  ]
}
```

### 启动 PaddleOCR-VL 服务

```bash
cd /Users/daodao/dsl/PaddleOCR-VL
./scripts/start_on_demand.sh
```

### 验证服务运行

```bash
curl http://localhost:8001/health
```

预期输出：
```json
{"status":"healthy","mlx_vlm_service":"running","api_server":"running"}
```

---

## 📡 使用子 Agent

### 决策机制：何时使用子 Agent

| 场景 | 推荐 | 说明 |
|------|------|------|
| 1-2张发票，快速查看 | 主 Agent 自己处理 | 快速查看 |
| 3+张发票 | **发票童子甲**（推荐） | 批量处理 |
| PDF发票 | **发票童子甲**（必须） | 自动转换 |
| 需要详细字段 | **发票童子甲**（推荐） | 10-15个字段 |
| 需要生成表格 | **发票童子甲**（必须） | CSV/JSON/Excel |
| 混合格式批量 | **发票童子甲**（必须） | 图片+PDF混合 |
| 未知发票类型 | **发票童子甲**（推荐） | 可以学习 |

### 🚨 重要：文件处理流程

**在调用子Agent之前，你必须**：

```
1. 接收文件（图片或PDF）
      ↓
2. 移动文件到子Agent临时目录
   mv /path/to/file.png ~/.openclaw/workspace-invoice-agent/temp/
      ↓
3. 调用子Agent（使用绝对路径）
      ↓
4. 子Agent处理并返回结果
      ↓
5. 展示结果给用户
```

**关键规则**：
- ❌ **不要使用 attachments 参数**（当前被禁用）
- 📍 **必须使用绝对路径**
- 🚀 **先移动文件，再调用**
- ⏱️ **设置合理超时时间**

### 调用方式

#### 单张发票（图片）

```python
# 假设用户发了一张发票图片
file_path = "/Users/daodao/Documents/invoice_001.png"

# 第1步：移动文件到子Agent临时目录
import shutil
import os

temp_dir = os.path.expanduser("~/.openclaw/workspace-invoice-agent/temp/")
os.makedirs(temp_dir, exist_ok=True)
temp_file = os.path.join(temp_dir, os.path.basename(file_path))
shutil.move(file_path, temp_file)

# 第2步：调用子Agent
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task=f"请处理这张发票: {temp_file}",
    cwd=os.path.expanduser("~/.openclaw/workspace-invoice-agent"),
    timeoutSeconds=120
)

# 第3步：展示结果
if result.get("success"):
    print(f"✅ 发票处理成功")
    print(f"类型: {result['results'][0]['invoice_type_name']}")
    print(f"金额: {result['results'][0]['fields']['total_amount']}")
else:
    print(f"❌ 处理失败: {result.get('error')}")
```

#### PDF发票

```python
# PDF处理需要更长时间
file_path = "/Users/daodao/Documents/invoices.pdf"

# 第1步：移动文件
temp_dir = os.path.expanduser("~/.openclaw/workspace-invoice-agent/temp/")
temp_file = os.path.join(temp_dir, os.path.basename(file_path))
shutil.move(file_path, temp_file)

# 第2步：调用子Agent（增加超时时间）
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task=f"请处理这个PDF发票: {temp_file}",
    cwd=os.path.expanduser("~/.openclaw/workspace-invoice-agent"),
    timeoutSeconds=300  # PDF需要更长时间
)

# 第3步：展示结果
# ...
```

#### 批量发票（混合格式）

```python
# 批量处理：图片和PDF混合
files = [
    "/Users/daodao/Documents/invoice_001.png",
    "/Users/daodao/Documents/invoice_002.jpg",
    "/Users/daodao/Documents/invoices.pdf"
]

# 第1步：移动所有文件
temp_dir = os.path.expanduser("~/.openclaw/workspace-invoice-agent/temp/")
temp_files = []
for file_path in files:
    temp_file = os.path.join(temp_dir, os.path.basename(file_path))
    shutil.move(file_path, temp_file)
    temp_files.append(temp_file)

# 第2步：调用子Agent（批量处理）
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task=f"""请批量处理以下发票文件:
{chr(10).join(f'- {f}' for f in temp_files)}

输出格式: CSV
保存位置: ~/.openclaw/workspace-invoice-agent/output/""",
    cwd=os.path.expanduser("~/.openclaw/workspace-invoice-agent"),
    timeoutSeconds=600  # 批量处理需要更长时间
)

# 第3步：展示结果
if result.get("success"):
    print(f"✅ 批量处理完成")
    print(f"成功: {result['processed_count']}/{result['processed_count']}")
    print(f"输出文件: {result.get('output_file')}")
else:
    print(f"❌ 处理失败: {result.get('error')}")
```

### 返回结果

#### 成功

```json
{
  "success": true,
  "processed_count": 5,
  "file_type": "mixed",
  "results": [
    {
      "filename": "invoice_001.png",
      "invoice_type": "vat_special",
      "invoice_type_name": "增值税专用发票",
      "fields": {
        "invoice_code": "1500242720",
        "invoice_no": "00534712",
        "invoice_date": "2024-12-18",
        "buyer_name": "xxx公司",
        "seller_name": "xxx公司",
        "amount": "227500.00",
        "tax_amount": "26172.57",
        "total_amount": "253672.57"
      },
      "confidence": 0.95
    }
  ],
  "output_file": "~/.openclaw/workspace-invoice-agent/output/2026-03-12_invoices.csv",
  "statistics": {
    "by_type": {
      "vat_special": 2,
      "vat_common": 3
    },
    "success_rate": 1.0,
    "avg_confidence": 0.92
  }
}
```

#### 失败

```json
{
  "success": false,
  "error": "OCR服务不可用",
  "error_type": "service_unavailable",
  "action_required": "检查PaddleOCR-VL服务状态",
  "instructions": {
    "step_1": "确认服务路径: /Users/daodao/dsl/PaddleOCR-VL",
    "step_2": "启动服务: cd /Users/daodao/dsl/PaddleOCR-VL && ./scripts/start_on_demand.sh",
    "step_3": "验证服务: curl http://localhost:8001/health"
  }
}
```

---

## 🎯 配置完成后的能力

### 初始能力

- ✅ 识别 4 种发票类型（专票、普票、电子、定额）
- ✅ 提取详细字段（10-15个字段）
- ✅ 生成表格文件（CSV/JSON/Excel）
- ✅ 批量处理支持（50个文件）
- ✅ PDF文件支持（自动转换）
- ✅ 混合格式处理

### v3.0 新能力

- ✨ **PDF处理**: 单页/多页PDF自动转换为图片
- ✨ **批量优化**: 最多50个文件，实时进度回调
- ✨ **速度提升**: 1.22秒/张（提升474%）
- ✨ **格式扩展**: 支持11种文件格式

### 学习能力

- 🔄 自动学习新发票类型（3个样本触发）
- 🔄 优化字段提取规则（3次失败触发）
- 🔄 学习用户反馈
- 🔄 定期自我升级（24小时检查）

---

## ⚠️ 重要提示

### 技能依赖

- invoice-agent **只依赖一个技能**：PaddleOCR-VL v3.0
- 如果这个技能不可用，会主动向你汇报
- 汇报会包含详细的配置指引

### 文件处理规则

**必须遵守**：
1. ❌ **不要使用 attachments** - 当前被禁用
2. 📍 **必须用绝对路径** - 写在 task 参数里
3. 🚀 **先移动文件** - 移到 temp/ 目录
4. ⏱️ **设置合理超时** - 单文件120s，PDF 300s，批量600s

### 配置要求

1. **项目路径存在**: `/Users/daodao/dsl/PaddleOCR-VL`
2. **配置文件存在**: `openclaw_config.json`
3. **服务正在运行**: `http://localhost:8001`
4. **子 Agent 已授权**: 允许使用 paddleocr-vl 技能
5. **版本匹配**: PaddleOCR-VL v3.0+

---

## 📚 相关文档

| 文档 | 说明 | 优先级 |
|------|------|--------|
| **MAIN_AGENT_SETUP_GUIDE.md** | ⭐ 主 Agent 配置指南（本文档） | 必读 |
| **AGENT_CONFIG_GUIDE.md** | 完整配置方案和调用规范 | 必读 |
| **README_QUICK.md** | 快速参考卡片 | 必读 |
| `DECISION_GUIDE.md` | 决策机制：何时使用子 Agent | 推荐 |
| `SOUL.md` | Agent 行为规范 | 参考 |
| `REPORTING_GUIDE.md` | 汇报机制详解 | 参考 |

### 文档阅读顺序

1. **MAIN_AGENT_SETUP_GUIDE.md**（本文档）- 配置子 Agent
2. **AGENT_CONFIG_GUIDE.md** - 了解完整调用规范
3. **README_QUICK.md** - 快速参考
4. 其他文档 - 参考和深入了解

---

## 🆘 遇到问题？

### 问题 1：技能不可用

**解决**：
1. 检查 PaddleOCR-VL 项目路径
2. 检查配置文件是否存在
3. 启动 OCR 服务：`cd /Users/daodao/dsl/PaddleOCR-VL && ./scripts/start_on_demand.sh`
4. 验证服务运行：`curl http://localhost:8001/health`

### 问题 2：学习系统未初始化

**解决**：
```bash
python3 /Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/learning/init_learning_system.py
```

### 问题 3：无法调用子 Agent

**解决**：
1. 确认子 Agent 已注册：`cat ~/.openclaw/agents/invoice-agent.json`
2. 确认技能已配置
3. 检查工作空间路径
4. 确认文件已移动到 temp/ 目录

### 问题 4：PDF处理失败

**解决**：
1. 检查PDF是否加密
2. 检查PDF页数（≤100页）
3. 增加超时时间到300秒
4. 检查临时目录权限

---

**配置完成后，子 Agent 将具备完整的发票处理能力（v3.0）！** 🎉

---

**文档版本**: 3.0.0
**适用对象**: OpenClaw 主 Agent
**最后更新**: 2026-03-12
