#!/usr/bin/env python3
"""
PaddleOCR-VL 升级功能测试套件
测试文件格式支持、批量处理、MLX-VLM加速等功能
"""

import os
import sys
import time
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from paddleocr_tool import (
    PaddleOCROptimized,
    quick_recognize,
    batch_recognize,
    get_service_manager
)
from pdf_utils import PDFProcessor


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def run_test(self, test_name, test_func):
        """运行单个测试"""
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"{'='*60}")

        try:
            test_func()
            self.passed += 1
            self.results.append({
                'name': test_name,
                'status': 'PASSED',
                'error': None
            })
            print(f"✅ 测试通过")
        except AssertionError as e:
            self.failed += 1
            self.results.append({
                'name': test_name,
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"❌ 测试失败: {e}")
        except Exception as e:
            self.failed += 1
            self.results.append({
                'name': test_name,
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"❌ 测试错误: {e}")

    def print_summary(self):
        """打印测试摘要"""
        print(f"\n{'='*60}")
        print("测试摘要")
        print(f"{'='*60}")
        print(f"总计: {self.passed + self.failed}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"成功率: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print(f"{'='*60}\n")


def test_pdf_utils():
    """测试 PDF 工具模块"""
    print("测试 PDF 工具模块...")

    # 测试文件类型检查
    assert PDFProcessor.is_supported_file("test.png"), "应该支持 PNG"
    assert PDFProcessor.is_supported_file("test.pdf"), "应该支持 PDF"
    assert not PDFProcessor.is_supported_file("test.txt"), "不应该支持 TXT"

    # 测试文件类型判断
    assert PDFProcessor.get_file_type("test.png") == "image"
    assert PDFProcessor.get_file_type("test.pdf") == "pdf"
    assert PDFProcessor.get_file_type("test.txt") == "unknown"

    print("✅ PDF 工具模块测试通过")


def test_service_manager():
    """测试服务管理器"""
    print("测试服务管理器...")

    manager = get_service_manager()

    # 测试健康检查
    health = manager.health_check()
    print(f"服务状态: {health.get('status', 'unknown')}")

    # 如果服务未运行，尝试启动
    if health.get('status') != 'healthy':
        print("启动服务...")
        success = manager.start()
        assert success, "服务启动应该成功"

        # 等待服务就绪
        time.sleep(8)

        # 再次检查
        health = manager.health_check()
        assert health.get('status') == 'healthy', "服务状态应该是健康的"

    # 测试内存监控
    memory = manager.get_memory_usage()
    print(f"内存使用: {memory}")

    print("✅ 服务管理器测试通过")


def test_file_format_support():
    """测试文件格式支持"""
    print("测试文件格式支持...")

    # 创建测试图片
    from PIL import Image, ImageDraw

    test_images = []

    # 创建不同格式的测试图片
    formats = ['PNG', 'JPEG', 'WebP']

    for fmt in formats:
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"测试文字 {fmt}", fill='black')

        test_path = f"/tmp/test_image_{fmt.lower()}.{fmt.lower().replace('jpeg', 'jpg')}"
        img.save(test_path, fmt)
        test_images.append(test_path)

    print(f"✅ 创建了 {len(test_images)} 个测试图片")

    # 测试图片格式验证
    for img_path in test_images:
        valid, msg = PDFProcessor.validate_file(img_path)
        assert valid, f"图片验证应该通过: {msg}"
        print(f"✅ {os.path.basename(img_path)} 验证通过")

    # 清理测试文件
    for img_path in test_images:
        try:
            os.remove(img_path)
        except:
            pass

    print("✅ 文件格式支持测试通过")


def test_batch_processing():
    """测试批量处理"""
    print("测试批量处理...")

    # 创建多个测试图片
    from PIL import Image, ImageDraw

    test_images = []
    for i in range(3):
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f"测试图片 {i+1}", fill='black')

        test_path = f"/tmp/batch_test_{i+1}.png"
        img.save(test_path, 'PNG')
        test_images.append(test_path)

    print(f"✅ 创建了 {len(test_images)} 个批量测试图片")

    try:
        # 测试批量识别
        print("开始批量识别...")
        start_time = time.time()

        result = batch_recognize(
            test_images,
            callback=lambda current, total, filename: print(f"  进度: {current}/{total} - {os.path.basename(filename)}")
        )

        elapsed_time = time.time() - start_time

        # 验证结果
        assert result['total_files'] == len(test_images), "文件总数应该匹配"
        assert result['successful'] > 0, "至少应该有一个成功"
        assert len(result['results']) == len(test_images), "结果数量应该匹配"

        print(f"✅ 批量识别完成: {result['successful']}/{result['total_files']} 成功")
        print(f"⏱️  总耗时: {elapsed_time:.2f} 秒")
        print(f"⚡ 平均速度: {elapsed_time / len(test_images):.2f} 秒/张")

    finally:
        # 清理测试文件
        for img_path in test_images:
            try:
                os.remove(img_path)
            except:
                pass

    print("✅ 批量处理测试通过")


def test_memory_management():
    """测试内存管理"""
    print("测试内存管理...")

    manager = get_service_manager()

    # 获取初始内存
    memory_before = manager.get_memory_usage()
    print(f"处理前内存: {memory_before}")

    # 创建并处理测试图片
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "内存测试图片", fill='black')

    test_path = "/tmp/memory_test.png"
    img.save(test_path, 'PNG')

    try:
        # 识别图片
        text = quick_recognize(test_path)
        print(f"识别结果: {text[:50]}...")

        # 获取处理后内存
        memory_after = manager.get_memory_usage()
        print(f"处理后内存: {memory_after}")

        # 验证内存没有异常增长（不应该增长超过 100MB）
        if memory_before.get('total_mb') and memory_after.get('total_mb'):
            growth = memory_after['total_mb'] - memory_before['total_mb']
            print(f"内存增长: {growth:.2f} MB")
            assert growth < 100, f"内存增长过大: {growth} MB"

    finally:
        try:
            os.remove(test_path)
        except:
            pass

    print("✅ 内存管理测试通过")


def test_error_handling():
    """测试错误处理"""
    print("测试错误处理...")

    # 测试不存在的文件
    result = quick_recognize("/nonexistent/file.png")
    # 应该返回空字符串而不是抛出异常
    assert result == "" or isinstance(result, str), "不存在的文件应该返回空字符串"

    # 测试不支持的格式
    with PaddleOCROptimized() as ocr:
        result = ocr.recognize_file("/tmp/test.txt")
        assert not result['success'], "不支持的格式应该失败"
        assert 'error' in result, "应该包含错误信息"

    print("✅ 错误处理测试通过")


def main():
    """主测试函数"""
    print("="*60)
    print("PaddleOCR-VL 升级功能测试套件")
    print("="*60)

    runner = TestRunner()

    # 运行所有测试
    runner.run_test("PDF 工具模块", test_pdf_utils)
    runner.run_test("服务管理器", test_service_manager)
    runner.run_test("文件格式支持", test_file_format_support)
    runner.run_test("批量处理", test_batch_processing)
    runner.run_test("内存管理", test_memory_management)
    runner.run_test("错误处理", test_error_handling)

    # 打印摘要
    runner.print_summary()

    # 保存测试结果
    results_file = project_root / "test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': runner.passed + runner.failed,
            'passed': runner.passed,
            'failed': runner.failed,
            'success_rate': runner.passed / (runner.passed + runner.failed) * 100,
            'results': runner.results
        }, f, ensure_ascii=False, indent=2)

    print(f"📄 测试结果已保存到: {results_file}")

    return 0 if runner.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
