#!/usr/bin/env python3
"""
PDF 处理工具模块
支持 PDF 文档转图片、多页处理等功能
"""

import fitz  # PyMuPDF
from PIL import Image
import io
import os
from typing import List, Tuple, Optional
import tempfile


class PDFProcessor:
    """PDF 处理器 - 将 PDF 转换为图片"""

    # 支持的图片格式
    SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif', '.tiff']

    # 支持的文档格式
    SUPPORTED_DOC_FORMATS = ['.pdf']

    @staticmethod
    def is_supported_file(file_path: str) -> bool:
        """
        检查文件是否支持

        Args:
            file_path: 文件路径

        Returns:
            是否支持
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in PDFProcessor.SUPPORTED_IMAGE_FORMATS or ext in PDFProcessor.SUPPORTED_DOC_FORMATS

    @staticmethod
    def get_file_type(file_path: str) -> str:
        """
        获取文件类型

        Args:
            file_path: 文件路径

        Returns:
            'pdf', 'image', 或 'unknown'
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext in PDFProcessor.SUPPORTED_DOC_FORMATS:
            return 'pdf'
        elif ext in PDFProcessor.SUPPORTED_IMAGE_FORMATS:
            return 'image'
        return 'unknown'

    @staticmethod
    def pdf_to_images(
        pdf_path: str,
        dpi: int = 200,
        max_pages: Optional[int] = None,
        output_format: str = 'PNG'
    ) -> List[Tuple[Image.Image, int]]:
        """
        将 PDF 转换为图片列表

        Args:
            pdf_path: PDF 文件路径
            dpi: 分辨率（默认 200）
            max_pages: 最大处理页数（None 表示全部）
            output_format: 输出格式（PNG, JPEG）

        Returns:
            [(Image, page_number), ...] 列表

        Raises:
            FileNotFoundError: PDF 文件不存在
            Exception: PDF 处理失败
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

        try:
            # 打开 PDF
            doc = fitz.open(pdf_path)
            total_pages = doc.page_count

            # 限制页数
            if max_pages is not None:
                total_pages = min(total_pages, max_pages)

            results = []

            for page_num in range(total_pages):
                page = doc[page_num]

                # 设置缩放以控制分辨率
                zoom = dpi / 72  # 72 是默认 DPI
                mat = fitz.Matrix(zoom, zoom)

                # 渲染页面为图片
                pix = page.get_pixmap(matrix=mat)

                # 转换为 PIL Image
                img_data = pix.tobytes(output_format.lower())
                img = Image.open(io.BytesIO(img_data))

                results.append((img, page_num + 1))

            doc.close()
            return results

        except Exception as e:
            raise Exception(f"PDF 处理失败: {str(e)}")

    @staticmethod
    def pdf_to_temp_images(
        pdf_path: str,
        dpi: int = 200,
        max_pages: Optional[int] = None,
        cleanup: bool = True
    ) -> List[Tuple[str, int]]:
        """
        将 PDF 转换为临时图片文件

        Args:
            pdf_path: PDF 文件路径
            dpi: 分辨率
            max_pages: 最大处理页数
            cleanup: 是否在关闭时清理临时文件

        Returns:
            [(temp_file_path, page_number), ...] 列表
        """
        images = PDFProcessor.pdf_to_images(pdf_path, dpi, max_pages)
        temp_files = []

        for img, page_num in images:
            # 创建临时文件
            fd, temp_path = tempfile.mkstemp(suffix='.png')
            os.close(fd)

            # 保存图片
            img.save(temp_path, 'PNG')
            temp_files.append((temp_path, page_num))

        return temp_files

    @staticmethod
    def get_pdf_info(pdf_path: str) -> dict:
        """
        获取 PDF 文件信息

        Args:
            pdf_path: PDF 文件路径

        Returns:
            PDF 信息字典
        """
        try:
            doc = fitz.open(pdf_path)
            info = {
                'page_count': doc.page_count,
                'metadata': doc.metadata,
                'size_bytes': os.path.getsize(pdf_path)
            }
            doc.close()
            return info
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def validate_file(file_path: str, max_size_mb: int = 50) -> Tuple[bool, str]:
        """
        验证文件是否可处理

        Args:
            file_path: 文件路径
            max_size_mb: 最大文件大小（MB）

        Returns:
            (是否有效, 错误消息)
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, f"文件不存在: {file_path}"

        # 检查文件类型
        file_type = PDFProcessor.get_file_type(file_path)
        if file_type == 'unknown':
            return False, f"不支持的文件格式: {os.path.splitext(file_path)[1]}"

        # 检查文件大小
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return False, f"文件过大: {file_size_mb:.2f}MB > {max_size_mb}MB"

        # 如果是 PDF，检查页数
        if file_type == 'pdf':
            info = PDFProcessor.get_pdf_info(file_path)
            if 'error' in info:
                return False, f"PDF 读取失败: {info['error']}"

            page_count = info.get('page_count', 0)
            if page_count > 100:
                return False, f"PDF 页数过多: {page_count} > 100"

        return True, ""


# 便捷函数
def convert_pdf_to_images(pdf_path: str, **kwargs) -> List[Tuple[Image.Image, int]]:
    """便捷函数：PDF 转图片"""
    return PDFProcessor.pdf_to_images(pdf_path, **kwargs)


def is_pdf(file_path: str) -> bool:
    """便捷函数：判断是否为 PDF"""
    return PDFProcessor.get_file_type(file_path) == 'pdf'


def get_file_page_count(file_path: str) -> int:
    """便捷函数：获取文件页数（图片返回1，PDF返回实际页数）"""
    file_type = PDFProcessor.get_file_type(file_path)
    if file_type == 'pdf':
        info = PDFProcessor.get_pdf_info(file_path)
        return info.get('page_count', 1)
    return 1


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("用法: python pdf_utils.py <pdf_file>")
        sys.exit(1)

    pdf_file = sys.argv[1]

    # 验证文件
    valid, msg = PDFProcessor.validate_file(pdf_file)
    if not valid:
        print(f"❌ 文件验证失败: {msg}")
        sys.exit(1)

    # 获取信息
    info = PDFProcessor.get_pdf_info(pdf_file)
    print(f"📄 PDF 信息:")
    print(f"   页数: {info['page_count']}")
    print(f"   大小: {info['size_bytes'] / 1024:.2f} KB")

    # 转换前 3 页
    print(f"\n🔄 转换前 3 页为图片...")
    images = PDFProcessor.pdf_to_images(pdf_file, max_pages=3)

    for img, page_num in images:
        print(f"   页面 {page_num}: {img.size[0]}x{img.size[1]} 像素")

    print(f"\n✅ 测试完成")
