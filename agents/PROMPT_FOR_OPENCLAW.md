# 发送给 OpenClaw 主 Agent 的指令

复制以下内容发送给 OpenClaw 主 Agent：

---

## 🤖 任务：创建发票处理子 Agent

请阅读 `/Users/daodao/dsl/PaddleOCR-VL/agents/README.md` 文件，然后按照文档中的步骤创建 `invoice-agent` 子 Agent。

### 要求：

1. **阅读 README.md** - 理解子 Agent 的功能和创建步骤
2. **执行创建命令** - 按照文档中的 bash 命令创建工作空间
3. **验证创建结果** - 确认所有文件都已正确创建

### 预期结果：

- 工作空间: `~/.openclaw/workspace-invoice-agent/`
- 支持 4 种发票类型
- 具备持续学习能力
- 可以通过 http://localhost:8002 调用

### 验证步骤：

创建完成后，请执行以下验证命令并报告结果：

```bash
# 1. 检查文件结构
ls -l ~/.openclaw/workspace-invoice-agent/

# 2. 检查学习数据
jq '.total_types' ~/.openclaw/workspace-invoice-agent/memory/known_invoices.json

# 3. 检查技能链接
ls -l ~/.openclaw/workspace-invoice-agent/skills/

# 4. 检查 Agent 注册
cat ~/.openclaw/agents/invoice-agent.json
```

请告诉我创建是否成功，以及验证结果。

---

## 📋 备用方案（如果主 Agent 无法执行）

如果主 Agent 无法直接执行 bash 命令，请告知我，我将提供手动创建的详细步骤。
