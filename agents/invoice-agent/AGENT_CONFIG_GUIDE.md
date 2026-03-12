# 发票童子甲（invoice-agent）配置方案

**日期**: 2026-03-12
**版本**: v3.0（全新升级）

---

## 一、子Agent 基础配置

| 项目 | 内容 |
|------|------|
| **名称** | 发票童子甲 |
| **ID** | invoice-agent |
| **角色** | 户部·发票司 |
| **工作空间** | `~/.openclaw/workspace-invoice-agent` |
| **依赖技能** | PaddleOCR-VL（v3.0+） |
| **状态** | ✅ 已配置完成 |
| **能力版本** | v3.0（支持PDF、批量处理） |

---

## 二、我如何使用这个子Agent（主Agent视角）

### 1. 触发条件

| 场景 | 动作 |
|------|------|
| 检测到发票图片 | 直接调用子agent处理 |
| 检测到PDF发票 | 直接调用子agent处理 |
| 用户说"发票发票" | 强制调用子agent |
| 用户说"我自己处理" | 我来处理 |
| 批量发票文件 | 调用子agent批量处理 |

### 2. 调用流程

```
① 收到发票文件（飞书发送/本地文件）
      ↓
② 判断文件类型（图片/PDF）
      ↓
③ 移动文件到子agent临时目录
      ~/.openclaw/workspace-invoice-agent/temp/
      ↓
④ 调用 sessions_spawn
      sessions_spawn(
          agentId="invoice-agent",
          mode="run",
          task="请处理发票文件: /absolute/path/to/file",
          cwd="~/.openclaw/workspace-invoice-agent",
          timeoutSeconds=300  # PDF可能需要更长时间
      )
      ↓
⑤ 接收返回结果
      ↓
⑥ 展示给用户
```

### 3. 关键规则

#### 🚫 不存文件在我这边
- **移动后交给子agent**
- 不要在主agent工作区保留发票文件

#### 📍 必须用绝对路径
- 图片/PDF路径必须是绝对路径
- 写在 task 参数里

#### ❌ 不用 attachments
- **当前被禁用**
- 不要尝试传递附件参数

#### 🚀 少问多做
- 能用就用，不打扰用户
- 自动判断和处理

### 4. 调用示例

#### 单张发票（图片）
```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="请处理这张发票图片: /Users/daodao/Documents/invoice_001.png",
    cwd="~/.openclaw/workspace-invoice-agent",
    timeoutSeconds=120
)
```

#### 单张发票（PDF）
```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="请处理这个PDF发票: /Users/daodao/Documents/invoices.pdf",
    cwd="~/.openclaw/workspace-invoice-agent",
    timeoutSeconds=300  # PDF需要更长时间
)
```

#### 批量发票（混合格式）
```python
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="""请批量处理以下发票文件:
- /Users/daodao/Documents/invoice_001.png
- /Users/daodao/Documents/invoice_002.jpg
- /Users/daodao/Documents/invoices.pdf
- /Users/daodao/Documents/invoice_003.webp

输出格式: CSV
保存位置: ~/.openclaw/workspace-invoice-agent/output/""",
    cwd="~/.openclaw/workspace-invoice-agent",
    timeoutSeconds=600  # 批量处理需要更长时间
)
```

### 5. 返回结果格式

#### 成功返回
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
      "confidence": 0.95,
      "validation": {
        "valid": true,
        "missing": []
      }
    }
  ],
  "output_file": "~/.openclaw/workspace-invoice-agent/output/2026-03-12_invoices.csv",
  "statistics": {
    "by_type": {
      "vat_special": 2,
      "vat_common": 2,
      "electronic": 1
    },
    "success_rate": 1.0,
    "avg_confidence": 0.92
  }
}
```

#### 失败返回
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

## 三、子Agent如何干活（发票童子甲视角）

### 1. 启动流程

```
① 接收任务
      ↓
② 检查 PaddleOCR-VL 技能可用性
      │ - 调用 health_check()
      │ - 验证服务版本（需要v3.0+）
      ↓
③ 读取文件（支持图片和PDF）
      │ - 图片: 直接读取
      │ - PDF: 自动转换为图片（每页一张）
      ↓
④ OCR识别
      │ - 单文件: recognize_document()
      │ - 批量: batch_recognize()
      │ - PDF: 逐页识别后合并
      ↓
⑤ 分类发票类型
      │ - 自动判断（4种已知类型）
      │ - 未知类型触发学习
      ↓
⑥ 提取字段
      │ - 根据类型提取对应字段
      │ - 验证必填字段
      ↓
⑦ 生成结果/表格
      │ - CSV/JSON/Excel格式
      │ - 添加元数据和置信度
      ↓
⑧ 清理/归档
      │ - 临时文件自动清理
      │ - 学习数据持久化
      ↓
⑨ 返回结果给主Agent
      │ - 标准JSON格式
      │ - 包含统计信息
```

### 2. 工作能力（v3.0升级）

#### 🎯 识别能力

| 能力 | 说明 |
|------|------|
| **支持格式** | PNG, JPG, JPEG, WebP, BMP, GIF, TIFF, PDF |
| **识别类型** | 4种发票（增值税专票、普票、电子发票、定额发票） |
| **PDF支持** | ✅ 单页/多页PDF自动转换 |
| **批量处理** | ✅ 最多50个文件/次 |
| **混合格式** | ✅ 图片+PDF混合处理 |
| **学习能力** | ✅ 自动学习新发票类型 |

#### 🔧 字段提取

| 发票类型 | 提取字段数 | 主要字段 |
|---------|-----------|---------|
| 增值税专票 | 10-12 | 发票代码、号码、日期、购买方、销售方、金额、税额、价税合计 |
| 增值税普票 | 6-8 | 发票代码、号码、日期、购买方、销售方、价税合计 |
| 电子发票 | 7-9 | 发票代码、号码、日期、购买方、销售方、价税合计、校验码 |
| 定额发票 | 4-5 | 发票代码、号码、金额、省份 |

#### 📦 输出格式

- **CSV**: 表格格式，适合Excel打开
- **JSON**: 结构化数据，适合程序处理
- **Excel**: .xlsx格式，包含格式化

### 3. PDF处理细节

#### PDF识别流程
```
1. 接收PDF文件
2. 使用 pdf_utils.pdf_to_images() 转换
3. 逐页OCR识别
4. 合并所有页面文字
5. 提取字段（以第一页为准）
6. 返回完整结果
```

#### PDF配置
```python
# PDF处理参数
{
    "dpi": 200,              # 分辨率
    "max_pages": 100,        # 最大页数
    "merge_pages": True,     # 是否合并页面文字
    "timeout_per_page": 30   # 每页超时时间（秒）
}
```

### 4. 批量处理细节

#### 批量处理流程
```
1. 接收文件列表（最多50个）
2. 按类型分组（图片/PDF）
3. 批量调用OCR API
4. 实时进度回调
5. 错误处理和重试
6. 汇总结果和统计
7. 生成输出文件
```

#### 批量处理配置
```python
# 批量处理参数
{
    "max_batch_size": 50,    # 最大文件数
    "parallel_workers": 3,   # 并发数
    "retry_failed": True,    # 失败重试
    "max_retries": 2,        # 最大重试次数
    "progress_callback": True # 进度回调
}
```

---

## 四、注意事项

### ⚠️ 重要限制

| 限制项 | 说明 |
|--------|------|
| **attachments参数** | ❌ 当前被禁用，无法直接传附件 |
| **文件路径** | 必须用绝对路径，写在task参数里 |
| **文件移动** | 调用前先把文件移到workspace/temp/ |
| **超时设置** | 单文件120秒，PDF 300秒，批量600秒 |
| **文件大小** | 单文件 ≤ 50MB |
| **PDF页数** | ≤ 100页 |

### 📋 调用前检查清单

- [ ] 文件已移动到 workspace/temp/
- [ ] 使用绝对路径
- [ ] 文件类型受支持（PNG/JPG/PDF等）
- [ ] 文件大小 ≤ 50MB
- [ ] PDF页数 ≤ 100页
- [ ] 批量文件 ≤ 50个
- [ ] 超时时间设置合理

### 🔧 故障排除

#### OCR服务不可用
```bash
# 检查服务状态
curl http://localhost:8001/health

# 启动服务
cd /Users/daodao/dsl/PaddleOCR-VL
./scripts/start_on_demand.sh
```

#### PDF处理失败
- 检查PDF是否加密
- 检查PDF页数是否超限
- 检查临时目录权限

#### 批量处理超时
- 减少批量文件数量
- 增加timeout参数
- 检查网络连接

---

## 五、升级日志

### v3.0（2026-03-12）

#### ✨ 新增功能

- ✅ **PDF支持**: 完整支持PDF发票识别
- ✅ **批量处理**: 最多50个文件/次
- ✅ **混合格式**: 图片+PDF混合处理
- ✅ **进度回调**: 实时处理进度
- ✅ **内存监控**: 资源使用监控

#### 🚀 性能提升

- 识别速度: **7秒 → 1.22秒**（+474%）
- 支持格式: **4种 → 11种**（+175%）
- 批量能力: **新增**，50文件/次

#### 📝 配置变更

- 更新 `supported_formats`: 新增PDF等7种格式
- 更新 `max_batch_size`: 10 → 50
- 更新 `timeout`: 根据文件类型动态调整

---

## 六、快速参考

### 常用命令

```bash
# 启动PaddleOCR-VL服务
cd /Users/daodao/dsl/PaddleOCR-VL
./scripts/start_on_demand.sh

# 检查服务状态
curl http://localhost:8001/health

# 停止服务
./scripts/stop_services.sh

# 调用子agent（单文件）
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="请处理发票: /absolute/path/to/file",
    cwd="~/.openclaw/workspace-invoice-agent",
    timeoutSeconds=120
)

# 调用子agent（批量）
sessions_spawn(
    agentId="invoice-agent",
    mode="run",
    task="批量处理: /path/to/file1.png, /path/to/file2.pdf",
    cwd="~/.openclaw/workspace-invoice-agent",
    timeoutSeconds=600
)
```

### 路径参考

```
PaddleOCR-VL项目:    /Users/daodao/dsl/PaddleOCR-VL
Agent工作空间:        ~/.openclaw/workspace-invoice-agent
临时文件目录:         ~/.openclaw/workspace-invoice-agent/temp/
输出文件目录:         ~/.openclaw/workspace-invoice-agent/output/
配置文件:             ~/.openclaw/workspace-invoice-agent/config.json
```

---

**配置方案版本**: v3.0
**最后更新**: 2026-03-12
**维护者**: PaddleOCR-VL Team
