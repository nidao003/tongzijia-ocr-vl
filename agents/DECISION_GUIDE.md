# 🤖 主 Agent 决策机制：发票处理任务分配

> **当遇到发票问题时，主 Agent 如何决定是使用子 Agent 还是自己处理**

---

## 📋 决策流程

### 第 1 步：识别任务类型

当用户请求涉及以下内容时，识别为发票处理任务：

**发票相关关键词**：
- 发票、票据、凭证
- 增值税、专票、普票、电子发票
- 发票号码、发票代码
- 抬头、金额、税额
- 报销、入账

**示例用户请求**：
- "帮我处理这张发票"
- "识别发票内容"
- "提取发票信息"
- "批量处理发票"
- "这张发票是什么类型的？"
- "发票上的金额是多少？"

---

## 🎯 决策逻辑

### 选项 A：建议使用 invoice-agent（推荐）

**适合使用子 Agent 的场景**：

```
✅ 批量处理（3张以上）
✅ 需要详细字段提取
✅ 需要生成表格文件
✅ 遇到未知发票类型
✅ 需要学习新的发票格式
✅ 需要定期处理大量发票
```

### 选项 B：主 Agent 自己处理

**适合主 Agent 自己处理的场景**：

```
✅ 简单查询（1-2张发票）
✅ 只需要基本信息
✅ 快速查看发票内容
✅ 不需要保存结果
✅ 不需要生成表格
✅ 用户明确要求主 Agent 处理
```

---

## 💬 询问用户的模板

### 标准询问格式

```
检测到您的请求涉及发票处理。

您希望我如何处理？

选项 1：使用"发票处理专员"处理（推荐）
  • 适合：批量处理、详细提取、生成表格
  • 能力：智能分类、字段提取、持续学习
  • 位置：使用我的子 Agent "发票处理专员"

选项 2：由我（主 Agent）直接处理
  • 适合：简单查询、快速查看
  • 限制：功能较基础，不保存结果

请选择 1 或 2：
```

### 具体场景的询问模板

#### 场景 1：批量处理发票

```
检测到您需要处理多张发票。

建议使用"发票处理专员"处理，因为：
  • 支持批量处理（最多10张/批）
  • 自动识别发票类型
  • 提取详细字段（10-15个字段）
  • 生成 CSV/JSON 表格文件

是否使用"发票处理专员"处理？
  • 是 → 使用子 Agent
  • 否 → 我自己处理（功能较基础）

请选择：
```

#### 场景 2：需要详细字段提取

```
检测到您需要详细的发票信息。

"发票处理专员"可以提取以下详细字段：
  • 发票代码、发票号码
  • 开票日期
  • 购买方、销售方信息
  • 金额、税率、税额
  • 价税合计
  • 备注
  • 并生成表格文件

是否使用"发票处理专员"提取详细字段？
  • 是 → 使用子 Agent
  • 否 → 我只提供基本信息

请选择：
```

#### 场景 3：遇到未知发票类型

```
检测到这张发票可能是未知类型。

建议使用"发票处理专员"，因为：
  • 它有持续学习能力
  • 可以自动识别新发票类型
  • 会学习和优化识别规则

是否使用"发票处理专员"处理？
  • 是 → 使用子 Agent（可能会学习新类型）
  • 否 → 我尝试识别（可能不准确）

请选择：
```

---

## 📡 向用户询问的代码示例

### 主 Agent 的决策逻辑

```python
# 主 Agent 的处理逻辑
def handle_invoice_request(user_request, invoice_images):
    # 1. 识别任务特征
    invoice_count = len(invoice_images)
    needs_detail = check_if_needs_detail_fields(user_request)
    needs_table = check_if_needs_table(user_request)

    # 2. 决策
    if invoice_count >= 3 or needs_detail or needs_table:
        # 建议使用子 Agent
        return ask_user_for_agent_choice(user_request, invoice_images)
    else:
        # 简单任务，主 Agent 自己处理
        return process_with_main_agent(user_request, invoice_images)

def ask_user_for_agent_choice(user_request, invoice_images):
    # 向用户询问
    message = f"""检测到您的请求涉及发票处理（{len(invoice_images)}张）。

您希望我如何处理？

**选项 1：使用"发票处理专员"处理（推荐）**
  • 智能识别发票类型
  • 提取详细字段（发票号码、金额、税额等）
  • 生成表格文件（CSV/JSON）
  • 支持批量处理

**选项 2：由我直接处理**
  • 快速查看基本信息
  • 不保存结果

请回复：
  • "1" 或 "使用发票处理专员" → 使用子 Agent
  • "2" 或 "你处理" → 我自己处理"""

    return message
```

---

## 🎯 快速决策指南

### 根据发票数量

| 数量 | 推荐 | 说明 |
|------|------|------|
| 1-2 张 | 主 Agent 自己处理 | 快速查看基本信息 |
| 3-10 张 | invoice-agent（推荐） | 批量处理效率高 |
| 10+ 张 | invoice-agent（必须） | 分批处理，生成表格 |

### 根据任务复杂度

| 任务 | 推荐 | 说明 |
|------|------|------|
| 查看发票类型 | 主 Agent 自己处理 | 简单分类 |
| 提取基本字段 | 主 Agent 自己处理 | 发票号、日期、金额 |
| 提取详细字段 | invoice-agent（推荐） | 所有字段（10-15个） |
| 生成表格文件 | invoice-agent（必须） | CSV/JSON/Excel |
| 批量统计 | invoice-agent（推荐） | 分类统计、金额汇总 |

### 根据用户需求

| 用户需求 | 推荐 |
|---------|------|
| "帮我看看这张发票" | 主 Agent 自己处理 |
| "这是什么发票" | 主 Agent 自己处理 |
| "发票金额是多少" | 主 Agent 自己处理 |
| "提取发票信息" | 询问用户 |
| "处理这些发票" | invoice-agent（推荐） |
| "生成报销单" | invoice-agent（必须） |
| "整理成表格" | invoice-agent（必须） |

---

## 💡 询问策略

### 主动询问时机

在以下情况下，主动询问用户：

```
1. 批量处理（3张以上）
   → "检测到您需要处理多张发票，是否使用专门的发票处理专员？"

2. 需要详细字段
   → "需要提取详细字段信息吗？我的子 Agent '发票处理专员' 可以提供更完整的字段提取"

3. 需要生成表格
   → "需要生成表格文件吗？我的子 Agent '发票处理专员' 可以为您生成 CSV/Excel 文件"

4. 遇到复杂发票
   → "这张发票格式较复杂，建议使用我的子 Agent '发票处理专员' 处理，它可以持续学习新类型"
```

### 简化询问（二选一）

```
检测到发票处理任务。

如何处理？
1. 使用"发票处理专员"（推荐，功能完整）
2. 我直接处理（快速，功能基础）

请选择 1 或 2：
```

---

## 📊 决策结果记录

### 选择使用 invoice-agent

```json
{
  "decision": "use_subagent",
  "subagent": "invoice-agent",
  "subagent_name": "发票处理专员",
  "reason": "user_requested_detail_processing",
  "task_forwarded": true
}
```

### 选择主 Agent 处理

```json
{
  "decision": "use_main_agent",
  "reason": "user_requested_simple_processing",
  "capabilities_used": ["basic_ocr", "simple_classification"],
  "task_forwarded": false
}
```

---

## 🔧 实现示例

### 主 Agent 的完整决策流程

```python
class InvoiceTaskRouter:
    def handle_invoice_task(self, user_message, invoice_images):
        # 分析任务
        task_analysis = self.analyze_task(user_message, invoice_images)

        # 决策
        if task_analysis["complexity"] == "high":
            # 高复杂度任务，询问用户
            return self.ask_user(
                task_analysis,
                options=[
                    "使用发票处理专员（推荐）",
                    "主 Agent 直接处理"
                ]
            )
        else:
            # 低复杂度任务，主 Agent 直接处理
            return self.process_directly(task_analysis)

    def ask_user(self, task_analysis, options):
        return {
            "type": "user_choice_required",
            "context": f"检测到发票处理任务（{task_analysis['invoice_count']}张）",
            "options": options,
            "default_recommendation": options[0],
            "question": "请选择处理方式："
        }
```

---

## 📝 用户回复示例

### 用户选择使用子 Agent

```
用户: "使用发票处理专员"
或
用户: "1"
或
用户: "用子 Agent 处理"

主 Agent 的响应：
"好的，我将使用我的子 Agent '发票处理专员' 为您处理发票。"

然后调用：
sessions_spawn(agent="invoice-agent", task="process_invoice", params={...})
```

### 用户选择主 Agent 处理

```
用户: "你处理"
或
用户: "2"
或
用户: "直接看看就行"

主 Agent 的响应：
"好的，我来为您查看发票的基本信息。"

然后主 Agent 自己处理（可能调用 OCR 但不生成表格）
```

---

## ⚡ 快速参考

### 决策树

```
发票任务
  │
  ├─→ 单张 + 简单查看？
  │   └─→ 主 Agent 自己处理
  │
  ├─→ 批量（3+张）？
  │   └─→ 询问用户（推荐子 Agent）
  │
  ├─→ 需要详细字段？
  │   └─→ 询问用户（推荐子 Agent）
  │
  ├─→ 需要表格文件？
  │   └─→ 询问用户（必须子 Agent）
  │
  └─→ 未知类型？
      └─→ 询问用户（推荐子 Agent，可以学习）
```

---

## 🎯 最佳实践

### 推荐做法

1. **明确告知子 Agent 名称**：总是使用"发票处理专员"这个中文名称
2. **说明子 Agent 能力**：简要说明子 Agent 擅长什么
3. **给出推荐选项**：基于任务特点给出推荐
4. **简化选择**：最多提供 2-3 个选项
5. **尊重用户选择**：用户选择后立即执行，不再二次询问

### 示例对话

```
用户: "帮我处理这5张发票"

主 Agent: 检测到您需要处理多张发票。

我建议使用我的子 Agent "发票处理专员" 处理，因为：
  • 支持批量处理
  • 自动识别发票类型
  • 提取详细字段
  • 生成表格文件

如何处理？
选项 1：使用"发票处理专员"（推荐）
选项 2：由我直接处理

请选择 1 或 2：

用户: "1"

主 Agent: 好的，正在使用"发票处理专员"为您处理发票...

[调用代码]
result = sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="batch_process",
    params={
        "image_paths": [...5张发票...],
        "output_format": "csv"
    },
    cwd="~/.openclaw/workspace-invoice-agent"
)

主 Agent: 处理完成！
  • 处理了 5 张发票
  • 识别出 2 张增值税专用发票，3 张普通发票
  • 提取了详细字段信息
  • 已生成表格文件：~/invoices_output/2026-03-11_invoices.csv
```

---

**决策机制版本**: 1.0.0
**最后更新**: 2026-03-11
**核心原则**: 让用户明确选择，说明子 Agent 的名称和能力
