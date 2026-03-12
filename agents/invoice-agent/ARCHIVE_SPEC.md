# 发票文件管理与归档规范

**版本**: 1.0
**日期**: 2026-03-12
**Agent**: invoice-agent

---

## 📂 目录结构设计

```
~/.openclaw/workspace-invoice-agent/
├── archive/                          # 发票归档目录
│   ├── 2026/
│   │   ├── 2026-03/                  # 按年月分类
│   │   │   ├── vat_special/          # 增值税专用发票
│   │   │   │   ├── 20260311_增值税专用发票_XXX公司_001.png
│   │   │   │   ├── 20260311_增值税专用发票_XXX公司_002.pdf
│   │   │   │   └── ...
│   │   │   ├── vat_common/           # 增值税普通发票
│   │   │   ├── electronic/           # 电子发票
│   │   │   └── quota/                # 定额发票
│   │   └── ...
│   └── 2025/
│       └── ...
│
├── temp/                             # 临时文件目录
│   └── [待处理文件]
│
├── output/                           # 输出目录
│   ├── 2026-03/                      # 按年月分类
│   │   ├── invoices_2026-03.csv      # 汇总表格
│   │   ├── invoices_2026-03.json
│   │   └── invoices_2026-03.xlsx
│   └── ...
│
└── memory/                           # 学习数据
    ├── invoice_index.json            # 发票索引（所有已处理发票）
    └── file_mapping.json             # 文件映射记录
```

---

## 📝 文件命名规范

### 命名格式（优化版 v2.0）

```
YYYYMMDD_金额(分)_发票号码_类型简称_开票方简称.{扩展名}
```

### 命名示例

```
20260311_100000_00534712_S_华为技术.png
20260312_50000_12345678_C_阿里云.jpg
20260315_30000_98765432_E_腾讯云.pdf
20260320_8000_11111111_Q_XX餐饮.png
```

### 命名规则

| 部分 | 说明 | 示例 | 来源 |
|------|------|------|------|
| **年月日** | YYYYMMDD 格式 | 20260311 | 发票开票日期 |
| **金额** | 金额（分，整数） | 100000 | 价税合计 × 100 |
| **发票号码** | 8位发票号 | 00534712 | 发票号码字段 |
| **类型简称** | 单字母类型码 | S/C/E/Q | 发票类型映射 |
| **开票方** | 销售方简称 | 华为技术 | 公司简称生成器 |
| **扩展名** | 原始文件扩展名 | .png/.pdf | 保持原格式 |

### 类型代码映射

| 代码 | 类型 | 英文 | 说明 |
|------|------|------|------|
| **S** | 增值税专用发票 | vat_special | Special |
| **C** | 增值税普通发票 | vat_common | Common |
| **E** | 电子发票 | electronic | Electronic |
| **Q** | 定额发票 | quota | Quota |
| **U** | 未知类型 | unknown | Unknown |

### 金额转换示例

| 原始金额 | 转换后（分） | 说明 |
|---------|-------------|------|
| ¥1,000.00 | 100000 | 去除符号和小数点，乘100 |
| ¥500.50 | 50050 | 保留精度 |
| ¥227,500.00 | 22750000 | 大额发票 |

### 交易方简称规则

```python
# 简称生成规则
def get_short_name(company_name):
    """
    从完整公司名生成简称

    规则：
    1. 去除行政区划（北京、上海等）
    2. 去除公司类型（有限公司、股份公司等）
    3. 保留核心品牌名（4-8个字符）
    4. 特殊公司使用约定俗成的简称

    示例：
    - "华为技术有限公司" → "华为技术"
    - "阿里巴巴（中国）有限公司" → "阿里云"
    - "腾讯科技（北京）有限公司" → "腾讯科技"
    - "中国移动通信集团浙江有限公司" → "浙江移动"
    """
    # 实现见下方代码
```

---

## 🔄 自动归档流程

### 触发时机

1. **单张发票处理完成后** → 立即归档
2. **批量发票处理完成后** → 批量归档
3. **邮箱下载完成后** → 批量归档

### 归档步骤

```python
"""
发票自动归档流程
"""

def archive_invoice(file_path, invoice_data):
    """
    归档单张发票（优化版 v2.0）

    Args:
        file_path: 原始文件路径
        invoice_data: 发票数据（包含识别结果）

    Returns:
        归档后的文件路径
    """
    # 1. 提取信息
    invoice_date = invoice_data['fields']['invoice_date']  # 2024-12-18
    invoice_type = invoice_data['invoice_type']            # vat_special
    invoice_no = invoice_data['fields']['invoice_no']      # 00534712
    total_amount = invoice_data['fields']['total_amount']  # "1000.00"
    company_name = invoice_data['fields'].get('seller_name') or invoice_data['fields'].get('buyer_name')

    # 2. 解析日期
    year_month = invoice_date[:7].replace('-', '')  # 2024-12 → 202412
    year_month_day = invoice_date.replace('-', '')    # 2024-12-18 → 20241218

    # 3. 生成公司简称
    short_name = get_short_name(company_name)  # "华为技术"

    # 4. 转换金额为分
    amount_cents = amount_to_cents(total_amount)  # "1000.00" → 100000

    # 5. 获取类型代码
    type_code = get_invoice_type_code(invoice_type)  # "vat_special" → "S"

    # 6. 构造新文件名（新格式）
    # 格式: YYYYMMDD_金额(分)_发票号码_类型简称_开票方简称
    original_ext = os.path.splitext(file_path)[1]
    new_filename = f"{year_month_day}_{amount_cents}_{invoice_no}_{type_code}_{short_name}{original_ext}"
    # 示例: 20241218_100000_00534712_S_华为技术.png

    # 7. 构造目标路径
    archive_dir = f"~/.openclaw/workspace-invoice-agent/archive/{year_month[:4]}/{year_month[4:]}/{invoice_type}/"
    os.makedirs(os.path.expanduser(archive_dir), exist_ok=True)

    target_path = os.path.join(archive_dir, new_filename)

    # 8. 移动文件
    shutil.move(file_path, os.path.expanduser(target_path))

    # 9. 更新索引
    update_invoice_index({
        'original_filename': os.path.basename(file_path),
        'new_filename': new_filename,
        'archive_path': target_path,
        'invoice_date': invoice_date,
        'invoice_type': invoice_type,
        'invoice_no': invoice_no,
        'amount': total_amount,
        'amount_cents': amount_cents,
        'company_name': company_name,
        'archived_at': datetime.now().isoformat()
    })

    return target_path
```

---

## 📧 邮箱监控配置

### 支持的邮箱协议

- **IMAP**（推荐）
- **POP3**

### 配置文件

```json
// ~/.openclaw/workspace-invoice-agent/email_config.json
{
  "enabled": true,
  "protocol": "imap",
  "server": "imap.gmail.com",
  "port": 993,
  "username": "your-email@gmail.com",
  "password": "app-password",  // 应用专用密码
  "inbox_folder": "INBOX",
  "mark_as_read": true,
  "download_attachments": true,

  "filters": {
    "subjects": ["发票", "invoice", "票据", "收据"],
    "senders": [],  // 空表示不限制发件人
    "attachment_types": [".pdf", ".png", ".jpg", ".jpeg"]
  },

  "schedule": {
    "enabled": true,
    "interval_minutes": 30,  // 每30分钟检查一次
    "batch_size": 50  // 每次最多处理50封邮件
  },

  "processing": {
    "auto_archive": true,
    "auto_classify": true,
    "generate_summary": true,
    "delete_after_archive": false  // 是否在归档后删除原邮件
  }
}
```

### 邮箱处理流程

```python
"""
邮箱监控和处理流程
"""

def process_email_invoices():
    """
    处理邮箱中的发票邮件
    """
    # 1. 连接邮箱
    mail = connect_email_server()

    # 2. 搜索未读邮件
    unread_emails = mail.search(['UNSEEN', 'SUBJECT', '发票'])

    # 3. 逐封处理
    downloaded_files = []
    for email in unread_emails:
        # 检查主题和发件人
        if is_invoice_email(email):
            # 下载附件
            for attachment in email.attachments:
                if is_invoice_file(attachment):
                    file_path = download_attachment(attachment)
                    downloaded_files.append(file_path)

            # 标记为已读
            email.mark_as_read()

    # 4. 批量识别发票
    if downloaded_files:
        results = batch_recognize(downloaded_files)

        # 5. 批量归档
        for file_path, result in zip(downloaded_files, results['results']):
            if result['success']:
                archive_invoice(file_path, result)

        # 6. 生成汇总表格
        summary_file = generate_summary(results)

        # 7. 通知用户
        notify_user(
            f"从邮箱下载并处理了 {len(downloaded_files)} 张发票",
            summary_file=summary_file
        )
```

---

## 📊 索引管理

### invoice_index.json

```json
{
  "last_updated": "2026-03-12T10:30:00Z",
  "total_invoices": 150,
  "by_type": {
    "vat_special": 60,
    "vat_common": 50,
    "electronic": 30,
    "quota": 10
  },
  "by_year": {
    "2026": 100,
    "2025": 50
  },
  "invoices": [
    {
      "id": "20260311_100000_00534712_S_华为技术",
      "original_filename": "invoice_001.png",
      "new_filename": "20260311_100000_00534712_S_华为技术.png",
      "archive_path": "archive/2026/03/vat_special/20260311_100000_00534712_S_华为技术.png",
      "invoice_date": "2026-03-11",
      "invoice_type": "vat_special",
      "invoice_type_name": "增值税专用发票",
      "invoice_code": "1500242720",
      "invoice_no": "00534712",
      "amount": "1000.00",
      "amount_cents": 100000,
      "company_name": "华为技术有限公司",
      "company_short_name": "华为技术",
      "archived_at": "2026-03-12T10:25:00Z"
    }
  ]
}
```

---

## 🔍 查询功能

### 按日期查询

```python
def query_by_date(start_date, end_date):
    """
    查询指定日期范围的发票

    Args:
        start_date: 开始日期（YYYY-MM-DD）
        end_date: 结束日期（YYYY-MM-DD）

    Returns:
        发票列表
    """
```

### 按类型查询

```python
def query_by_type(invoice_type):
    """
    查询指定类型的发票

    Args:
        invoice_type: 发票类型（vat_special, vat_common等）

    Returns:
        发票列表
    """
```

### 按公司查询

```python
def query_by_company(company_name):
    """
    查询指定公司的发票

    Args:
        company_name: 公司名称（支持模糊搜索）

    Returns:
        发票列表
    """
```

---

## 📋 配置文件

### archive_config.json

```json
{
  "archive_base": "~/.openclaw/workspace-invoice-agent/archive",
  "output_base": "~/.openclaw/workspace-invoice-agent/output",

  "naming": {
    "format": "{date}_{type}_{company}_{serial:03d}",
    "date_format": "YYYYMMDD",
    "serial_digits": 3
  },

  "directories": {
    "by_year": true,
    "by_month": true,
    "by_type": true
  },

  "company_short_names": {
    "华为技术有限公司": "华为技术",
    "阿里巴巴（中国）有限公司": "阿里云",
    "腾讯科技（北京）有限公司": "腾讯科技",
    "中国移动通信集团浙江有限公司": "浙江移动",
    "中国电信股份有限公司上海分公司": "上海电信"
  },

  "auto_cleanup": {
    "enabled": true,
    "temp_files_days": 7,
    "empty_folders": true
  }
}
```

---

## 🎯 实现计划

### Phase 1: 基础归档功能
- [x] 设计目录结构
- [x] 定义命名规范
- [ ] 实现自动归档函数
- [ ] 实现索引管理

### Phase 2: 邮箱集成
- [ ] 实现邮箱连接
- [ ] 实现邮件过滤
- [ ] 实现附件下载
- [ ] 实现定时检查

### Phase 3: 查询和统计
- [ ] 实现日期查询
- [ ] 实现类型查询
- [ ] 实现公司查询
- [ ] 实现统计报表

---

**规范版本**: 2.0
**生效日期**: 2026-03-12
**维护者**: invoice-agent
