# 📖 OpenClaw 主 Agent 文档阅读指南

> **告诉 OpenClaw 主 Agent 应该阅读哪些文档，以及阅读顺序**

---

## 🎯 核心文档（必读）

OpenClaw 主 Agent **必须阅读**以下文档：

### 第 1 优先级：配置指南

```
/Users/daodao/dsl/PaddleOCR-VL/agents/MAIN_AGENT_SETUP_GUIDE.md
```

**内容**：
- ✅ 完整的配置步骤（5步）
- ✅ 技能配置说明
- ✅ 验证清单
- ✅ 使用说明
- ✅ 决策机制简介

**作用**：让主 Agent 知道如何创建和配置 invoice-agent

---

### 第 2 优先级：决策机制

```
/Users/daodao/dsl/PaddleOCR-VL/agents/DECISION_GUIDE.md
```

**内容**：
- ✅ 如何判断何时使用子 Agent
- ✅ 如何向用户询问
- ✅ 询问模板和话术
- ✅ 决策树和最佳实践

**作用**：让主 Agent 知道如何向用户推荐使用子 Agent

---

## 📋 完整阅读顺序

### 阶段 1：配置（首次使用）

```
1. MAIN_AGENT_SETUP_GUIDE.md
   ↓
   执行配置步骤
   ↓
   验证配置完成
```

### 阶段 2：学习决策机制（配置完成后）

```
2. DECISION_GUIDE.md
   ↓
   理解决策逻辑
   ↓
   学习询问话术
   ↓
   测试决策流程
```

### 阶段 3：深入了解（可选）

```
3. SOUL.md
   └─ 子 Agent 的行为规范

4. FIELD_DEFINITIONS.md
   └─ 详细的字段定义

5. REPORTING_GUIDE.md
   └─ 汇报机制详解

6. SKILL_REQUIREMENTS.md
   └─ 技能检查详解
```

---

## 🎯 快速开始

### 给 OpenClaw 的指令

```
请阅读以下文档来配置 invoice-agent 子 Agent：

1. 首先阅读配置指南：
   /Users/daodao/dsl/PaddleOCR-VL/agents/MAIN_AGENT_SETUP_GUIDE.md

2. 然后阅读决策机制：
   /Users/daodao/dsl/PaddleOCR-VL/agents/DECISION_GUIDE.md

配置完成后，请告诉我：
1. 配置是否成功
2. 是否有任何问题
```

---

## 📊 文档关系图

```
主 Agent 入口
    │
    ├─→ MAIN_AGENT_SETUP_GUIDE.md (必读)
    │   ├─→ 配置步骤
    │   ├─→ 技能配置
    │   └─→ 决策机制简介
    │
    └─→ DECISION_GUIDE.md (必读)
        ├─→ 决策逻辑
        ├─→ 询问模板
        └─→ 最佳实践
    │
    ├─→ SOUL.md (参考)
    │   └─→ Agent 行为规范
    │
    ├─→ FIELD_DEFINITIONS.md (参考)
    │   └─→ 字段定义详情
    │
    ├─→ REPORTING_GUIDE.md (参考)
    │   └─→ 汇报机制详解
    │
    └─→ SKILL_REQUIREMENTS.md (参考)
        └─> 技能检查详解
```

---

## 💡 关键要点总结

### 配置要点

1. **只依赖一个技能**：PaddleOCR-VL
2. **每次任务前检查技能**：如果不可用就汇报
3. **通过 sessions_spawn 调用**：不使用 HTTP API
4. **子 Agent 会主动汇报**：学习、更新、性能变化

### 决策要点

1. **批量处理（3+张）**：推荐使用子 Agent
2. **需要详细字段**：推荐使用子 Agent
3. **需要表格文件**：必须使用子 Agent
4. **简单查询（1-2张）**：主 Agent 自己处理
5. **总是询问用户**：让用户明确选择

### 询问话术要点

1. **使用子 Agent 的中文名称**："发票处理专员"
2. **说明子 Agent 的能力**：批量、详细、表格、学习
3. **给出明确的选项**：选项 1 / 选项 2
4. **标注推荐选项**：基于任务特点推荐
5. **尊重用户选择**：选择后立即执行

---

## ✅ 配置完成后的验证

### 主 Agent 自检清单

```
配置完成后，请确认：

□ 已创建工作空间
□ 已复制所有文件
□ 已初始化学习系统
□ 已配置技能引用
□ 已注册子 Agent
□ 已启动 PaddleOCR-VL 服务
□ 已阅读决策机制文档
□ 理解询问用户的模板
□ 准备好处理发票任务
```

---

## 🎯 实际使用流程

### 用户请求处理

```
用户: "帮我处理这5张发票"
    ↓
主 Agent: 检测任务特点
    ├─→ 5张发票 → 批量任务
    ├─→ 建议使用子 Agent
    └─→ 询问用户
    ↓
用户: "使用发票处理专员"
    ↓
主 Agent: 调用子 Agent
    sessions_spawn(
        agent="invoice-agent",
        task="batch_process",
        params={...}
    )
    ↓
子 Agent: 处理发票
    ├─→ OCR 识别
    ├─→ 分类
    ├─→ 提取字段
    ├─→ 生成表格
    └─→ 汇报结果
    ↓
主 Agent: 接收结果
    ↓
主 Agent: 返回给用户
    ✅ 完成
```

---

## 📞 遇到问题？

### 配置问题

参考 `MAIN_AGENT_SETUP_GUIDE.md` 的故障排除部分

### 决策问题

参考 `DECISION_GUIDE.md` 的具体场景和话术

### 技能问题

参考 `SKILL_REQUIREMENTS.md` 的技能检查和汇报

---

## 🎉 总结

**最重要的两个文档**：

1. **MAIN_AGENT_SETUP_GUIDE.md** - 配置子 Agent
2. **DECISION_GUIDE.md** - 决策何时使用子 Agent

**核心原则**：

- ✅ 配置完成后，主动向用户推荐使用子 Agent
- ✅ 使用子 Agent 的中文名称："**发票处理专员**"
- ✅ 明确说明子 Agent 的能力和优势
- ✅ 让用户做出明确的选择
- ✅ 尊重用户的选择并立即执行

---

**文档版本**: 1.0.0
**最后更新**: 2026-03-11
**适用对象**: OpenClaw 主 Agent
