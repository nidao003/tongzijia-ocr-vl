#!/usr/bin/env python3
"""
发票处理 Agent - 学习引擎

提供持续学习和自我优化能力
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import hashlib


class LearningEngine:
    """学习引擎 - 负责学习新类型和优化规则"""

    def __init__(self, workspace: Path = None):
        """初始化学习引擎"""
        if workspace is None:
            workspace = Path.home() / ".openclaw" / "workspace-invoice-agent"

        self.workspace = workspace
        self.memory_dir = workspace / "memory"
        self.learning_dir = workspace / "skills" / "invoice-processor" / "learning"

        # 加载学习数据
        self.known_invoices = self._load_json("known_invoices.json")
        self.extraction_rules = self._load_json("extraction_rules.json")
        self.performance = self._load_json("performance_metrics.json")
        self.learning_config = self._load_json("learning_config.json")

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """加载 JSON 文件"""
        filepath = self.memory_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_json(self, data: Dict[str, Any], filename: str) -> None:
        """保存 JSON 文件"""
        filepath = self.memory_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def extract_features(self, ocr_text: str) -> Dict[str, Any]:
        """从 OCR 文本中提取特征"""
        features = {
            "text_length": len(ocr_text),
            "line_count": len(ocr_text.split('\n')),
            "keywords_found": [],
            "has_amount": bool(re.search(r'[¥￥]?\d+\.?\d*', ocr_text)),
            "has_date": bool(re.search(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}', ocr_text)),
            "has_tax": bool(re.search(r'税[率额]', ocr_text)),
            "has_invoice_code": bool(re.search(r'发票代码', ocr_text)),
            "has_invoice_no": bool(re.search(r'发票号码', ocr_text)),
            "layout_type": "unknown"
        }

        # 检测关键词
        all_keywords = []
        for inv_type, config in self.known_invoices.get("invoice_types", {}).items():
            all_keywords.extend(config.get("keywords", []))

        for keyword in all_keywords:
            if keyword in ocr_text:
                features["keywords_found"].append(keyword)

        # 简单版式检测
        if "增值税专用发票" in ocr_text or "专用发票" in ocr_text:
            features["layout_type"] = "standard"
        elif "电子发票" in ocr_text:
            features["layout_type"] = "digital"
        elif "定额发票" in ocr_text:
            features["layout_type"] = "simple"
        else:
            features["layout_type"] = "simplified"

        return features

    def classify_invoice(self, ocr_text: str) -> Tuple[str, float]:
        """分类发票类型"""
        features = self.extract_features(ocr_text)
        scores = {}

        # 对每种已知类型计算匹配分数
        for type_id, type_config in self.known_invoices.get("invoice_types", {}).items():
            score = 0.0
            keywords = type_config.get("keywords", [])

            # 关键词匹配
            keyword_matches = sum(1 for kw in keywords if kw in ocr_text)
            if keyword_matches > 0:
                score += 0.5 * keyword_matches

            # 版式匹配
            if features.get("layout_type") == type_config.get("features", {}).get("layout"):
                score += 0.3

            # 特征匹配
            type_features = type_config.get("features", {})
            if type_features.get("has_tax") and features.get("has_tax"):
                score += 0.1
            if type_features.get("has_tax_rate") and "税率" in ocr_text:
                score += 0.1

            scores[type_id] = score

        # 返回得分最高的类型
        if scores:
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]

            # 归一化分数到 0-1
            normalized_score = min(best_score, 1.0)

            return best_type, normalized_score

        return "unknown", 0.0

    def learn_new_type(
        self,
        ocr_text: str,
        type_name: str,
        field_examples: Dict[str, List[str]] = None
    ) -> Dict[str, Any]:
        """学习新的发票类型"""
        # 生成新类型 ID
        type_id = f"custom_{int(datetime.now().timestamp())}"

        # 提取特征
        features = self.extract_features(ocr_text)

        # 推断字段模式
        inferred_fields = {}
        if field_examples:
            for field_name, examples in field_examples.items():
                if examples:
                    # 尝试学习正则模式
                    patterns = self._learn_pattern_from_examples(examples)
                    inferred_fields[field_name] = {
                        "required": True,
                        "patterns": patterns,
                        "learned_from_examples": True
                    }

        # 创建新类型定义
        new_type = {
            "id": type_id,
            "name": type_name,
            "confidence": 0.7,  # 初始置信度
            "sample_count": 1,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "keywords": self._extract_keywords(ocr_text),
            "features": {
                "has_tax": features.get("has_tax", False),
                "has_date": features.get("has_date", False),
                "has_amount": features.get("has_amount", False),
                "layout_type": features.get("layout_type", "unknown"),
                "text_length_avg": features.get("text_length", 0)
            },
            "fields": inferred_fields or self._infer_fields(ocr_text),
            "extraction_rules": {
                "strategy": "fuzzy",
                "fallback": ["keyword", "regex"],
                "min_confidence": 0.6
            },
            "learned": True,
            "source": "user_feedback"
        }

        # 更新知识库
        self.known_invoices["invoice_types"][type_id] = new_type
        self.known_invoices["total_types"] = len(self.known_invoices["invoice_types"])
        self.known_invoices["last_updated"] = datetime.now().isoformat()

        # 保存更新
        self._save_json(self.known_invoices, "known_invoices.json")

        # 更新性能指标
        self.performance["learning_progress"]["new_types_learned"] += 1
        self._save_json(self.performance, "performance_metrics.json")

        return {
            "success": True,
            "type_id": type_id,
            "type_name": type_name,
            "confidence": 0.7,
            "message": f"已学习新类型：{type_name}",
            "requires_validation": True,
            "min_samples_needed": self.learning_config.get("learning", {}).get(
                "triggers", {}
            ).get("min_samples_for_new_type", 3)
        }

    def _extract_keywords(self, ocr_text: str) -> List[str]:
        """从文本中提取可能的关键词"""
        keywords = []

        # 查找可能的发票类型指示词
        patterns = [
            r'发票',
            r'增值税.*发票',
            r'专用发票',
            r'普通发票',
            r'电子发票',
            r'定额发票',
            r'销售.*发票',
            r'收购.*发票'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, ocr_text)
            keywords.extend(matches[:2])  # 最多取2个匹配

        # 去重并限制数量
        return list(set(keywords))[:5]

    def _infer_fields(self, ocr_text: str) -> Dict[str, Any]:
        """推断字段结构"""
        fields = {}

        # 常见字段推断
        field_patterns = {
            "invoice_code": r'发票代码[：:]\s*(\d+)',
            "invoice_no": r'发票号码[：:]\s*(\d+)',
            "invoice_date": r'开票日期[：:]\s*([^\n]+)',
            "amount": r'金额[：:]\s*[¥￥]?([\d,]+\.?\d*)',
            "total_amount": r'[合计总计][：:]\s*[¥￥]?([\d,]+\.?\d*)'
        }

        for field_name, pattern in field_patterns.items():
            if re.search(pattern, ocr_text):
                fields[field_name] = {
                    "required": True,
                    "patterns": [pattern],
                    "inferred": True
                }

        return fields

    def _learn_pattern_from_examples(self, examples: List[str]) -> List[str]:
        """从示例中学习模式"""
        if not examples:
            return []

        # 简单策略：尝试生成通用的正则表达式
        # 实际应用中可以使用更复杂的机器学习方法

        # 分析示例的共同特征
        sample_lengths = [len(ex) for ex in examples]
        avg_length = sum(sample_lengths) / len(sample_lengths)

        # 检查是否都是数字
        all_digits = all(ex.isdigit() for ex in examples)

        # 检查是否有日期格式
        has_date = any(
            re.search(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}', ex)
            for ex in examples
        )

        # 检查是否有金额
        has_amount = any(
            re.search(r'[\d,]+\.?\d*', ex)
            for ex in examples
        )

        # 生成模式
        patterns = []

        if all_digits:
            patterns.append(rf'\d{{{int(min(sample_lengths))},{int(max(sample_lengths))}}}')
        elif has_date:
            patterns.append(r'\d{4}[-年]\d{1,2}[-月]\d{1,2}')
        elif has_amount:
            patterns.append(r'[¥￥]?[\d,]+\.?\d*')
        else:
            # 通用模式
            patterns.append(r'[^\n]+')

        return patterns

    def optimize_rules(self, failures: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基于失败案例优化规则"""
        optimizations = []

        # 按类型分组失败案例
        failures_by_type = defaultdict(list)
        for failure in failures:
            invoice_type = failure.get("invoice_type", "unknown")
            failures_by_type[invoice_type].append(failure)

        # 分析每种类型的失败
        for invoice_type, type_failures in failures_by_type.items():
            if invoice_type not in self.known_invoices.get("invoice_types", {}):
                continue

            # 分析失败原因
            field_failures = defaultdict(int)
            for failure in type_failures:
                missing_fields = failure.get("missing_fields", [])
                for field in missing_fields:
                    field_failures[field] += 1

            # 对高频失败的字段进行优化
            for field_name, fail_count in field_failures.items():
                if fail_count >= 3:  # 同一字段失败3次以上
                    optimization = self._optimize_field_rule(
                        invoice_type, field_name, type_failures
                    )
                    if optimization:
                        optimizations.append(optimization)

        # 保存优化结果
        self.performance["learning_progress"]["rules_refined"] += len(optimizations)
        self._save_json(self.performance, "performance_metrics.json")

        return {
            "success": True,
            "optimizations_count": len(optimizations),
            "optimizations": optimizations
        }

    def _optimize_field_rule(
        self,
        invoice_type: str,
        field_name: str,
        failures: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """优化单个字段的提取规则"""
        # 从失败案例中提取可能的正确模式
        examples = []
        for failure in failures:
            if field_name in failure.get("raw_text", ""):
                # 尝试从原始文本中提取字段值
                examples.append(failure.get("raw_text", ""))

        if not examples:
            return None

        # 学习新模式
        new_patterns = self._learn_pattern_from_examples(examples)

        if new_patterns:
            # 更新字段配置
            type_config = self.known_invoices["invoice_types"][invoice_type]
            if field_name in type_config.get("fields", {}):
                old_patterns = type_config["fields"][field_name].get("patterns", [])
                # 添加新模式
                type_config["fields"][field_name]["patterns"].extend(new_patterns)
                # 去重
                type_config["fields"][field_name]["patterns"] = list(
                    set(type_config["fields"][field_name]["patterns"])
                )

                # 保存
                self._save_json(self.known_invoices, "known_invoices.json")

                return {
                    "invoice_type": invoice_type,
                    "field": field_name,
                    "action": "pattern_added",
                    "new_patterns": new_patterns,
                    "message": f"为 {invoice_type} 的 {field_name} 字段添加了新模式"
                }

        return None

    def record_feedback(
        self,
        feedback_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """记录用户反馈"""
        timestamp = datetime.now().isoformat()
        feedback_record = {
            "timestamp": timestamp,
            "type": feedback_type,
            "data": data
        }

        # 保存反馈
        feedback_dir = self.learning_dir / "feedback"
        feedback_file = feedback_dir / f"{feedback_type}_{timestamp.replace(':', '-')}.json"
        self._save_json(feedback_record, feedback_file)

        # 根据反馈类型采取行动
        if feedback_type == "classification_correction":
            return self._handle_classification_correction(data)
        elif feedback_type == "field_correction":
            return self._handle_field_correction(data)
        elif feedback_type == "new_template":
            return self._handle_new_template(data)

        return {"success": True, "message": "反馈已记录"}

    def _handle_classification_correction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理分类纠正反馈"""
        # 记录正确的分类
        correct_type = data.get("correct_type")
        ocr_text = data.get("ocr_text", "")

        if correct_type and correct_type in self.known_invoices.get("invoice_types", {}):
            # 更新类型特征
            type_config = self.known_invoices["invoice_types"][correct_type]
            type_config["sample_count"] += 1
            type_config["last_seen"] = datetime.now().isoformat()

            # 从错误分类的文本中学习新的关键词
            keywords = self._extract_keywords(ocr_text)
            for kw in keywords:
                if kw not in type_config.get("keywords", []):
                    type_config["keywords"].append(kw)

            self._save_json(self.known_invoices, "known_invoices.json")

            return {
                "success": True,
                "action": "keywords_updated",
                "message": f"已更新 {correct_type} 的关键词"
            }

        return {"success": False, "message": "未知类型"}

    def _handle_field_correction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理字段纠正反馈"""
        invoice_type = data.get("invoice_type")
        field_name = data.get("field_name")
        correct_value = data.get("correct_value")

        if invoice_type and field_name and correct_value:
            # 将正确的值添加到学习样本
            learning_samples = self.learning_dir / "field_patterns" / f"{invoice_type}_{field_name}.jsonl"

            with open(learning_samples, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "field": field_name,
                    "value": correct_value,
                    "timestamp": datetime.now().isoformat()
                }, ensure_ascii=False) + '\n')

            # 如果样本足够，触发规则优化
            if self._count_samples(learning_samples) >= 5:
                self._trigger_field_rule_optimization(invoice_type, field_name)

            return {
                "success": True,
                "action": "sample_recorded",
                "message": f"已记录 {field_name} 的正确值"
            }

        return {"success": False, "message": "缺少必要参数"}

    def _handle_new_template(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理新模板反馈"""
        type_name = data.get("type_name")
        ocr_text = data.get("ocr_text")
        fields = data.get("fields", {})

        if type_name and ocr_text:
            return self.learn_new_type(ocr_text, type_name, fields)

        return {"success": False, "message": "缺少必要参数"}

    def _count_samples(self, filepath: Path) -> int:
        """统计样本数量"""
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        return 0

    def _trigger_field_rule_optimization(self, invoice_type: str, field_name: str) -> None:
        """触发字段规则优化"""
        # 加载学习样本
        sample_file = self.learning_dir / "field_patterns" / f"{invoice_type}_{field_name}.jsonl"
        samples = []

        if sample_file.exists():
            with open(sample_file, 'r', encoding='utf-8') as f:
                for line in f:
                    samples.append(json.loads(line))

        # 学习新模式
        if samples:
            values = [s.get("value", "") for s in samples]
            new_patterns = self._learn_pattern_from_examples(values)

            if new_patterns:
                # 更新规则
                if invoice_type in self.known_invoices.get("invoice_types", {}):
                    field_config = self.known_invoices["invoice_types"][invoice_type]["fields"]
                    if field_name in field_config:
                        field_config[field_name]["patterns"].extend(new_patterns)
                        field_config[field_name]["patterns"] = list(
                            set(field_config[field_name]["patterns"])
                        )
                        self._save_json(self.known_invoices, "known_invoices.json")


# 导出
__all__ = ['LearningEngine']
