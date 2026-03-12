#!/usr/bin/env python3
"""
发票文件管理与归档模块
提供自动分类、命名规范、目录管理等功能
"""

import os
import re
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib


class InvoiceArchiver:
    """发票归档管理器"""

    def __init__(self, workspace: str = None):
        """初始化归档管理器"""
        if workspace is None:
            workspace = os.path.expanduser("~/.openclaw/workspace-invoice-agent")

        self.workspace = workspace
        self.archive_base = os.path.join(workspace, "archive")
        self.output_base = os.path.join(workspace, "output")
        self.temp_dir = os.path.join(workspace, "temp")
        self.memory_dir = os.path.join(workspace, "memory")

        # 配置文件
        self.config_file = os.path.join(self.memory_dir, "archive_config.json")
        self.index_file = os.path.join(self.memory_dir, "invoice_index.json")
        self.mapping_file = os.path.join(self.memory_dir, "file_mapping.json")

        # 加载配置和数据
        self.config = self._load_config()
        self.index = self._load_index()
        self.mapping = self._load_mapping()

        # 公司简称映射
        self.company_short_names = {
            "华为技术有限公司": "华为技术",
            "华为投资控股有限公司": "华为",
            "阿里巴巴（中国）有限公司": "阿里云",
            "阿里巴巴网络技术有限公司": "阿里云",
            "腾讯科技（北京）有限公司": "腾讯科技",
            "腾讯科技（深圳）有限公司": "腾讯",
            "深圳市腾讯计算机系统有限公司": "腾讯",
            "百度在线网络技术（北京）有限公司": "百度",
            "北京百度网讯科技有限公司": "百度",
            "中国移动通信集团浙江有限公司": "浙江移动",
            "中国移动通信集团上海有限公司": "上海移动",
            "中国移动通信集团北京有限公司": "北京移动",
            "中国电信股份有限公司上海分公司": "上海电信",
            "中国电信股份有限公司北京分公司": "北京电信",
            "中国联合网络通信有限公司浙江分公司": "浙江联通",
            "京东集团股份有限公司": "京东",
            "北京京东世纪贸易有限公司": "京东",
            "上海寻梦信息技术有限公司": "拼多多",
            "杭州网易科技有限公司": "网易",
            "网易（杭州）网络有限公司": "网易",
            "北京三快在线科技有限公司": "美团",
            "北京小米智能科技有限公司": "小米",
            "小米科技有限责任公司": "小米",
            "珠海格力电器股份有限公司": "格力",
            "青岛海尔股份有限公司": "海尔",
            "美的集团股份有限公司": "美的",
        }

    def _load_config(self) -> dict:
        """加载配置"""
        default_config = {
            "archive_base": self.archive_base,
            "output_base": self.output_base,
            "naming": {
                "format": "{date}_{type}_{company}_{serial:03d}",
                "date_format": "YYYYMMDD",
                "serial_digits": 3
            },
            "directories": {
                "by_year": True,
                "by_month": True,
                "by_type": True
            }
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return default_config

    def _load_index(self) -> dict:
        """加载发票索引"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "last_updated": datetime.now().isoformat(),
            "total_invoices": 0,
            "by_type": {},
            "by_year": {},
            "invoices": []
        }

    def _load_mapping(self) -> dict:
        """加载文件映射"""
        if os.path.exists(self.mapping_file):
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {}

    def _save_index(self):
        """保存发票索引"""
        self.index["last_updated"] = datetime.now().isoformat()
        os.makedirs(self.memory_dir, exist_ok=True)

        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def _save_mapping(self):
        """保存文件映射"""
        os.makedirs(self.memory_dir, exist_ok=True)

        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.mapping, f, ensure_ascii=False, indent=2)

    def get_short_name(self, company_name: str) -> str:
        """
        获取公司简称

        Args:
            company_name: 完整公司名称

        Returns:
            公司简称（4-8个字符）
        """
        # 优先使用映射表
        if company_name in self.company_short_names:
            return self.company_short_names[company_name]

        # 使用规则生成
        # 1. 去除行政区划
        name = re.sub(r'(北京|上海|天津|重庆|广东|浙江|江苏|四川|湖北|湖南|河北|河南|山东|山西|陕西|辽宁|吉林|黑龙江|内蒙古|甘肃|青海|宁夏|新疆|西藏|云南|贵州|福建|江西|广西|海南|台湾|香港|澳门)(市|省|自治区|特别行政区)?', '', company_name)

        # 2. 去除公司类型后缀
        suffixes = [
            r'股份有限公司$', r'有限公司$', r'有限责任公司$',
            r'集团有限公司$', r'控股有限公司$',
            r'网络技术有限公司$', r'科技有限公司$',
            r'电子商务有限公司$', r'贸易有限公司$',
            r'分公司$', r'（.*?）$', r'\(.*?\)$'
        ]

        for suffix in suffixes:
            name = re.sub(suffix, '', name)

        # 3. 清理多余字符
        name = name.strip()

        # 4. 限制长度（4-8个字符）
        if len(name) > 8:
            name = name[:8]
        elif len(name) < 4:
            # 如果太短，使用原始名称的前4个字
            name = company_name[:4]

        return name

    def get_next_serial_number(self, date_str: str, invoice_type: str) -> int:
        """
        获取下一个流水号

        Args:
            date_str: 日期字符串（YYYYMMDD）
            invoice_type: 发票类型

        Returns:
            流水号（从1开始）
        """
        # 查找当天该类型的最大流水号
        max_serial = 0

        for invoice in self.index["invoices"]:
            if invoice["invoice_date"].replace("-", "") == date_str and invoice["invoice_type"] == invoice_type:
                # 从文件名中提取流水号
                filename = invoice["new_filename"]
                match = re.search(r'_(\d{3})\.', filename)
                if match:
                    serial = int(match.group(1))
                    max_serial = max(max_serial, serial)

        return max_serial + 1

    def generate_filename(self, invoice_data: dict) -> str:
        """
        生成标准化文件名

        Args:
            invoice_data: 发票数据

        Returns:
            标准化文件名
        """
        # 1. 提取信息
        invoice_date = invoice_data.get("invoice_date", "")
        invoice_type_name = invoice_data.get("invoice_type_name", "未知类型")
        company_name = invoice_data.get("buyer_name") or invoice_data.get("seller_name", "未知公司")

        # 2. 解析日期
        if invoice_date:
            date_str = invoice_date.replace("-", "")
        else:
            date_str = datetime.now().strftime("%Y%m%d")

        # 3. 获取简称
        short_name = self.get_short_name(company_name)

        # 4. 获取流水号
        invoice_type = invoice_data.get("invoice_type", "unknown")
        serial = self.get_next_serial_number(date_str, invoice_type)

        # 5. 构造文件名
        filename = f"{date_str}_{invoice_type_name}_{short_name}_{serial:03d}"

        return filename

    def get_archive_path(self, invoice_data: dict, filename: str, original_ext: str) -> str:
        """
        获取归档路径

        Args:
            invoice_data: 发票数据
            filename: 标准化文件名
            original_ext: 原始文件扩展名

        Returns:
            完整的归档路径
        """
        # 1. 提取日期信息
        invoice_date = invoice_data.get("invoice_date", "")
        if invoice_date:
            date_obj = datetime.strptime(invoice_date, "%Y-%m-%d")
            year = date_obj.strftime("%Y")
            month = date_obj.strftime("%m")
        else:
            year = datetime.now().strftime("%Y")
            month = datetime.now().strftime("%m")

        # 2. 获取发票类型
        invoice_type = invoice_data.get("invoice_type", "unknown")

        # 3. 构造目录路径
        archive_path = os.path.join(
            self.archive_base,
            year,
            month,
            invoice_type
        )

        # 4. 创建目录
        os.makedirs(archive_path, exist_ok=True)

        # 5. 返回完整路径
        full_path = os.path.join(archive_path, f"{filename}{original_ext}")

        return full_path

    def archive_invoice(self, file_path: str, invoice_data: dict) -> dict:
        """
        归档单张发票

        Args:
            file_path: 原始文件路径
            invoice_data: 发票数据

        Returns:
            归档结果
        """
        try:
            # 1. 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"文件不存在: {file_path}"
                }

            # 2. 获取原始扩展名
            original_ext = os.path.splitext(file_path)[1]

            # 3. 生成标准化文件名
            new_filename = self.generate_filename(invoice_data)

            # 4. 获取归档路径
            archive_path = self.get_archive_path(invoice_data, new_filename, original_ext)

            # 5. 移动文件
            shutil.move(file_path, archive_path)

            # 6. 更新索引
            invoice_record = {
                "id": f"{new_filename}_{datetime.now().strftime('%H%M%S')}",
                "original_filename": os.path.basename(file_path),
                "new_filename": f"{new_filename}{original_ext}",
                "archive_path": archive_path,
                "invoice_date": invoice_data.get("invoice_date", ""),
                "invoice_type": invoice_data.get("invoice_type", ""),
                "invoice_type_name": invoice_data.get("invoice_type_name", ""),
                "invoice_code": invoice_data.get("fields", {}).get("invoice_code", ""),
                "invoice_no": invoice_data.get("fields", {}).get("invoice_no", ""),
                "amount": invoice_data.get("fields", {}).get("total_amount", ""),
                "company_name": invoice_data.get("fields", {}).get("buyer_name") or invoice_data.get("fields", {}).get("seller_name", ""),
                "archived_at": datetime.now().isoformat()
            }

            self.index["invoices"].append(invoice_record)
            self.index["total_invoices"] += 1

            # 更新统计
            invoice_type = invoice_data.get("invoice_type", "")
            if invoice_type:
                self.index["by_type"][invoice_type] = self.index["by_type"].get(invoice_type, 0) + 1

            invoice_year = invoice_data.get("invoice_date", "")[:4]
            if invoice_year:
                self.index["by_year"][invoice_year] = self.index["by_year"].get(invoice_year, 0) + 1

            # 保存索引
            self._save_index()

            # 7. 更新映射
            self.mapping[os.path.basename(file_path)] = archive_path
            self._save_mapping()

            return {
                "success": True,
                "original_path": file_path,
                "archive_path": archive_path,
                "filename": f"{new_filename}{original_ext}",
                "record": invoice_record
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"归档失败: {str(e)}"
            }

    def batch_archive(self, file_paths: List[str], invoice_results: List[dict]) -> dict:
        """
        批量归档发票

        Args:
            file_paths: 文件路径列表
            invoice_results: 识别结果列表

        Returns:
            批量归档结果
        """
        results = []
        successful = 0
        failed = 0

        for file_path, invoice_result in zip(file_paths, invoice_results):
            if invoice_result.get("success"):
                result = self.archive_invoice(file_path, invoice_result)
                results.append(result)

                if result.get("success"):
                    successful += 1
                else:
                    failed += 1
            else:
                failed += 1
                results.append({
                    "success": False,
                    "error": "识别失败，跳过归档",
                    "file_path": file_path
                })

        return {
            "total_files": len(file_paths),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    def query_by_date(self, start_date: str, end_date: str) -> List[dict]:
        """
        按日期查询发票

        Args:
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）

        Returns:
            发票列表
        """
        results = []

        for invoice in self.index["invoices"]:
            invoice_date = invoice.get("invoice_date", "")

            if start_date <= invoice_date <= end_date:
                results.append(invoice)

        return results

    def query_by_type(self, invoice_type: str) -> List[dict]:
        """
        按类型查询发票

        Args:
            invoice_type: 发票类型

        Returns:
            发票列表
        """
        results = []

        for invoice in self.index["invoices"]:
            if invoice.get("invoice_type") == invoice_type:
                results.append(invoice)

        return results

    def query_by_company(self, company_name: str) -> List[dict]:
        """
        按公司查询发票（支持模糊搜索）

        Args:
            company_name: 公司名称

        Returns:
            发票列表
        """
        results = []

        for invoice in self.index["invoices"]:
            if company_name.lower() in invoice.get("company_name", "").lower():
                results.append(invoice)

        return results

    def get_statistics(self) -> dict:
        """
        获取统计信息

        Returns:
            统计数据
        """
        return {
            "total_invoices": self.index["total_invoices"],
            "by_type": self.index["by_type"],
            "by_year": self.index["by_year"],
            "last_updated": self.index["last_updated"]
        }


# 便捷函数
def archive_single_invoice(file_path: str, invoice_data: dict, workspace: str = None) -> dict:
    """
    归档单张发票（便捷函数）

    Args:
        file_path: 文件路径
        invoice_data: 发票数据
        workspace: 工作空间路径

    Returns:
        归档结果
    """
    archiver = InvoiceArchiver(workspace)
    return archiver.archive_invoice(file_path, invoice_data)


def batch_archive_invoices(file_paths: List[str], invoice_results: List[dict], workspace: str = None) -> dict:
    """
    批量归档发票（便捷函数）

    Args:
        file_paths: 文件路径列表
        invoice_results: 识别结果列表
        workspace: 工作空间路径

    Returns:
        批量归档结果
    """
    archiver = InvoiceArchiver(workspace)
    return archiver.batch_archive(file_paths, invoice_results)


# 测试代码
if __name__ == "__main__":
    # 测试简称生成
    archiver = InvoiceArchiver()

    test_companies = [
        "华为技术有限公司",
        "阿里巴巴（中国）有限公司",
        "腾讯科技（北京）有限公司",
        "中国移动通信集团浙江有限公司",
        "北京京东世纪贸易有限公司"
    ]

    print("公司简称生成测试:")
    for company in test_companies:
        short_name = archiver.get_short_name(company)
        print(f"{company} → {short_name}")

    # 测试文件名生成
    print("\n文件名生成测试:")
    test_invoice = {
        "invoice_date": "2026-03-11",
        "invoice_type": "vat_special",
        "invoice_type_name": "增值税专用发票",
        "buyer_name": "华为技术有限公司",
        "fields": {
            "invoice_code": "1500242720",
            "invoice_no": "00534712",
            "total_amount": "227500.00"
        }
    }

    filename = archiver.generate_filename(test_invoice)
    print(f"生成的文件名: {filename}.png")

    print("\n✅ 归档模块测试完成")
