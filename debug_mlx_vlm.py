#!/usr/bin/env python3
"""
MLX-VLM API 直接测试脚本
用于调试 MLX-VLM 服务的 API 接口
"""

import requests
import base64

MLX_SERVER_URL = "http://localhost:8111"

def test_mlx_vlm_api():
    """测试 MLX-VLM API"""
    print("="*60)
    print("MLX-VLM API 调试测试")
    print("="*60)

    # 准备测试图片
    test_image = "test_image.png"

    try:
        with open(test_image, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

        # 测试 OpenAI 兼容的聊天完成接口
        print("\n测试 OpenAI 兼容接口...")

        payload = {
            "model": "PaddlePaddle/PaddleOCR-VL-1.5",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请识别这张图片中的文字"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }
            ],
            "max_tokens": 512
        }

        response = requests.post(
            f"{MLX_SERVER_URL}/v1/chat/completions",
            json=payload,
            timeout=30
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ API 调用成功！")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ API 调用失败")
            print(f"响应: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_server_status():
    """检查服务器状态"""
    print("\n" + "="*60)
    print("检查 MLX-VLM 服务器状态")
    print("="*60)

    try:
        # 尝试连接服务器
        response = requests.get(MLX_SERVER_URL, timeout=5)
        print(f"服务器响应: {response.status_code}")

        # 显示日志
        print("\n最近日志:")
        try:
            with open("mlx_vlm_server.log", "r") as f:
                logs = f.read()
                print("\n".join(logs.split("\n")[-20:]))
        except:
            print("无法读取日志文件")

    except Exception as e:
        print(f"❌ 服务器未运行: {str(e)}")

def main():
    """主函数"""
    print(f"服务器地址: {MLX_SERVER_URL}\n")

    # 检查服务器状态
    check_server_status()

    # 测试 API
    success = test_mlx_vlm_api()

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    if success:
        print("✅ MLX-VLM API 工作正常")
        print("\n下一步：在 PaddleOCR-VL 中使用 MLX-VLM 后端")
    else:
        print("❌ MLX-VLM API 测试失败")
        print("\n可能的问题:")
        print("1. MLX-VLM 服务未正确启动")
        print("2. API 端点不匹配")
        print("3. 模型未下载或配置错误")
        print("\n建议:")
        print("1. 重启服务: pkill -f mlx_vlm.server")
        print("2. 查看日志: tail -f mlx_vlm_server.log")
        print("3. 检查 MLX-VLM 文档")

if __name__ == "__main__":
    main()
