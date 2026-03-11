#!/usr/bin/env python3
"""
MLX-VLM API 使用示例
展示如何调用 MLX-VLM API 进行文档识别
"""

import requests
import base64
import json
import time

# API 服务地址
API_BASE_URL = "http://localhost:8001"

def example_1_simple_ocr():
    """示例 1: 简单的 OCR 识别"""
    print("="*60)
    print("示例 1: 简单的 OCR 识别")
    print("="*60)

    # 准备图片
    image_path = "test_image.png"

    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}

        # 调用 API
        print(f"正在识别图片: {image_path}")
        start_time = time.time()

        response = requests.post(
            f"{API_BASE_URL}/ocr",
            files=files,
            timeout=60
        )

        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 识别成功！")
            print(f"⏱️  耗时: {elapsed_time:.2f} 秒")
            print(f"\n识别结果:")
            print(result['text'])
            print(f"\n资源使用:")
            print(f"- 输入 tokens: {result['usage']['input_tokens']}")
            print(f"- 输出 tokens: {result['usage']['output_tokens']}")
            print(f"- 总计 tokens: {result['usage']['total_tokens']}")
            print(f"- 峰值内存: {result['usage']['peak_memory_mb']:.2f} MB")
        else:
            print(f"❌ 识别失败: {response.text}")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def example_2_base64_ocr():
    """示例 2: 使用 Base64 编码的图片"""
    print("\n" + "="*60)
    print("示例 2: 使用 Base64 编码的图片")
    print("="*60)

    try:
        # 读取图片并转换为 Base64
        with open('test_image.png', 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 调用 API
        print("正在识别 Base64 图片...")
        response = requests.post(
            f"{API_BASE_URL}/ocr/base64",
            data={'image_base64': image_base64},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 识别成功！")
            print(f"\n识别结果:")
            print(result['text'])
        else:
            print(f"❌ 识别失败: {response.text}")

    except Exception as e:
        print(f"❌ 错误: {str(e)}")

def example_3_batch_processing():
    """示例 3: 批量处理多张图片"""
    print("\n" + "="*60)
    print("示例 3: 批量处理多张图片")
    print("="*60)

    # 模拟多张图片（实际使用时替换为真实路径）
    image_paths = [
        "test_image.png",
        # "image2.png",
        # "image3.png",
    ]

    results = []

    for idx, image_path in enumerate(image_paths, 1):
        print(f"\n处理图片 {idx}/{len(image_paths)}: {image_path}")

        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}

            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/ocr",
                files=files,
                timeout=60
            )
            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                results.append({
                    'filename': image_path,
                    'text': result['text'],
                    'time': elapsed_time
                })
                print(f"✅ 成功 ({elapsed_time:.2f} 秒)")
            else:
                print(f"❌ 失败: {response.text}")

        except Exception as e:
            print(f"❌ 错误: {str(e)}")

    # 输出汇总
    print(f"\n{'='*60}")
    print("批量处理完成")
    print(f"{'='*60}")
    print(f"总图片数: {len(image_paths)}")
    print(f"成功识别: {len(results)}")

    if results:
        total_time = sum(r['time'] for r in results)
        avg_time = total_time / len(results)
        print(f"总耗时: {total_time:.2f} 秒")
        print(f"平均耗时: {avg_time:.2f} 秒/张")

def example_4_error_handling():
    """示例 4: 错误处理和重试"""
    print("\n" + "="*60)
    print("示例 4: 错误处理和重试")
    print("="*60)

    max_retries = 3
    image_path = "test_image.png"

    for attempt in range(1, max_retries + 1):
        print(f"\n尝试 {attempt}/{max_retries}")

        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}

            response = requests.post(
                f"{API_BASE_URL}/ocr",
                files=files,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 识别成功！")
                print(f"结果: {result['text'][:50]}...")
                break
            else:
                print(f"❌ HTTP 错误: {response.status_code}")
                if attempt < max_retries:
                    print("重试中...")
                    time.sleep(2)

        except requests.exceptions.Timeout:
            print(f"❌ 请求超时")
            if attempt < max_retries:
                print("重试中...")
                time.sleep(2)
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            break

def main():
    """主函数"""
    print("="*60)
    print("MLX-VLM API 使用示例")
    print("="*60)
    print(f"API 服务地址: {API_BASE_URL}")
    print("="*60)

    # 检查服务状态
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ MLX-VLM API 服务运行正常\n")
        else:
            print("⚠️  MLX-VLM API 服务状态异常")
            return
    except:
        print("❌ MLX-VLM API 服务未运行")
        print("请先启动服务: ./start_services.sh")
        return

    # 运行示例
    example_1_simple_ocr()
    example_2_base64_ocr()
    example_3_batch_processing()
    example_4_error_handling()

    print("\n" + "="*60)
    print("所有示例运行完成")
    print("="*60)

if __name__ == "__main__":
    main()
