---
name: invoice-processor
description: 发票类型识别和智能字段提取技能
version: 1.0.0
author: PaddleOCR-VL Integration
tags: [invoice, ocr, field-extraction, classification]
compatibleAgents: [invoice-agent, main-agent]
---

# 发票处理技能

本技能提供发票类型自动识别和关键字段智能提取能力，配合 PaddleOCR-VL 使用。

## 功能概述

- **自动分类**：根据 OCR 识别文本自动判断发票类型
- **智能提取**：根据发票类型提取对应的关键字段
- **数据验证**：对提取的字段进行格式验证和清洗
- **格式转换**：支持多种输出格式（CSV、JSON、Excel）

## 输入参数

### 单张发票处理
```python
{
    "image_path": "/path/to/invoice.png",
    "output_format": "csv",  # 可选: csv, json, excel
    "auto_classify": true    # 是否自动分类，默认 true
}
```

### 批量发票处理
```python
{
    "image_paths": [
        "/path/to/invoice1.png",
        "/path/to/invoice2.png"
    ],
    "output_format": "csv",
    "auto_classify": true,
    "merge_output": true    # 是否合并到一个文件
}
```

## 处理流程

### 1. OCR 识别
调用 PaddleOCR-VL 获取发票文本内容：
```python
from paddleocr_tool import quick_recognize

text = quick_recognize(image_path)
```

### 2. 发票类型分类
```python
INVOICE_TYPES = {
    "vat_special": {
        "name": "增值税专用发票",
        "keywords": ["增值税专用发票", "专用发票"],
        "priority": 1
    },
    "vat_common": {
        "name": "增值税普通发票",
        "keywords": ["增值税普通发票", "普通发票"],
        "priority": 2
    },
    "electronic": {
        "name": "电子发票",
        "keywords": ["电子发票", "增值税电子发票"],
        "priority": 3
    },
    "quota": {
        "name": "定额发票",
        "keywords": ["定额发票"],
        "priority": 4
    }
}
```

### 3. 字段提取规则

#### 增值税专用发票
```python
FIELDS = {
    "invoice_code": {"pattern": r"发票代码[：:]\s*(\d+)", "required": True},
    "invoice_no": {"pattern": r"发票号码[：:]\s*(\d+)", "required": True},
    "invoice_date": {"pattern": r"开票日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)", "required": True},
    "buyer_name": {"pattern": r"购买方[名称|名称及纳税人识别号][：:]\s*([^\n]+)", "required": True},
    "buyer_tax_id": {"pattern": r"纳税人识别号[：:]\s*([A-Z0-9]+)", "required": False},
    "seller_name": {"pattern": r"销售方[名称|名称及纳税人识别号][：:]\s*([^\n]+)", "required": True},
    "seller_tax_id": {"pattern": r"纳税人识别号[：:]\s*([A-Z0-9]+)", "required": False},
    "amount": {"pattern": r"金额[：:]\s*[¥￥]?([\d,]+\.?\d*)", "required": True},
    "tax_rate": {"pattern": r"税率[：:]\s*(\d+%)", "required": False},
    "tax_amount": {"pattern": r"税额[：:]\s*[¥￥]?([\d,]+\.?\d*)", "required": True},
    "total_amount": {"pattern": r"价税合计[：:]\s*[¥￥]?([\d,]+\.?\d*)", "required": True},
    "remark": {"pattern": r"备注[：:]\s*([^\n]*)", "required": False}
}
```

#### 增值税普通发票
```python
FIELDS = {
    "invoice_code": {"pattern": r"发票代码[：:]\s*(\d+)", "required": True},
    "invoice_no": {"pattern": r"发票号码[：:]\s*(\d+)", "required": True},
    "invoice_date": {"pattern": r"开票日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)", "required": True},
    "buyer": {"pattern": r"购买方[：:]\s*([^\n]+)", "required": False},
    "seller": {"pattern": r"销售方[：:]\s*([^\n]+)", "required": True},
    "total_amount": {"pattern": r"价税合计[：:]\s*[¥￥]?([\d,]+\.?\d*)", "required": True},
    "remark": {"pattern": r"备注[：:]\s*([^\n]*)", "required": False}
}
```

#### 电子发票
```python
FIELDS = {
    "invoice_code": {"pattern": r"发票代码[：:]\s*(\d+)", "required": True},
    "invoice_no": {"pattern": r"发票号码[：:]\s*(\d+)", "required": True},
    "invoice_date": {"pattern": r"开票日期[：:]\s*(\d{4}-\d{2}-\d{2})", "required": True},
    "buyer": {"pattern": r"购买方[：:]\s*([^\n]+)", "required": False},
    "seller": {"pattern": r"销售方[：:]\s*([^\n]+)", "required": True},
    "total_amount": {"pattern": r"价税合计[：:]\s*[¥￥]?([\d,]+\.?\d*)", "required": True},
    "check_code": {"pattern": r"校验码[：:]\s*(\d+)", "required": False}
}
```

#### 定额发票
```python
FIELDS = {
    "invoice_code": {"pattern": r"发票代码[：:]\s*(\d+)", "required": True},
    "invoice_no": {"pattern": r"发票号码[：:]\s*(\d+)", "required": True},
    "amount": {"pattern": r"金额[：:]\s*[¥￥]?([\d,]+\.?\d*)", "required": True},
    "province": {"pattern": r"(北京|上海|广东|深圳)等", "required": False}
}
```

### 4. 数据清洗和验证

```python
def clean_field(field_name, value):
    """字段数据清洗"""
    if field_name.endswith("_date"):
        # 统一日期格式为 YYYY-MM-DD
        return normalize_date(value)
    elif field_name.endswith("_amount"):
        # 清洗金额格式，去除逗号和符号
        return clean_amount(value)
    elif field_name.endswith("_no") or field_name.endswith("_code"):
        # 去除空格和特殊字符
        return value.strip().replace(" ", "")
    return value.strip()

def validate_fields(fields, invoice_type):
    """字段验证"""
    required_fields = get_required_fields(invoice_type)
    missing = [f for f in required_fields if not fields.get(f)]
    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "confidence": calculate_confidence(fields, invoice_type)
    }
```

## 输出规范

### CSV 格式
```csv
文件名,发票类型,发票代码,发票号码,开票日期,购买方,销售方,金额,税额,价税合计,置信度
invoice1.png,增值税专用发票,1100XXXXXXXX,12345678,2026-03-11,公司A,公司B,1000.00,130.00,1130.00,0.95
```

### JSON 格式
```json
{
  "processing_time": "2026-03-11T22:00:00",
  "total_invoices": 2,
  "statistics": {
    "by_type": {
      "vat_special": 1,
      "vat_common": 1
    },
    "success_rate": 1.0,
    "avg_confidence": 0.915
  },
  "invoices": [
    {
      "filename": "invoice1.png",
      "invoice_type": "vat_special",
      "invoice_type_name": "增值税专用发票",
      "fields": {
        "invoice_code": "1100XXXXXXXX",
        "invoice_no": "12345678",
        "invoice_date": "2026-03-11",
        "buyer_name": "公司A",
        "seller_name": "公司B",
        "amount": "1000.00",
        "tax_amount": "130.00",
        "total_amount": "1130.00"
      },
      "confidence": 0.95,
      "validation": {
        "valid": true,
        "missing": []
      }
    }
  ]
}
```

## 使用示例

### 示例 1：处理单张发票
```python
result = process_invoice({
    "image_path": "/path/to/invoice.png",
    "output_format": "json"
})
print(result)
# {
#   "filename": "invoice.png",
#   "type": "vat_special",
#   "fields": {...},
#   "confidence": 0.95
# }
```

### 示例 2：批量处理
```python
results = batch_process_invoices({
    "image_paths": [
        "/path/to/invoice1.png",
        "/path/to/invoice2.png"
    ],
    "output_format": "csv",
    "merge_output": true
})
# 输出文件: ./invoices_output/2026-03-11_invoices.csv
```

## 依赖与限制

- **依赖**：PaddleOCR-VL 服务（http://localhost:8001）
- **支持格式**：PNG, JPEG, WebP
- **最大文件大小**：10MB
- **处理速度**：约 7 秒/张
- **准确率**：标准发票 95%+，模糊发票 80%+

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| OCR 服务不可用 | 返回错误，建议检查服务状态 |
| 无法识别发票类型 | 标记为"未知"，提取所有可能字段 |
| 必填字段缺失 | 标记为验证失败，返回缺失字段列表 |
| 图片格式不支持 | 跳过该文件，记录错误 |

## 扩展性

如需支持新的发票类型，在 `INVOICE_TYPES` 中添加：
```python
"new_type": {
    "name": "新发票类型",
    "keywords": ["关键词1", "关键词2"],
    "priority": 5,
    "fields": {
        "field_name": {
            "pattern": r"正则表达式",
            "required": True/False
        }
    }
}
```
