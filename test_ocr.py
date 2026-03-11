#!/usr/bin/env python3
"""
PaddleOCR-VL 测试脚本
测试 CLI 和 Python API 调用
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_test_image(filename="test_image.png"):
    """创建测试图片"""
    # 创建一个简单的测试图片
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)

    # 添加一些文本
    text = "Hello PaddleOCR-VL!\n这是中文测试文本\nTesting OCR on Mac M4"

    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 40)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()

    # 绘制文本
    y_position = 50
    for line in text.split('\n'):
        draw.text((50, y_position), line, fill='black', font=font)
        y_position += 80

    # 保存图片
    img.save(filename)
    print(f"✅ 测试图片已创建: {filename}")
    return filename

def test_cli_command(image_path):
    """测试 CLI 命令"""
    print("\n" + "="*60)
    print("测试 1: CLI 命令（无加速）")
    print("="*60)

    import subprocess
    cmd = [
        ".venv_paddleocr/bin/paddleocr",
        "doc_parser",
        "--input", image_path
    ]

    print(f"执行命令: {' '.join(cmd)}")
    print("\n⏳ 正在处理...（首次运行会下载模型，请耐心等待）")

    result = subprocess.run(
        cmd,
        cwd="/Users/daodao/dsl/paddleocr-vl",
        capture_output=True,
        text=True,
        timeout=300
    )

    if result.returncode == 0:
        print("\n✅ CLI 测试成功！")
        print("\n输出结果:")
        print(result.stdout)
        return True
    else:
        print("\n❌ CLI 测试失败！")
        print("错误信息:")
        print(result.stderr)
        return False

def test_python_api(image_path):
    """测试 Python API"""
    print("\n" + "="*60)
    print("测试 2: Python API（无加速）")
    print("="*60)

    try:
        from paddleocr import PaddleOCRVL

        print("\n⏳ 初始化 PaddleOCR-VL...")
        print("（首次运行会下载模型，请耐心等待）")

        # 创建 PaddleOCR-VL 实例
        ocr = PaddleOCRVL()

        print("\n⏳ 正在识别...")
        result = ocr.predict(image_path)

        print("\n✅ Python API 测试成功！")
        print("\n识别结果:")

        # 处理结果
        if hasattr(result, '__iter__'):
            for idx, res in enumerate(result):
                print(f"\n--- 结果 {idx + 1} ---")
                print(res)
        else:
            print(result)

        return True

    except Exception as e:
        print(f"\n❌ Python API 测试失败！")
        print(f"错误信息: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_mlx_vlm_server(image_path):
    """测试 MLX-VLM 服务"""
    print("\n" + "="*60)
    print("测试 3: MLX-VLM 推理加速（可选）")
    print("="*60)

    print("\n⚠️  注意：MLX-VLM 需要单独启动服务器")
    print("启动命令: .venv_paddleocr/bin/mlx_vlm.server --port 8111")
    print("\n跳过此测试，如需测试请手动启动 MLX-VLM 服务")

    return None

def main():
    """主函数"""
    print("="*60)
    print("PaddleOCR-VL 功能测试")
    print("="*60)

    # 创建测试图片
    image_path = create_test_image()

    # 测试 CLI
    cli_success = test_cli_command(image_path)

    # 测试 Python API
    api_success = test_python_api(image_path)

    # 测试 MLX-VLM（可选）
    mlx_result = test_mlx_vlm_server(image_path)

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"CLI 测试: {'✅ 通过' if cli_success else '❌ 失败'}")
    print(f"Python API 测试: {'✅ 通过' if api_success else '❌ 失败'}")
    print(f"MLX-VLM 测试: {'⏭️  跳过' if mlx_result is None else ('✅ 通过' if mlx_result else '❌ 失败')}")

if __name__ == "__main__":
    main()
