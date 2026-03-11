#!/usr/bin/env python3
"""
发票处理 Agent - 学习系统初始化脚本

用于初始化自我学习所需的数据结构和配置
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace-invoice-agent"
MEMORY_DIR = WORKSPACE / "memory"
LEARNING_DIR = WORKSPACE / "skills" / "invoice-processor" / "learning"

# 创建目录
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
LEARNING_DIR.mkdir(parents=True, exist_ok=True)
(LEARNING_DIR / "invoice_templates").mkdir(exist_ok=True)
(LEARNING_DIR / "field_patterns").mkdir(exist_ok=True)
(LEARNING_DIR / "feedback").mkdir(exist_ok=True)


def init_known_invoices() -> Dict[str, Any]:
    """初始化已知发票类型数据库"""
    return {
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat(),
        "total_types": 4,
        "invoice_types": {
            "vat_special": {
                "id": "vat_special",
                "name": "增值税专用发票",
                "confidence": 0.95,
                "sample_count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": None,
                "keywords": ["增值税专用发票", "专用发票"],
                "features": {
                    "has_tax_rate": True,
                    "has_buyer_tax_id": True,
                    "has_seller_tax_id": True,
                    "layout": "standard"
                },
                "fields": {
                    "invoice_code": {
                        "required": True,
                        "patterns": [r"发票代码[：:]\s*(\d+)"],
                        "position_hint": "top_left"
                    },
                    "invoice_no": {
                        "required": True,
                        "patterns": [r"发票号码[：:]\s*(\d+)"],
                        "position_hint": "top_left"
                    },
                    "invoice_date": {
                        "required": True,
                        "patterns": [
                            r"开票日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
                            r"开票日期[：:]\s*(\d{4}-\d{2}-\d{2})"
                        ],
                        "position_hint": "top_right"
                    },
                    "buyer_name": {
                        "required": True,
                        "patterns": [
                            r"购买方[名称|名称及纳税人识别号][：:]\s*([^\n]+)"
                        ],
                        "position_hint": "middle_left"
                    },
                    "buyer_tax_id": {
                        "required": False,
                        "patterns": [r"纳税人识别号[：:]\s*([A-Z0-9]+)"],
                        "position_hint": "below_buyer_name"
                    },
                    "seller_name": {
                        "required": True,
                        "patterns": [
                            r"销售方[名称|名称及纳税人识别号][：:]\s*([^\n]+)"
                        ],
                        "position_hint": "middle_right"
                    },
                    "seller_tax_id": {
                        "required": False,
                        "patterns": [r"纳税人识别号[：:]\s*([A-Z0-9]+)"],
                        "position_hint": "below_seller_name"
                    },
                    "amount": {
                        "required": True,
                        "patterns": [r"金额[：:]\s*[¥￥]?([\d,]+\.?\d*)"],
                        "position_hint": "bottom_left"
                    },
                    "tax_rate": {
                        "required": False,
                        "patterns": [r"税率[：:]\s*(\d+%)"],
                        "position_hint": "near_amount"
                    },
                    "tax_amount": {
                        "required": True,
                        "patterns": [r"税额[：:]\s*[¥￥]?([\d,]+\.?\d*)"],
                        "position_hint": "near_amount"
                    },
                    "total_amount": {
                        "required": True,
                        "patterns": [r"价税合计[：:]\s*[¥￥]?([\d,]+\.?\d*)"],
                        "position_hint": "bottom_right"
                    },
                    "remark": {
                        "required": False,
                        "patterns": [r"备注[：:]\s*([^\n]*)"],
                        "position_hint": "bottom"
                    }
                },
                "extraction_rules": {
                    "strategy": "keyword_first",
                    "fallback": ["position", "regex", "fuzzy"],
                    "min_confidence": 0.7
                }
            },
            "vat_common": {
                "id": "vat_common",
                "name": "增值税普通发票",
                "confidence": 0.92,
                "sample_count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": None,
                "keywords": ["增值税普通发票", "普通发票"],
                "features": {
                    "has_tax_rate": False,
                    "has_buyer_tax_id": False,
                    "has_seller_tax_id": False,
                    "layout": "simplified"
                },
                "fields": {
                    "invoice_code": {"required": True, "patterns": [r"发票代码[：:]\s*(\d+)"]},
                    "invoice_no": {"required": True, "patterns": [r"发票号码[：:]\s*(\d+)"]},
                    "invoice_date": {
                        "required": True,
                        "patterns": [
                            r"开票日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)",
                            r"开票日期[：:]\s*(\d{4}-\d{2}-\d{2})"
                        ]
                    },
                    "buyer": {"required": False, "patterns": [r"购买方[：:]\s*([^\n]+)"]},
                    "seller": {"required": True, "patterns": [r"销售方[：:]\s*([^\n]+)"]},
                    "total_amount": {
                        "required": True,
                        "patterns": [r"价税合计[：:]\s*[¥￥]?([\d,]+\.?\d*)"]
                    },
                    "remark": {"required": False, "patterns": [r"备注[：:]\s*([^\n]*)"]}
                },
                "extraction_rules": {
                    "strategy": "keyword_first",
                    "fallback": ["regex", "fuzzy"],
                    "min_confidence": 0.7
                }
            },
            "electronic": {
                "id": "electronic",
                "name": "电子发票",
                "confidence": 0.90,
                "sample_count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": None,
                "keywords": ["电子发票", "增值税电子发票"],
                "features": {
                    "has_tax_rate": True,
                    "has_buyer_tax_id": False,
                    "has_seller_tax_id": True,
                    "layout": "digital"
                },
                "fields": {
                    "invoice_code": {"required": True, "patterns": [r"发票代码[：:]\s*(\d+)"]},
                    "invoice_no": {"required": True, "patterns": [r"发票号码[：:]\s*(\d+)"]},
                    "invoice_date": {
                        "required": True,
                        "patterns": [
                            r"开票日期[：:]\s*(\d{4}-\d{2}-\d{2})",
                            r"开票日期[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)"
                        ]
                    },
                    "buyer": {"required": False, "patterns": [r"购买方[：:]\s*([^\n]+)"]},
                    "seller": {"required": True, "patterns": [r"销售方[：:]\s*([^\n]+)"]},
                    "total_amount": {
                        "required": True,
                        "patterns": [r"价税合计[：:]\s*[¥￥]?([\d,]+\.?\d*)"]
                    },
                    "check_code": {"required": False, "patterns": [r"校验码[：:]\s*(\d+)"]}
                },
                "extraction_rules": {
                    "strategy": "keyword_first",
                    "fallback": ["regex"],
                    "min_confidence": 0.65
                }
            },
            "quota": {
                "id": "quota",
                "name": "定额发票",
                "confidence": 0.85,
                "sample_count": 0,
                "first_seen": datetime.now().isoformat(),
                "last_seen": None,
                "keywords": ["定额发票"],
                "features": {
                    "has_amount_only": True,
                    "layout": "simple"
                },
                "fields": {
                    "invoice_code": {"required": True, "patterns": [r"发票代码[：:]\s*(\d+)"]},
                    "invoice_no": {"required": True, "patterns": [r"发票号码[：:]\s*(\d+)"]},
                    "amount": {
                        "required": True,
                        "patterns": [r"金额[：:]\s*[¥￥]?([\d,]+\.?\d*)"]
                    },
                    "province": {
                        "required": False,
                        "patterns": ["(北京|上海|广东|深圳|江苏|浙江)"]
                    }
                },
                "extraction_rules": {
                    "strategy": "position_first",
                    "fallback": ["keyword"],
                    "min_confidence": 0.6
                }
            }
        },
        "unknown_types": [],
        "learning_state": {
            "enabled": True,
            "auto_learn": True,
            "min_samples_for_new_type": 3,
            "confidence_threshold": 0.7
        }
    }


def init_extraction_rules() -> Dict[str, Any]:
    """初始化提取规则配置"""
    return {
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat(),
        "field_extraction": {
            "strategy_priority": ["keyword", "regex", "position", "fuzzy"],
            "confidence_threshold": 0.7,
            "fallback_enabled": True,
            "multi_strategy": True
        },
        "type_classification": {
            "strategies": {
            "keyword": {
                "enabled": True,
                "weight": 0.5,
                "min_matches": 1
            },
            "layout": {
                "enabled": True,
                "weight": 0.3,
                "threshold": 0.6
            },
            "ml": {
                "enabled": False,  # 需要足够的训练数据后启用
                "weight": 0.2,
                "min_confidence": 0.7
            }
            },
            "min_confidence": 0.6
        },
        "data_cleaning": {
            "date_normalization": True,
            "amount_cleaning": True,
            "whitespace_removal": True,
            "empty_value_handling": "keep"
        },
        "validation": {
            "required_fields_check": True,
            "format_validation": True,
            "logical_validation": True
        }
    }


def init_performance_metrics() -> Dict[str, Any]:
    """初始化性能指标追踪"""
    return {
        "version": "1.0.0",
        "start_date": datetime.now().isoformat(),
        "statistics": {
            "total_processed": 0,
            "total_success": 0,
            "total_failed": 0,
            "success_rate": 0.0,
            "avg_confidence": 0.0,
            "avg_processing_time": 0.0
        },
        "by_type": {
            "vat_special": {
                "processed": 0,
                "success": 0,
                "avg_confidence": 0.0
            },
            "vat_common": {
                "processed": 0,
                "success": 0,
                "avg_confidence": 0.0
            },
            "electronic": {
                "processed": 0,
                "success": 0,
                "avg_confidence": 0.0
            },
            "quota": {
                "processed": 0,
                "success": 0,
                "avg_confidence": 0.0
            }
        },
        "learning_progress": {
            "new_types_learned": 0,
            "rules_refined": 0,
            "accuracy_improvement": 0.0,
            "last_learning_date": None
        },
        "field_extraction_stats": {
            "total_fields_attempted": 0,
            "total_fields_extracted": 0,
            "field_success_rate": 0.0,
            "by_field": {}
        }
    }


def init_learning_config() -> Dict[str, Any]:
    """初始化学习配置"""
    return {
        "version": "1.0.0",
        "learning": {
            "enabled": True,
            "auto_mode": True,
            "triggers": {
                "unknown_type_confidence": 0.6,
                "min_samples_for_new_type": 3,
                "failure_rate_threshold": 0.3,
                "user_feedback_weight": 0.8
            },
            "validation": {
                "min_accuracy_for_adoption": 0.8,
                "cross_validation": True,
                "test_set_size": 0.2
            }
        },
        "upgrade": {
            "enabled": True,
            "auto_upgrade": False,
            "check_interval_hours": 24,
            "source": {
                "type": "local",
                "path": "/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
            },
            "backup_before_upgrade": True,
            "preserve_learning_data": True
        },
        "feedback": {
            "enabled": True,
            "collect_corrections": True,
            "collect_templates": True,
            "collect_performance": True
        }
    }


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """保存 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    print("🧠 初始化发票处理 Agent 学习系统...")
    print(f"📁 工作空间: {WORKSPACE}")
    print(f"📁 内存目录: {MEMORY_DIR}")
    print(f"📁 学习目录: {LEARNING_DIR}")
    print()

    # 1. 初始化已知发票类型
    print("✅ 初始化已知发票类型数据库...")
    known_invoices = init_known_invoices()
    save_json(known_invoices, MEMORY_DIR / "known_invoices.json")
    print(f"   - 已支持 {known_invoices['total_types']} 种发票类型")

    # 2. 初始化提取规则
    print("✅ 初始化提取规则配置...")
    extraction_rules = init_extraction_rules()
    save_json(extraction_rules, MEMORY_DIR / "extraction_rules.json")
    print("   - 4 种提取策略已配置")

    # 3. 初始化性能指标
    print("✅ 初始化性能指标追踪...")
    performance_metrics = init_performance_metrics()
    save_json(performance_metrics, MEMORY_DIR / "performance_metrics.json")
    print("   - 指标追踪已启用")

    # 4. 初始化学习配置
    print("✅ 初始化学习配置...")
    learning_config = init_learning_config()
    save_json(learning_config, MEMORY_DIR / "learning_config.json")
    print("   - 自动学习已启用")
    print("   - 升级检查已配置（24小时间隔）")

    # 5. 创建反馈数据目录结构
    print("✅ 创建学习数据目录...")
    (LEARNING_DIR / "invoice_templates").mkdir(exist_ok=True)
    (LEARNING_DIR / "field_patterns").mkdir(exist_ok=True)
    (LEARNING_DIR / "feedback").mkdir(exist_ok=True)
    print("   - invoice_templates/: 发票模板库")
    print("   - field_patterns/: 字段模式库")
    print("   - feedback/: 用户反馈数据")

    print()
    print("🎉 学习系统初始化完成！")
    print()
    print("📋 初始配置摘要：")
    print(f"   工作空间: {WORKSPACE}")
    print(f"   已知类型: {known_invoices['total_types']} 种")
    print(f"   自动学习: {'启用' if learning_config['learning']['enabled'] else '禁用'}")
    print(f"   升级检查: {learning_config['upgrade']['check_interval_hours']} 小时")
    print()
    print("🚀 子 Agent 现在具备以下能力：")
    print("   ✅ 识别 4 种常见发票类型")
    print("   ✅ 智能字段提取")
    print("   ✅ 持续学习新类型")
    print("   ✅ 自我优化规则")
    print("   ✅ 定期检查更新")
    print()


if __name__ == "__main__":
    main()
