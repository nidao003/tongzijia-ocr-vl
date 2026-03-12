# 发票童子甲 - 快速参考

**版本**: v3.0 | **更新**: 2026-03-12

---

## 📥 给 OpenClaw 的安装指令

```
请安装/升级发票童子甲（invoice-agent）v3.0
路径：/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent/
依赖：paddleocr-vl 技能（本地）+ email 技能（可选，主系统）
```

---

## 🎯 我是谁

- **名称**: 发票童子甲
- **ID**: invoice-agent
- **职责**: 发票识别、字段提取、数据整理
- **工作空间**: `~/.openclaw/workspace-invoice-agent`

---

## ✨ v3.0 新能力

| 能力 | 说明 |
|------|------|
| **PDF支持** | ✅ 单页/多页PDF自动识别 |
| **批量处理** | ✅ 最多50个文件/次 |
| **混合格式** | ✅ 图片+PDF混合处理 |
| **速度提升** | ⚡ 1.22秒/张（提升474%） |
| **格式支持** | 11种（PNG/JPG/PDF/WebP/BMP等） |

---

## 🚀 如何调用我

### 单张发票（图片/PDF）
```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="请处理发票: /absolute/path/to/file.png",
    cwd="~/.openclaw/workspace-invoice-agent",
    timeoutSeconds=120
)
```

### PDF发票
```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="请处理PDF发票: /absolute/path/to/invoice.pdf",
    cwd="~/.openclaw/workspace-invoice-agent",
    timeoutSeconds=300  # PDF需要更长时间
)
```

### 批量发票（混合格式）
```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="批量处理: /path/file1.png, /path/file2.pdf, /path/file3.jpg",
    cwd="~/.openclaw/workspace-invoice-agent",
    timeoutSeconds=600
)
```

---

## ⚠️ 重要规则

1. **❌ 不用 attachments** - 当前被禁用
2. **📍 必须用绝对路径** - 写在 task 参数里
3. **🚀 先移动文件** - 移到 workspace/temp/ 后再调用
4. **⏱️ 设置合理超时** - 单文件120秒，PDF 300秒，批量600秒

---

## 📋 支持格式

**图片**: PNG, JPG, JPEG, WebP, BMP, GIF, TIFF
**文档**: PDF（最多100页）

**限制**:
- 单文件 ≤ 50MB
- PDF ≤ 100页
- 批量 ≤ 50文件

---

## 📤 返回格式

### 成功
```json
{
  "success": true,
  "processed_count": 5,
  "results": [...],
  "statistics": {...}
}
```

### 失败
```json
{
  "success": false,
  "error": "错误原因",
  "action_required": "解决方法"
}
```

---

## 🔧 服务依赖

- **PaddleOCR-VL**: v3.0+
- **服务地址**: http://localhost:8001
- **启动脚本**: `/Users/daodao/dsl/PaddleOCR-VL/scripts/start_on_demand.sh`

---

## 📚 完整文档

- 配置指南: `AGENT_CONFIG_GUIDE.md`
- 灵魂文档: `SOUL.md`
- 技能说明: `skills/invoice-processor/SKILL.md`

---

**快速参考 v3.0** | 最后更新: 2026-03-12
