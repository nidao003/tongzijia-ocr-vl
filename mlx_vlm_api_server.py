#!/usr/bin/env python3
"""
MLX-VLM API 服务
直接使用 MLX-VLM 提供高性能 OCR 识别服务
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import uvicorn
import io
import base64
from PIL import Image
import requests
import json

# 创建 FastAPI 应用
app = FastAPI(
    title="MLX-VLM OCR API",
    description="基于 MLX-VLM 的高性能 OCR 识别服务",
    version="1.0.0"
)

# MLX-VLM 服务配置
MLX_SERVER_URL = "http://localhost:8111"

def ocr_with_mlx_vlm(image_data: bytes) -> dict:
    """使用 MLX-VLM 进行 OCR 识别"""

    # 转换图片为 Base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    # 构造请求
    payload = {
        "model": "PaddlePaddle/PaddleOCR-VL-1.5",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请识别这张图片中的所有文字内容，包括中英文。请直接返回识别的文字，不要添加任何解释。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.1
    }

    try:
        # 调用 MLX-VLM API
        response = requests.post(
            f"{MLX_SERVER_URL}/v1/chat/completions",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            usage = result.get('usage', {})

            return {
                'success': True,
                'text': content,
                'usage': {
                    'input_tokens': usage.get('input_tokens', 0),
                    'output_tokens': usage.get('output_tokens', 0),
                    'total_tokens': usage.get('total_tokens', 0),
                    'peak_memory_mb': usage.get('peak_memory', 0)
                }
            }
        else:
            return {
                'success': False,
                'error': f'MLX-VLM API 错误: {response.status_code}',
                'details': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'请求失败: {str(e)}'
        }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "MLX-VLM OCR API 服务",
        "version": "1.0.0",
        "backend": "MLX-VLM (Apple Silicon 加速)",
        "endpoints": {
            "/health": "健康检查",
            "/ocr": "OCR 识别（POST，支持文件上传）",
            "/ocr/base64": "OCR 识别（POST，支持 Base64）",
            "/docs": "API 文档"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查 MLX-VLM 服务
        response = requests.get(f"{MLX_SERVER_URL}/v1/models", timeout=5)
        mlx_status = response.status_code == 200
    except:
        mlx_status = False

    return {
        "status": "healthy" if mlx_status else "degraded",
        "mlx_vlm_service": "running" if mlx_status else "unavailable",
        "api_server": "running"
    }

@app.post("/ocr")
async def ocr_file(file: UploadFile = File(...)):
    """
    OCR 文件识别

    参数:
    - file: 上传的图片文件

    返回: JSON 格式的识别结果
    """
    try:
        # 检查文件类型
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.content_type}"
            )

        # 读取文件
        contents = await file.read()

        # 执行 OCR
        result = ocr_with_mlx_vlm(contents)

        if result['success']:
            return {
                "filename": file.filename,
                "text": result['text'],
                "usage": result['usage']
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'OCR 识别失败')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理失败: {str(e)}"
        )

@app.post("/ocr/base64")
async def ocr_base64(image_base64: str = Form(...)):
    """
    OCR Base64 识别

    参数:
    - image_base64: Base64 编码的图片数据

    返回: JSON 格式的识别结果
    """
    try:
        # 解码 Base64
        import base64
        image_data = base64.b64decode(image_base64)

        # 执行 OCR
        result = ocr_with_mlx_vlm(image_data)

        if result['success']:
            return {
                "text": result['text'],
                "usage": result['usage']
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'OCR 识别失败')
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理失败: {str(e)}"
        )

if __name__ == "__main__":
    print("="*60)
    print("启动 MLX-VLM OCR API 服务")
    print("="*60)
    print("服务地址: http://localhost:8001")
    print("API 文档: http://localhost:8001/docs")
    print("健康检查: http://localhost:8001/health")
    print("="*60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
