#!/usr/bin/env python3
"""
MLX-VLM API 服务
直接使用 MLX-VLM 提供高性能 OCR 识别服务
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import io
import base64
import os
from PIL import Image
import requests
import json
from pdf_utils import PDFProcessor
from typing import List, Optional
import asyncio

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
async def ocr_file(
    file: UploadFile = File(...),
    merge_pdf_pages: bool = True,
    max_pdf_pages: int = None
):
    """
    OCR 文件识别（支持图片和PDF）

    参数:
    - file: 上传的文件（图片或PDF）
    - merge_pdf_pages: 是否合并PDF所有页面（默认True）
    - max_pdf_pages: PDF最大处理页数（默认全部）

    返回: JSON 格式的识别结果
    """
    try:
        # 读取文件内容
        contents = await file.read()

        # 判断文件类型
        filename = file.filename or ""
        ext = os.path.splitext(filename)[1].lower()

        if ext == '.pdf':
            # 处理 PDF
            return await ocr_pdf(contents, filename, merge_pdf_pages, max_pdf_pages)
        else:
            # 处理图片
            # 检查文件类型
            if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/bmp", "image/gif"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件类型: {file.content_type}"
                )

            # 执行 OCR
            result = ocr_with_mlx_vlm(contents)

            if result['success']:
                return {
                    "filename": file.filename,
                    "file_type": "image",
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


async def ocr_pdf(
    pdf_data: bytes,
    filename: str,
    merge_pages: bool = True,
    max_pages: int = None
):
    """处理 PDF 文件"""
    import tempfile

    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_data)
        tmp_path = tmp.name

    try:
        # 转换 PDF 为图片
        images = PDFProcessor.pdf_to_images(tmp_path, dpi=200, max_pages=max_pages)

        if not images:
            raise HTTPException(
                status_code=400,
                detail="PDF 文件为空或无法读取"
            )

        # 逐页识别
        page_results = []
        all_text = []

        for img, page_num in images:
            # 将 PIL Image 转换为字节
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_data = img_bytes.getvalue()

            # 执行 OCR
            result = ocr_with_mlx_vlm(img_data)

            if result['success']:
                page_text = result.get('text', '')
                page_results.append({
                    'page': page_num,
                    'text': page_text,
                    'usage': result.get('usage', {})
                })
                all_text.append(page_text)
            else:
                page_results.append({
                    'page': page_num,
                    'error': result.get('error', '识别失败')
                })

        # 合并结果
        merged_text = '\n\n'.join(all_text) if merge_pages else all_text

        return {
            "filename": filename,
            "file_type": "pdf",
            "total_pages": len(images),
            "text": merged_text if merge_pages else None,
            "pages": page_results,
            "usage": {
                "total_pages": len(images),
                "successful_pages": len([r for r in page_results if 'error' not in r])
            }
        }

    finally:
        # 清理临时文件
        try:
            os.unlink(tmp_path)
        except:
            pass

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


@app.post("/ocr/batch")
async def ocr_batch(
    files: List[UploadFile] = File(...),
    merge_pdf_pages: bool = True,
    max_pdf_pages: int = None
):
    """
    批量OCR识别（支持多文件）

    参数:
    - files: 上传的多个文件（图片或PDF）
    - merge_pdf_pages: 是否合并PDF所有页面（默认True）
    - max_pdf_pages: PDF最大处理页数（默认全部）

    返回: JSON 格式的批量识别结果
    """
    if len(files) > 50:
        raise HTTPException(
            status_code=400,
            detail="单次请求文件数量不能超过50个"
        )

    results = []
    successful = 0
    failed = 0

    for file in files:
        try:
            # 读取文件内容
            contents = await file.read()

            # 判断文件类型
            filename = file.filename or ""
            ext = os.path.splitext(filename)[1].lower()

            if ext == '.pdf':
                # 处理 PDF
                result = await ocr_pdf(contents, filename, merge_pdf_pages, max_pdf_pages)
                result['success'] = True
                results.append(result)
                successful += 1
            else:
                # 处理图片
                if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/bmp", "image/gif"]:
                    results.append({
                        "filename": filename,
                        "success": False,
                        "error": f"不支持的文件类型: {file.content_type}"
                    })
                    failed += 1
                    continue

                # 执行 OCR
                ocr_result = ocr_with_mlx_vlm(contents)

                if ocr_result['success']:
                    results.append({
                        "filename": filename,
                        "file_type": "image",
                        "success": True,
                        "text": ocr_result['text'],
                        "usage": ocr_result['usage']
                    })
                    successful += 1
                else:
                    results.append({
                        "filename": filename,
                        "success": False,
                        "error": ocr_result.get('error', 'OCR 识别失败')
                    })
                    failed += 1

        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": f"处理失败: {str(e)}"
            })
            failed += 1

    return {
        "total_files": len(files),
        "successful": successful,
        "failed": failed,
        "results": results
    }


@app.post("/ocr/base64")
async def ocr_base64(
    image_base64: str = Form(...),
    file_type: str = Form("png")
):
    """
    OCR Base64 识别

    参数:
    - image_base64: Base64 编码的图片数据
    - file_type: 文件类型（png, jpg, pdf等）

    返回: JSON 格式的识别结果
    """
    try:
        # 解码 Base64
        image_data = base64.b64decode(image_base64)

        # 如果是 PDF，需要先保存为临时文件
        if file_type.lower() == 'pdf':
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(image_data)
                tmp_path = tmp.name

            try:
                result = await ocr_pdf(image_data, "document.pdf", True, None)
                return result
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        else:
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
