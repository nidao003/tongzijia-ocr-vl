# 发票字段详细定义

本文档定义了每种发票类型的详细字段列表和输出格式。

---

## 📋 增值税专用发票（vat_special）

### 必填字段

| 字段代码 | 字段名称 | 说明 | 示例 |
|---------|---------|------|------|
| `invoice_code` | 发票代码 | 10-12位数字 | 1100XXXXXXXX |
| `invoice_no` | 发票号码 | 8位数字 | 12345678 |
| `invoice_date` | 开票日期 | YYYY-MM-DD | 2026-03-11 |
| `buyer_name` | 购买方名称 | 企业全称 | 北京某某科技有限公司 |
| `buyer_tax_id` | 购买方纳税人识别号 | 18-20位 | 91110000XXXXXXXXXX |
| `seller_name` | 销售方名称 | 企业全称 | 上海某某贸易有限公司 |
| `seller_tax_id` | 销售方纳税人识别号 | 18-20位 | 91310000XXXXXXXXXX |
| `amount` | 金额 | 不含税金额 | 1000.00 |
| `tax_rate` | 税率 | 百分比 | 13% |
| `tax_amount` | 税额 | | 130.00 |
| `total_amount` | 价税合计 | 含税总额 | 1130.00 |

### 可选字段

| 字段代码 | 字段名称 | 说明 | 示例 |
|---------|---------|------|------|
| `buyer_address_phone` | 购买方地址电话 | | 北京市朝阳区xxx电话12345678 |
| `buyer_bank_account` | 购买方开户行账户 | | 招行北京分行xxx账号 |
| `seller_address_phone` | 销售方地址电话 | | 上海市浦东新区xxx |
| `seller_bank_account` | 销售方开户行账户 | | 工行上海分行xxx |
| `remark` | 备注 | | 货物已收到 |
| `payer` | 收款人 | | 张三 |
| `reviewer` | 复核 | | 李四 |
| `drawer` | 开票人 | | 王五 |

---

## 📋 增值税普通发票（vat_common）

### 必填字段

| 字段代码 | 字段名称 | 说明 | 示例 |
|---------|---------|------|------|
| `invoice_code` | 发票代码 | 10-12位数字 | 1100XXXXXXXX |
| `invoice_no` | 发票号码 | 8位数字 | 12345678 |
| `invoice_date` | 开票日期 | YYYY-MM-DD | 2026-03-11 |
| `seller_name` | 销售方名称 | 企业全称 | 北京某某超市有限公司 |
| `total_amount` | 价税合计 | 含税总额 | 500.00 |

### 可选字段

| 字段代码 | 字段名称 | 说明 | 示例 |
|---------|---------|------|------|
| `buyer` | 购买方 | 个人或企业名称 | 张三 / 北京某某公司 |
| `seller_tax_id` | 销售方纳税人识别号 | | 91110000XXXXXXXXXX |
| `seller_address_phone` | 销售方地址电话 | | |
| `remark` | 备注 | | |
| `project_name` | 项目名称 | | 办公用品 |
| `drawer` | 开票人 | | |

---

## 📋 电子发票（electronic）

### 必填字段

| 字段代码 | 字段名称 | 说明 | 示例 |
|---------|---------|------|------|
| `invoice_code` | 发票代码 | 10-12位数字 | 031001800111 |
| `invoice_no` | 发票号码 | 8位数字 | 12345678 |
| `invoice_date` | 开票日期 | YYYY-MM-DD | 2026-03-11 |
| `seller_name` | 销售方名称 | 企业全称 | 北京某某科技有限公司 |
| `total_amount` | 价税合计 | 含税总额 | 299.00 |

### 可选字段

| 字段代码 | 字段名称 | 说明 | 示例 |
|---------|---------|------|------|
| `buyer` | 购买方 | | 个人 |
| `check_code` | 校验码 | 20位数字 | 12345678901234567890 |
| `seller_tax_id` | 销售方纳税人识别号 | | |
| `remark` | 备注 | | |
| `download_url` | 下载地址 | | https://... |

---

## 📋 定额发票（quota）

### 必填字段

| 字段代码 | 字段名称 | 说明 | 示例 |
|---------|---------|------|------|
| `invoice_code` | 发票代码 | | 01XXXXXXXX |
| `invoice_no` | 发票号码 | | 12345678 |
| `amount` | 金额 | | 100.00 |

### 可选字段

| 字段代码 | 字段名称 | 说明 | 示例 |
|---------|---------|------|------|
| `province` | 省份 | | 北京 |
| `city` | 城市 | | 北京市 |
| `industry` | 行业 | | 餐饮业 |
| `invoice_date` | 开票日期 | | 2026-03-11 |
| `valid_period` | 有效期 | | 2026年度 |

---

## 📊 表格输出格式

### CSV 格式示例

```csv
文件名,发票类型,发票代码,发票号码,开票日期,购买方,购买方税号,销售方,销售方税号,金额,税率,税额,价税合计,备注,置信度
invoice1.png,增值税专用发票,1100123456,12345678,2026-03-11,北京科技有限公司,91110000XXXXXXXXXX,上海贸易公司,91310000XXXXXXXXXX,1000.00,13%,130.00,1130.00,货已收,0.95
invoice2.png,增值税普通发票,1100123457,87654321,2026-03-10,张三,,北京超市,91110000YYYYYYYYYY,,,500.00,,0.92
invoice3.png,电子发票,031001800111,12345679,2026-03-09,个人,,餐饮公司,91110000ZZZZZZZZZ,,,299.00,0.90
```

### Excel 格式示例

| 文件名 | 发票类型 | 发票代码 | 发票号码 | 开票日期 | 购买方 | 销售方 | 金额 | 税额 | 价税合计 | 置信度 |
|--------|---------|---------|---------|---------|--------|--------|------|------|----------|--------|
| invoice1.png | 增值税专用发票 | 1100XXXXXXXX | 12345678 | 2026-03-11 | 北京科技有限公司 | 上海贸易公司 | 1000.00 | 130.00 | 1130.00 | 0.95 |
| invoice2.png | 增值税普通发票 | 1100XXXXXXXX | 87654321 | 2026-03-10 | 张三 | 北京超市 | 500.00 | - | 500.00 | 0.92 |

### JSON 格式示例

```json
{
  "processing_time": "2026-03-11T23:30:00",
  "summary": {
    "total_invoices": 3,
    "by_type": {
      "vat_special": 1,
      "vat_common": 1,
      "electronic": 1
    },
    "total_amount": 1929.00,
    "avg_confidence": 0.92
  },
  "invoices": [
    {
      "filename": "invoice1.png",
      "invoice_type": "vat_special",
      "invoice_type_name": "增值税专用发票",
      "confidence": 0.95,
      "fields": {
        "invoice_code": "1100123456",
        "invoice_no": "12345678",
        "invoice_date": "2026-03-11",
        "buyer_name": "北京科技有限公司",
        "buyer_tax_id": "91110000XXXXXXXXXX",
        "seller_name": "上海贸易公司",
        "seller_tax_id": "91310000XXXXXXXXXX",
        "amount": "1000.00",
        "tax_rate": "13%",
        "tax_amount": "130.00",
        "total_amount": "1130.00",
        "remark": "货已收"
      },
      "validation": {
        "required_fields_present": true,
        "missing_fields": [],
        "valid": true
      }
    }
  ]
}
```

---

## 🔍 字段验证规则

### 数字字段验证

- **金额类字段**：必须包含数字，可有小数点
- **代码号码**：纯数字，固定长度
- **税号**：18-20位，可能是字母+数字

### 日期字段验证

- 格式：YYYY-MM-DD 或 YYYY年MM月DD日
- 必须是有效日期
- 不能晚于当前日期

### 文本字段验证

- 不能为空（必填字段）
- 去除首尾空格
- 特殊字符处理

---

## 📁 输出文件位置

默认输出目录：`~/invoices_output/`

文件命名规则：
- CSV: `YYYY-MM-DD_invoices.csv`
- Excel: `YYYY-MM-DD_invoices.xlsx`
- JSON: `YYYY-MM-DD_invoices.json`

---

## 🎯 完整示例

### 输入

```python
sessions_spawn(
    agent="invoice-agent",
    task="batch_process",
    params={
        "image_paths": [
            "/path/to/invoice1.png",
            "/path/to/invoice2.png"
        ],
        "output_format": "csv"
    }
)
```

### 输出文件：`~/invoices_output/2026-03-11_invoices.csv`

```csv
文件名,发票类型,发票代码,发票号码,开票日期,购买方,购买方税号,销售方,销售方税号,金额,税率,税额,价税合计,备注,置信度
invoice1.png,增值税专用发票,1100123456,12345678,2026-03-11,北京科技有限公司,91110000XXXXXXXXXX,上海贸易公司,91310000XXXXXXXXXX,1000.00,13%,130.00,1130.00,货已收,0.95
invoice2.png,增值税普通发票,1100123457,87654321,2026-03-10,张三,,北京超市,91110000YYYYYYYYYY,,,500.00,,0.92
```

### 同时返回的 JSON 结果

```json
{
  "success": true,
  "processed_count": 2,
  "output_file": "/Users/xxx/invoices_output/2026-03-11_invoices.csv",
  "statistics": {
    "total_amount": 1630.00,
    "avg_confidence": 0.935
  }
}
```

---

**字段定义版本**: 1.0.0
**最后更新**: 2026-03-11
