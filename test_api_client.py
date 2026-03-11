#!/usr/bin/env python3
"""
PaddleOCR-VL API 客户端测试脚本
"""

import requests
import base64
import sys
import os

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查"""
    print("="*60)
    print("测试 1: 健康检查")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

def test_ocr_file(image_path):
    """测试文件上传 OCR"""
    print("\n" + "="*60)
    print("测试 2: 文件上传 OCR")
    print("="*60)

    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return False

    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {'return_format': 'json'}

            print(f"⏳ 正在上传文件: {image_path}")
            response = requests.post(
                f"{API_BASE_URL}/ocr",
                files=files,
                data=data,
                timeout=60
            )

        if response.status_code == 200:
            print("✅ OCR 识别成功")
            result = response.json()
            print(f"\n识别结果:")
            print(result)
            return True
        else:
            print(f"❌ OCR 识别失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def test_ocr_base64(image_path):
    """测试 Base64 OCR"""
    print("\n" + "="*60)
    print("测试 3: Base64 OCR")
    print("="*60)

    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return False

    try:
        # 读取图片并转换为 Base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

        data = {
            'image_base64': image_base64,
            'return_format': 'json'
        }

        print(f"⏳ 正在识别 Base64 图片...")
        response = requests.post(
            f"{API_BASE_URL}/ocr/base64",
            data=data,
            timeout=60
        )

        if response.status_code == 200:
            print("✅ Base64 OCR 识别成功")
            result = response.json()
            print(f"\n识别结果:")
            print(result)
            return True
        else:
            print(f"❌ Base64 OCR 识别失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("PaddleOCR-VL API 客户端测试")
    print("="*60)
    print(f"API 服务地址: {API_BASE_URL}")
    print("="*60)

    # 测试健康检查
    health_ok = test_health_check()

    if not health_ok:
        print("\n❌ API 服务未运行，请先启动服务:")
        print("   .venv_paddleocr/bin/python api_server.py")
        return

    # 测试文件上传
    test_image = "test_image.png"
    file_ok = test_ocr_file(test_image)

    # 测试 Base64
    base64_ok = test_ocr_base64(test_image)

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"文件上传: {'✅ 通过' if file_ok else '❌ 失败'}")
    print(f"Base64 识别: {'✅ 通过' if base64_ok else '❌ 失败'}")

if __name__ == "__main__":
    main()
