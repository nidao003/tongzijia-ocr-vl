#!/usr/bin/env python3
"""
PaddleOCR-VL API 服务
提供 REST API 接口进行文档解析
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from paddleocr import PaddleOCRVL
import uvicorn
import io
import os
from PIL import Image
from typing import Optional
import base64

# 创建 FastAPI 应用
app = FastAPI(
    title="PaddleOCR-VL API",
    description="文档解析 API 服务，支持文本、表格、公式、图表识别",
    version="1.0.0"
)

# 全局 OCR 实例
ocr_instance = None

def get_ocr_instance():
    """获取或创建 OCR 实例"""
    global ocr_instance
    if ocr_instance is None:
        print("⏳ 初始化 PaddleOCR-VL...")
        ocr_instance = PaddleOCRVL()
        print("✅ PaddleOCR-VL 初始化完成")
    return ocr_instance

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化 OCR"""
    get_ocr_instance()

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "PaddleOCR-VL API 服务",
        "version": "1.0.0",
        "endpoints": {
            "/health": "健康检查",
            "/ocr": "OCR 识别（POST，支持文件上传）",
            "/ocr/url": "OCR 识别（POST，支持 URL）",
            "/docs": "API 文档"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        ocr = get_ocr_instance()
        return {"status": "healthy", "ocr_loaded": ocr is not None}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/ocr")
async def ocr_file(
    file: UploadFile = File(...),
    return_format: str = Form("json")
):
    """
    OCR 文件识别

    参数:
    - file: 上传的图片文件
    - return_format: 返回格式（json 或 markdown）

    返回: JSON 格式的识别结果
    """
    try:
        # 读取上传的文件
        contents = await file.read()

        # 检查文件类型
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file.content_type}。仅支持 JPEG、PNG、WebP 格式"
            )

        # 转换为 PIL Image
        image = Image.open(io.BytesIO(contents))

        # 获取 OCR 实例
        ocr = get_ocr_instance()

        # 执行识别
        print(f"⏳ 正在识别文件: {file.filename}")
        result = ocr.predict(image)

        # 处理结果
        if return_format == "markdown" and hasattr(result, '__iter__'):
            # 提取 Markdown 格式
            output = []
            for res in result:
                if 'markdown' in res:
                    output.append(res['markdown'])
            return {"filename": file.filename, "markdown": "\n\n".join(output)}
        else:
            # 返回完整 JSON
            return {
                "filename": file.filename,
                "result": str(result) if not hasattr(result, '__iter__') else [dict(r) for r in result]
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OCR 识别失败: {str(e)}")

@app.post("/ocr/base64")
async def ocr_base64(
    image_base64: str = Form(...),
    return_format: str = Form("json")
):
    """
    OCR Base64 识别

    参数:
    - image_base64: Base64 编码的图片数据
    - return_format: 返回格式（json 或 markdown）

    返回: JSON 格式的识别结果
    """
    try:
        # 解码 Base64
        image_data = base64.b64decode(image_base64)

        # 转换为 PIL Image
        image = Image.open(io.BytesIO(image_data))

        # 获取 OCR 实例
        ocr = get_ocr_instance()

        # 执行识别
        print("⏳ 正在识别 Base64 图片...")
        result = ocr.predict(image)

        # 处理结果
        if return_format == "markdown" and hasattr(result, '__iter__'):
            output = []
            for res in result:
                if 'markdown' in res:
                    output.append(res['markdown'])
            return {"markdown": "\n\n".join(output)}
        else:
            return {
                "result": str(result) if not hasattr(result, '__iter__') else [dict(r) for r in result]
            }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OCR 识别失败: {str(e)}")

if __name__ == "__main__":
    print("="*60)
    print("启动 PaddleOCR-VL API 服务")
    print("="*60)
    print("服务地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/health")
    print("="*60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
