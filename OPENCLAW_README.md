# OpenClaw 快速集成指南

## 🚀 30 秒快速开始

### 1. 确认服务运行
```bash
curl http://localhost:8001/health
```

### 2. 调用 API
```bash
curl -X POST -F "file=@image.png" http://localhost:8001/ocr
```

### 3. 获取结果
```json
{
  "filename": "image.png",
  "text": "识别的文字内容"
}
```

---

## 📦 安装配置

### Step 1: 环境准备

确保 Python 3.11+ 已安装：
```bash
python3 --version
```

### Step 2: 复制工具文件

将 `paddleocr_tool.py` 复制到 OpenClaw 项目的工具目录：
```bash
cp /Users/daodao/dsl/paddleocr-vl/paddleocr_tool.py /path/to/openclaw/tools/
```

### Step 3: 配置 OpenClaw

在 OpenClaw 配置中添加 PaddleOCR 工具：

```python
# 在 OpenClaw 的工具配置中
{
  "name": "paddleocr",
  "module": "tools.paddleocr_tool",
  "functions": ["quick_recognize", "batch_recognize"]
}
```

---

## 🔧 集成方式

### 方式 A: 直接导入（推荐）

```python
# OpenClaw 代码中
import sys
sys.path.append('/Users/daodao/dsl/paddleocr-vl')

from paddleocr_tool import quick_recognize

def process_document(image_path):
    """处理文档"""
    text = quick_recognize(image_path)
    return {
        'text': text,
        'source': 'paddleocr',
        'confidence': 'high'
    }
```

### 方式 B: HTTP 调用

```python
import requests

def ocr_via_http(image_path):
    """通过 HTTP 调用 OCR"""
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            'http://localhost:8001/ocr',
            files=files,
            timeout=60
        )
    return response.json()
```

### 方式 C: MCP Server

创建 MCP Server 配置 `paddleocr_mcp.json`：

```json
{
  "mcpServers": {
    "paddleocr": {
      "command": "python",
      "args": [
        "/Users/daodao/dsl/paddleocr-vl/paddleocr_tool.py"
      ],
      "env": {
        "API_BASE_URL": "http://localhost:8001"
      }
    }
  }
}
```

---

## 📚 API 参考

### 核心函数

#### 1. quick_recognize(image_path)
**最简单的识别接口**

```python
from paddleocr_tool import quick_recognize

text = quick_recognize("/path/to/image.png")
print(text)  # 识别的文字
```

**参数**: `image_path` (str) - 图片路径
**返回**: `str` - 识别的文字内容

---

#### 2. batch_recognize(image_paths)
**批量识别接口**

```python
from paddleocr_tool import batch_recognize

results = batch_recognize([
    "/path/to/doc1.png",
    "/path/to/doc2.png"
])

for result in results:
    if result['success']:
        print(f"{result['filename']}: {result['text']}")
```

**参数**: `image_paths` (list) - 图片路径列表
**返回**: `list` - 识别结果列表

---

#### 3. PaddleOCRTool 类
**完整工具类**

```python
from paddleocr_tool import PaddleOCRTool

tool = PaddleOCRTool()

# 检查服务状态
health = tool.health_check()

# 识别图片
result = tool.recognize_file("image.png")

# Base64 识别
result = tool.recognize_base64(base64_data)

# 批量识别
results = tool.batch_recognize(image_list)
```

---

## 💡 使用示例

### 示例 1: 文档处理流水线

```python
from paddleocr_tool import quick_recognize
import os

def document_pipeline(doc_folder):
    """文档处理流水线"""
    results = []

    for filename in os.listdir(doc_folder):
        if filename.endswith(('.png', '.jpg')):
            image_path = os.path.join(doc_folder, filename)
            text = quick_recognize(image_path)

            results.append({
                'filename': filename,
                'text': text,
                'status': 'success'
            })

    return results
```

### 示例 2: 错误处理

```python
from paddleocr_tool import PaddleOCRTool

tool = PaddleOCRTool()

def safe_recognize(image_path):
    """安全的识别函数"""
    result = tool.recognize_file(image_path)

    if result['success']:
        return {
            'status': 'success',
            'text': result['text']
        }
    else:
        return {
            'status': 'error',
            'error': result['error']
        }
```

### 示例 3: 进度监控

```python
from paddleocr_tool import PaddleOCRTool

def progress_handler(current, total):
    """进度回调"""
    percent = (current / total) * 100
    print(f"处理进度: {percent:.1f}%")

tool = PaddleOCRTool()
results = tool.batch_recognize(
    image_list,
    callback=progress_handler
)
```

---

## ⚡ 性能优化

### 1. 批量处理
```python
# 不推荐：循环调用
for path in paths:
    text = quick_recognize(path)  # 每次都有开销

# 推荐：批量调用
results = batch_recognize(paths)  # 更高效
```

### 2. 异步处理
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_batch_recognize(image_paths):
    """异步批量识别"""
    with ThreadPoolExecutor(max_workers=3) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                quick_recognize,
                path
            )
            for path in image_paths
        ]
        return await asyncio.gather(*tasks)
```

### 3. 结果缓存
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_recognize(image_path):
    """带缓存的识别"""
    return quick_recognize(image_path)
```

---

## 🛡️ 错误处理

### 服务未运行
```python
from paddleocr_tool import PaddleOCRTool

tool = PaddleOCRTool()
health = tool.health_check()

if health.get('status') != 'healthy':
    print("⚠️  服务未运行，请先启动服务")
    print("启动命令: cd /Users/daodao/dsl/paddleocr-vl && ./start_services.sh")
```

### 请求超时
```python
try:
    result = tool.recognize_file("large_image.png", timeout=120)
except requests.exceptions.Timeout:
    print("⚠️  请求超时，请尝试:")
    print("1. 压缩图片大小")
    print("2. 分批处理")
    print("3. 增加超时时间")
```

### 格式错误
```python
valid_extensions = ['.png', '.jpg', '.jpeg', '.webp']

if not any(image_path.lower().endswith(ext) for ext in valid_extensions):
    print(f"⚠️  不支持的格式，仅支持: {', '.join(valid_extensions)}")
```

---

## 📊 监控和日志

### 性能监控
```python
import time
from paddleocr_tool import PaddleOCRTool

def monitored_recognize(image_path):
    """带监控的识别"""
    tool = PaddleOCRTool()

    start_time = time.time()
    result = tool.recognize_file(image_path)
    elapsed_time = time.time() - start_time

    print(f"识别耗时: {elapsed_time:.2f} 秒")
    print(f"资源使用: {result.get('usage', {})}")

    return result
```

### 错误日志
```python
import logging

logging.basicConfig(filename='ocr_errors.log', level=logging.ERROR)

def logged_recognize(image_path):
    """带日志的识别"""
    try:
        return quick_recognize(image_path)
    except Exception as e:
        logging.error(f"识别失败 {image_path}: {str(e)}")
        return None
```

---

## 🔍 测试和调试

### 测试脚本
```python
#!/usr/bin/env python3
"""测试 PaddleOCR 集成"""

import sys
sys.path.append('/Users/daodao/dsl/paddleocr-vl')

from paddleocr_tool import quick_recognize, PaddleOCRTool

def test_basic():
    """基础测试"""
    print("测试 1: 基础识别")
    text = quick_recognize("test_image.png")
    print(f"✅ 结果: {text}")

def test_health():
    """健康检查"""
    print("\n测试 2: 健康检查")
    tool = PaddleOCRTool()
    health = tool.health_check()
    print(f"✅ 状态: {health}")

def test_batch():
    """批量测试"""
    print("\n测试 3: 批量识别")
    from paddleocr_tool import batch_recognize
    results = batch_recognize(["test_image.png"])
    print(f"✅ 完成: {len(results)} 张")

if __name__ == "__main__":
    test_basic()
    test_health()
    test_batch()
    print("\n✅ 所有测试通过")
```

---

## 📞 获取帮助

### 查看文档
```bash
cd /Users/daodao/dsl/paddleocr-vl
cat OPENCLAW_GUIDE.md      # 完整指南
cat openclaw_config.json    # 配置示例
```

### 运行示例
```bash
cd /Users/daodao/dsl/paddleocr-vl
.venv_paddleocr/bin/python paddleocr_tool.py
```

### API 文档
访问在线文档: http://localhost:8001/docs

---

## 🎯 快速参考

| 任务 | 函数 | 示例 |
|------|------|------|
| 简单识别 | `quick_recognize(path)` | `text = quick_recognize("img.png")` |
| 批量识别 | `batch_recognize(paths)` | `results = batch_recognize(paths)` |
| 详细结果 | `PaddleOCRTool().recognize_file(path)` | `result = tool.recognize_file("img.png")` |
| 健康检查 | `PaddleOCRTool().health_check()` | `status = tool.health_check()` |

---

**版本**: 1.0.0
**更新**: 2025年
**路径**: /Users/daodao/dsl/paddleocr-vl
