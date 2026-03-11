#!/usr/bin/env python3
"""
PaddleOCR-VL OpenClaw 工具类（优化版）
智能管理服务生命周期，按需启动/停止，最大化释放资源
"""

import requests
import base64
import os
import subprocess
import time
import atexit
import threading
import io
from typing import Dict, Any, List, Optional, Tuple
import json
from pdf_utils import PDFProcessor, is_pdf, get_file_page_count


class ServiceManager:
    """服务管理器 - 负责启动和停止 OCR 服务"""

    def __init__(self, project_dir: str = "/Users/daodao/dsl/paddleocr-vl"):
        self.project_dir = project_dir
        self.api_url = "http://localhost:8001"
        self.mlx_url = "http://localhost:8111"
        self.api_process = None
        self.mlx_process = None
        self.service_count = 0  # 引用计数
        self._last_activity = None  # 最后活动时间

        # 注册清理函数
        import atexit
        atexit.register(self.cleanup)

    def _check_port(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}', '-sTCP:LISTEN'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def _start_mlx_vlm(self) -> bool:
        """启动 MLX-VLM 推理服务"""
        if self._check_port(8111):
            print("✅ MLX-VLM 推理服务已运行")
            return True

        print("📦 启动 MLX-VLM 推理服务...")
        try:
            self.mlx_process = subprocess.Popen(
                [
                    os.path.join(self.project_dir, ".venv_paddleocr/bin/python"),
                    "-m", "mlx_vlm.server",
                    "--port", "8111"
                ],
                stdout=open(os.path.join(self.project_dir, "mlx_vlm_server.log"), "w"),
                stderr=subprocess.STDOUT,
                cwd=self.project_dir
            )
            print("✅ MLX-VLM 推理服务启动中...")
            time.sleep(5)  # 等待服务启动

            if self._check_port(8111):
                print("✅ MLX-VLM 推理服务就绪")
                return True
            else:
                print("⚠️  MLX-VLM 推理服务启动可能失败")
                return False
        except Exception as e:
            print(f"❌ MLX-VLM 推理服务启动失败: {e}")
            return False

    def _start_api(self) -> bool:
        """启动 MLX-VLM API 服务"""
        if self._check_port(8001):
            print("✅ MLX-VLM API 服务已运行")
            return True

        print("📦 启动 MLX-VLM API 服务...")
        try:
            self.api_process = subprocess.Popen(
                [
                    os.path.join(self.project_dir, ".venv_paddleocr/bin/python"),
                    os.path.join(self.project_dir, "mlx_vlm_api_server.py")
                ],
                stdout=open(os.path.join(self.project_dir, "mlx_vlm_api_server.log"), "w"),
                stderr=subprocess.STDOUT,
                cwd=self.project_dir
            )
            print("✅ MLX-VLM API 服务启动中...")
            time.sleep(3)  # 等待服务启动

            if self._check_port(8001):
                print("✅ MLX-VLM API 服务就绪")
                return True
            else:
                print("⚠️  MLX-VLM API 服务启动可能失败")
                return False
        except Exception as e:
            print(f"❌ MLX-VLM API 服务启动失败: {e}")
            return False

    def start(self) -> bool:
        """启动所有需要的服务"""
        self.service_count += 1

        if self.service_count > 1:
            print(f"📊 服务已有 {self.service_count} 个使用者，跳过启动")
            return True

        print("="*60)
        print("🚀 启动 PaddleOCR-VL 服务（按需模式）")
        print("="*60)

        success = True
        success &= self._start_mlx_vlm()
        success &= self._start_api()

        if success:
            print("\n✅ 所有服务已就绪！")
            print(f"📍 API 地址: {self.api_url}")
            print(f"📖 API 文档: {self.api_url}/docs")
        else:
            print("\n❌ 部分服务启动失败")

        return success

    def stop(self):
        """停止服务"""
        self.service_count -= 1

        if self.service_count > 0:
            print(f"📊 还有 {self.service_count} 个使用者，不停止服务")
            return

        print("="*60)
        print("🛑 停止 PaddleOCR-VL 服务（释放资源）")
        print("="*60)

        # 停止 API 服务
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("✅ MLX-VLM API 服务已停止")
            except:
                self.api_process.kill()
                print("✅ MLX-VLM API 服务已强制停止")
            self.api_process = None

        # 停止推理服务
        if self.mlx_process:
            try:
                self.mlx_process.terminate()
                self.mlx_process.wait(timeout=5)
                print("✅ MLX-VLM 推理服务已停止")
            except:
                self.mlx_process.kill()
                print("✅ MLX-VLM 推理服务已强制停止")
            self.mlx_process = None

        print("💾 所有资源已释放，系统恢复正常")

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            if response.status_code == 200:
                # 更新最后活动时间
                import time
                self._last_activity = time.time()
                return response.json()
        except:
            pass

        return {
            "status": "unavailable",
            "message": "服务未运行，请先调用 start() 方法"
        }

    def cleanup(self):
        """清理资源（进程退出时自动调用）"""
        if self.api_process or self.mlx_process:
            try:
                self.stop()
            except:
                pass

    def get_memory_usage(self) -> Dict[str, float]:
        """获取服务内存使用情况（MB）"""
        import psutil
        memory_usage = {}

        try:
            # MLX-VLM 推理服务内存
            if self.mlx_process and self.mlx_process.poll() is None:
                try:
                    proc = psutil.Process(self.mlx_process.pid)
                    memory_usage['mlx_vlm_mb'] = proc.memory_info().rss / 1024 / 1024
                except:
                    pass

            # API 服务内存
            if self.api_process and self.api_process.poll() is None:
                try:
                    proc = psutil.Process(self.api_process.pid)
                    memory_usage['api_mb'] = proc.memory_info().rss / 1024 / 1024
                except:
                    pass

            # 总内存
            if memory_usage:
                memory_usage['total_mb'] = sum(memory_usage.values())

        except ImportError:
            # psutil 未安装
            pass

        return memory_usage


# 全局服务管理器实例
_service_manager = None

def get_service_manager() -> ServiceManager:
    """获取全局服务管理器"""
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager


class PaddleOCROptimized:
    """PaddleOCR-VL 优化版工具类 - 自动管理服务生命周期"""

    def __init__(self, auto_start: bool = True, auto_stop: bool = True):
        """
        初始化 PaddleOCR 工具

        Args:
            auto_start: 使用时自动启动服务
            auto_stop: 使用完自动停止服务
        """
        self.auto_start = auto_start
        self.auto_stop = auto_stop
        self.service_manager = get_service_manager()

        if auto_start:
            self.service_manager.start()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if self.auto_stop:
            self.service_manager.stop()

    def recognize_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        识别文件（支持图片和PDF）

        Args:
            file_path: 文件路径（图片或PDF）
            **kwargs: 额外参数
                - dpi: PDF 分辨率（默认 200）
                - max_pages: PDF 最大处理页数（默认全部）
                - merge_pdf_pages: 是否合并 PDF 所有页面的文字（默认 True）

        Returns:
            识别结果字典
        """
        # 检查文件
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"文件不存在: {file_path}"
            }

        # 验证文件
        valid, error_msg = PDFProcessor.validate_file(file_path)
        if not valid:
            return {
                "success": False,
                "error": error_msg
            }

        # 判断文件类型
        file_type = PDFProcessor.get_file_type(file_path)

        try:
            if file_type == 'pdf':
                return self._recognize_pdf(file_path, **kwargs)
            else:
                return self._recognize_image(file_path)

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "服务未运行，请先启动服务"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时，请稍后重试"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"识别失败: {str(e)}"
            }

    def _recognize_image(self, image_path: str) -> Dict[str, Any]:
        """识别单张图片"""
        # 读取文件
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # 调用 API
        files = {
            'file': (os.path.basename(image_path), image_data, 'image/png')
        }

        response = requests.post(
            f"{self.service_manager.api_url}/ocr",
            files=files,
            timeout=120  # 增加超时时间以支持大文件
        )

        if response.status_code == 200:
            result = response.json()
            result['success'] = True
            result['file_type'] = 'image'
            return result
        else:
            return {
                "success": False,
                "error": f"API 错误 (HTTP {response.status_code}): {response.text}"
            }

    def _recognize_pdf(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """识别 PDF 文件"""
        dpi = kwargs.get('dpi', 200)
        max_pages = kwargs.get('max_pages', None)
        merge_pages = kwargs.get('merge_pdf_pages', True)

        # 转换 PDF 为图片
        print(f"🔄 正在转换 PDF: {os.path.basename(pdf_path)}")
        images = PDFProcessor.pdf_to_images(pdf_path, dpi=dpi, max_pages=max_pages)

        if not images:
            return {
                "success": False,
                "error": "PDF 转换失败或没有页面"
            }

        print(f"✅ PDF 共 {len(images)} 页，开始识别...")

        # 逐页识别
        page_results = []
        all_text = []

        for img, page_num in images:
            # 将 PIL Image 转换为字节
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_data = img_bytes.getvalue()

            # 调用 API
            files = {
                'file': (f"page_{page_num}.png", img_data, 'image/png')
            }

            response = requests.post(
                f"{self.service_manager.api_url}/ocr",
                files=files,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                page_text = result.get('text', '')
                page_results.append({
                    'page': page_num,
                    'text': page_text,
                    'usage': result.get('usage', {})
                })
                all_text.append(page_text)
                print(f"   ✅ 第 {page_num}/{len(images)} 页识别完成")
            else:
                page_results.append({
                    'page': page_num,
                    'error': f"识别失败: {response.text}"
                })
                print(f"   ❌ 第 {page_num}/{len(images)} 页识别失败")

        # 合并结果
        merged_text = '\n\n'.join(all_text) if merge_pages else all_text

        return {
            "success": True,
            "file_type": "pdf",
            "total_pages": len(images),
            "text": merged_text if merge_pages else None,
            "pages": page_results,
            "usage": {
                "total_pages": len(images),
                "successful_pages": len([r for r in page_results if 'error' not in r])
            }
        }

    def get_text_only(self, image_path: str) -> str:
        """
        仅获取识别的文字（最简单的接口）

        Args:
            image_path: 图片路径

        Returns:
            识别的文字，失败返回空字符串
        """
        result = self.recognize_file(image_path)
        return result.get('text', '') if result.get('success') else ''

    def batch_recognize(
        self,
        file_paths: List[str],
        callback: Optional[callable] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        批量识别多个文件（支持图片和PDF）

        Args:
            file_paths: 文件路径列表
            callback: 进度回调函数 callback(current, total, filename)
            **kwargs: 传递给 recognize_file 的参数

        Returns:
            批量识别结果字典
        """
        results = []
        total = len(file_paths)
        successful = 0
        failed = 0

        for i, file_path in enumerate(file_paths, 1):
            result = self.recognize_file(file_path, **kwargs)

            # 添加文件名到结果
            result['filename'] = os.path.basename(file_path)

            if result.get('success'):
                successful += 1
            else:
                failed += 1

            results.append(result)

            # 进度回调
            if callback:
                callback(i, total, file_path)

        return {
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'results': results
        }

    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return self.service_manager.health_check()

    def shutdown(self):
        """手动停止服务"""
        if self.auto_stop:
            print("⚠️  已启用自动停止，无需手动调用")
            return

        print("🛑 手动停止服务...")
        self.service_manager.stop()


# ========== 简化的便捷函数 ==========

def quick_recognize(image_path: str) -> str:
    """
    快速识别图片（最简单的接口）
    自动管理服务生命周期

    Args:
        image_path: 图片路径

    Returns:
        识别的文字内容

    示例:
        text = quick_recognize("/path/to/image.png")
        print(text)
    """
    with PaddleOCROptimized(auto_start=True, auto_stop=True) as ocr:
        return ocr.get_text_only(image_path)


def batch_recognize(
    file_paths: List[str],
    callback: Optional[callable] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    批量识别（自动管理服务，支持图片和PDF）

    Args:
        file_paths: 文件路径列表
        callback: 进度回调函数 callback(current, total, filename)
        **kwargs: 传递给 recognize_file 的参数
            - dpi: PDF 分辨率（默认 200）
            - max_pages: PDF 最大处理页数（默认全部）
            - merge_pdf_pages: 是否合并 PDF 所有页面的文字（默认 True）

    Returns:
        批量识别结果字典

    示例:
        result = batch_recognize(["doc1.png", "doc2.pdf"])
        print(f"成功: {result['successful']}/{result['total_files']}")
        for r in result['results']:
            if r['success']:
                print(f"{r['filename']}: {r['text'][:50]}...")
    """
    with PaddleOCROptimized(auto_start=True, auto_stop=True) as ocr:
        return ocr.batch_recognize(file_paths, callback, **kwargs)


def recognize_with_auto_stop(image_path: str, stop_after: int = 300):
    """
    识别图片并在指定时间后自动停止服务

    Args:
        image_path: 图片路径
        stop_after: 停止服务的延迟时间（秒），默认 5 分钟

    示例:
        text = recognize_with_auto_stop("doc.png", stop_after=60)
    """
    ocr = PaddleOCROptimized(auto_start=True, auto_stop=False)

    try:
        result = ocr.recognize_file(image_path)
        text = result.get('text', '') if result.get('success') else ''

        # 延迟停止服务
        print(f"⏰ 服务将在 {stop_after} 秒后自动停止...")
        time.sleep(stop_after)

        return text
    finally:
        ocr.shutdown()


# ========== OpenClaw 专用接口 ==========

class OpenClawOCR:
    """
    OpenClaw 专用 OCR 工具
    智能管理服务，最大化资源释放
    """

    def __init__(self):
        self._ocr = None

    def __enter__(self):
        """进入上下文（自动启动服务）"""
        self._ocr = PaddleOCROptimized(auto_start=True, auto_stop=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文（延迟停止服务）"""
        # 延迟 30 秒后停止，允许连续调用
        print("⏰ 服务将在 30 秒后自动停止...")
        time.sleep(30)
        self._ocr.shutdown()
        self._ocr = None

    def recognize(self, image_path: str) -> str:
        """识别图片"""
        if self._ocr is None:
            raise RuntimeError("请在上下文管理器中使用此方法")
        return self._ocr.get_text_only(image_path)

    def batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """批量识别"""
        if self._ocr is None:
            raise RuntimeError("请在上下文管理器中使用此方法")
        return self._ocr.batch_recognize(image_paths)

    def health(self) -> Dict[str, Any]:
        """健康检查"""
        if self._ocr is None:
            return {"status": "not_initialized"}
        return self._ocr.health_check()


# ========== 测试和示例 ==========

def test_quick_recognize():
    """测试快速识别"""
    print("="*60)
    print("测试：快速识别（自动启动/停止）")
    print("="*60)

    text = quick_recognize("test_image.png")
    print(f"\n✅ 识别结果:\n{text}")
    print(f"\n💾 服务已自动停止，资源已释放")


def test_context_manager():
    """测试上下文管理器"""
    print("\n" + "="*60)
    print("测试：上下文管理器（推荐）")
    print("="*60)

    with PaddleOCROptimized() as ocr:
        result = ocr.recognize_file("test_image.png")
        if result['success']:
            print(f"✅ 识别成功:")
            print(f"文字: {result['text']}")
            print(f"耗时: {result.get('usage', {})}")


def test_openclaw_interface():
    """测试 OpenClaw 专用接口"""
    print("\n" + "="*60)
    print("测试：OpenClaw 专用接口")
    print("="*60)

    # 推荐用法：使用上下文管理器
    with OpenClawOCR() as ocr:
        text = ocr.recognize("test_image.png")
        print(f"✅ 识别结果:\n{text}")
        print("\n📝 识别完成，30 秒后将自动停止服务...")

    print("\n💾 服务已自动停止，资源已释放")


def main():
    """运行所有测试"""
    print("="*60)
    print("PaddleOCR-VL 优化版工具测试")
    print("="*60)

    # 检查测试文件
    if not os.path.exists("test_image.png"):
        print("❌ 测试文件不存在，请先创建 test_image.png")
        return

    # 运行测试
    test_quick_recognize()
    test_context_manager()
    test_openclaw_interface()

    print("\n" + "="*60)
    print("✅ 所有测试完成")
    print("="*60)


if __name__ == "__main__":
    main()
