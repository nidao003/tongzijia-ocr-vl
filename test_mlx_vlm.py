#!/usr/bin/env python3
"""
MLX-VLM 推理服务测试脚本
测试 MLX-VLM 推理加速功能
"""

import requests
import time
import sys

MLX_SERVER_URL = "http://localhost:8111"

def check_mlx_server():
    """检查 MLX-VLM 服务状态"""
    print("="*60)
    print("检查 MLX-VLM 服务状态")
    print("="*60)

    try:
        # MLX-VLM 服务可能没有健康检查端点，我们尝试访问根路径
        response = requests.get(MLX_SERVER_URL, timeout=5)
        print(f"✅ MLX-VLM 服务正在运行")
        print(f"状态码: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ MLX-VLM 服务未运行")
        print(f"\n请先启动 MLX-VLM 服务:")
        print(f"   cd /Users/daodao/dsl/paddleocr-vl")
        print(f"   .venv_paddleocr/bin/mlx_vlm.server --port 8111")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return False

def test_paddleocr_with_mlx(image_path):
    """测试 PaddleOCR-VL + MLX-VLM 集成"""
    print("\n" + "="*60)
    print("测试 PaddleOCR-VL + MLX-VLM 集成")
    print("="*60)

    try:
        from paddleocr import PaddleOCRVL

        print("\n⏳ 初始化 PaddleOCR-VL（使用 MLX-VLM 后端）...")
        ocr = PaddleOCRVL(
            vl_rec_backend="mlx-vlm-server",
            vl_rec_server_url="http://localhost:8111/",
            vl_rec_api_model_name="PaddlePaddle/PaddleOCR-VL-1.5"
        )

        print("⏳ 正在识别...")
        start_time = time.time()
        result = ocr.predict(image_path)
        elapsed_time = time.time() - start_time

        print(f"\n✅ MLX-VLM 推理成功！")
        print(f"⏱️  耗时: {elapsed_time:.2f} 秒")

        # 显示结果
        if hasattr(result, '__iter__') and len(result) > 0:
            print(f"\n识别结果（第一页）:")
            first_result = result[0]
            if hasattr(first_result, 'items'):
                for key, value in first_result.items():
                    if key == 'layout_dets' and value:
                        print(f"\n检测到 {len(value)} 个元素:")
                        for idx, det in enumerate(value[:5]):  # 只显示前5个
                            print(f"  {idx+1}. {det.get('label', 'unknown')}: {det.get('content', '')[:50]}")
                    elif key != 'input_imgs' and key != 'imgs_in_doc':
                        print(f"{key}: {value}")

        return True, elapsed_time

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0

def test_paddleocr_native(image_path):
    """测试 PaddleOCR-VL 原生推理（无加速）"""
    print("\n" + "="*60)
    print("测试 PaddleOCR-VL 原生推理（无加速）")
    print("="*60)

    try:
        from paddleocr import PaddleOCRVL

        print("\n⏳ 初始化 PaddleOCR-VL（原生后端）...")
        ocr = PaddleOCRVL()

        print("⏳ 正在识别...")
        start_time = time.time()
        result = ocr.predict(image_path)
        elapsed_time = time.time() - start_time

        print(f"\n✅ 原生推理成功！")
        print(f"⏱️  耗时: {elapsed_time:.2f} 秒")

        # 显示结果
        if hasattr(result, '__iter__') and len(result) > 0:
            print(f"\n识别结果（第一页）:")
            first_result = result[0]
            if hasattr(first_result, 'items'):
                for key, value in first_result.items():
                    if key == 'layout_dets' and value:
                        print(f"\n检测到 {len(value)} 个元素:")
                        for idx, det in enumerate(value[:5]):  # 只显示前5个
                            print(f"  {idx+1}. {det.get('label', 'unknown')}: {det.get('content', '')[:50]}")
                    elif key != 'input_imgs' and key != 'imgs_in_doc':
                        print(f"{key}: {value}")

        return True, elapsed_time

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0

def main():
    """主函数"""
    print("="*60)
    print("MLX-VLM 推理加速测试")
    print("="*60)

    # 检查 MLX-VLM 服务
    mlx_running = check_mlx_server()

    # 测试图片
    test_image = "test_image.png"

    if mlx_running:
        # 测试 MLX-VLM 加速
        mlx_success, mlx_time = test_paddleocr_with_mlx(test_image)

        # 测试原生推理
        native_success, native_time = test_paddleocr_native(test_image)

        # 性能对比
        print("\n" + "="*60)
        print("性能对比总结")
        print("="*60)
        print(f"MLX-VLM 加速: {'✅ 成功' if mlx_success else '❌ 失败'} - {mlx_time:.2f} 秒")
        print(f"原生推理: {'✅ 成功' if native_success else '❌ 失败'} - {native_time:.2f} 秒")

        if mlx_success and native_success:
            speedup = native_time / mlx_time
            print(f"\n🚀 加速比: {speedup:.2f}x")
            if speedup > 1:
                print(f"✨ MLX-VLM 比原生推理快 {speedup:.2f} 倍！")
            else:
                print(f"⚠️  MLX-VLM 比原生推理慢 {1/speedup:.2f} 倍")

    else:
        print("\n" + "="*60)
        print("仅测试原生推理")
        print("="*60)
        native_success, native_time = test_paddleocr_native(test_image)
        print(f"\n原生推理: {'✅ 成功' if native_success else '❌ 失败'} - {native_time:.2f} 秒")

if __name__ == "__main__":
    main()
