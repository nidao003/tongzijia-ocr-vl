# PaddleOCR-VL 快速使用指南

## 🚀 快速开始

### 当前服务状态 ✅
- **API 服务**：运行中 (http://localhost:8000)
- **MLX-VLM 服务**：运行中 (http://localhost:8111)

---

## 📋 三种使用方式

### 方式一：CLI 命令行（最简单）

```bash
cd /Users/daodao/dsl/paddleocr-vl

# 识别单张图片
.venv_paddleocr/bin/paddleocr doc_parser --input image.png

# 识别多张图片
.venv_paddleocr/bin/paddleocr doc_parser --input image1.png image2.jpg
```

### 方式二：Python API（推荐用于集成）

```python
from paddleocr import PaddleOCRVL

# 初始化（原生推理）
ocr = PaddleOCRVL()

# 识别图片
result = ocr.predict("image.png")

# 处理结果
for page in result:
    for element in page['layout_dets']:
        print(f"{element['label']}: {element['content']}")
```

### 方式三：REST API（推荐用于生产环境）

```bash
# 健康检查
curl http://localhost:8000/health

# 上传文件识别
curl -X POST \
  -F "file=@image.png" \
  http://localhost:8000/ocr

# Base64 识别
curl -X POST \
  -F "image_base64=$(base64 -i image.png)" \
  http://localhost:8000/ocr/base64

# 查看 API 文档
open http://localhost:8000/docs
```

---

## 🛠️ 服务管理

### 启动服务
```bash
cd /Users/daodao/dsl/paddleocr-vl

# 使用启动脚本（推荐）
./start_services.sh

# 手动启动
.venv_paddleocr/bin/python api_server.py
```

### 停止服务
```bash
cd /Users/daodao/dsl/paddleocr-vl

# 使用停止脚本（推荐）
./stop_services.sh

# 手动停止
pkill -f api_server.py
pkill -f mlx_vlm.server
```

### 检查服务状态
```bash
# 检查端口占用
lsof -i :8000  # API 服务
lsof -i :8111  # MLX-VLM 服务

# 查看日志
tail -f api_server.log
tail -f mlx_vlm_server.log

# 测试服务
curl http://localhost:8000/health
```

---

## 📊 识别结果格式

### CLI 输出
```
#################
label:	text
bbox:	[49, 50, 148, 62]
content:	Hello PaddleOCR-VL!
#################
```

### Python API 结果
```python
{
    'input_path': 'image.png',
    'layout_dets': [
        {
            'label': 'text',
            'bbox': [49, 50, 148, 62],
            'content': 'Hello PaddleOCR-VL!',
            'score': 0.99
        }
    ],
    'parsing_res_list': [...]
}
```

### REST API 结果
```json
{
    "filename": "image.png",
    "result": [...]
}
```

---

## 🎯 支持的识别类型

PaddleOCR-VL 可以识别以下文档元素：

- ✅ **文本**（text）：普通文本段落
- ✅ **标题**（title、paragraph_title）：各级标题
- ✅ **表格**（table）：表格内容
- ✅ **公式**（formula）：数学公式
- ✅ **图表**（figure、chart）：图片和图表
- ✅ **印章**（seal）：公章和印章
- ✅ **页眉页脚**（header、footer）：页面布局元素

---

## 🌍 多语言支持

PaddleOCR-VL 支持 **109 种语言**，包括但不限于：

- ✅ 中文（简体、繁体）
- ✅ 英文
- ✅ 日文
- ✅ 韩文
- ✅ 阿拉伯文
- ✅ 俄文
- ✅ 德文
- ✅ 法文
- ✅ 西班牙文

---

## 💡 使用示例

### 示例 1：批量处理图片

```python
from paddleocr import PaddleOCRVL
import os

ocr = PaddleOCRVL()
image_dir = "images/"

# 批量处理
for filename in os.listdir(image_dir):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(image_dir, filename)
        result = ocr.predict(image_path)
        print(f"已处理: {filename}")
```

### 示例 2：提取表格数据

```python
from paddleocr import PaddleOCRVL

ocr = PaddleOCRVL()
result = ocr.predict("table.png")

# 提取表格
for page in result:
    for element in page['layout_dets']:
        if element['label'] == 'table':
            print("发现表格:", element['content'])
```

### 示例 3：API 调用示例

```python
import requests

# 上传文件识别
with open('image.png', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/ocr',
        files={'file': f}
    )
    result = response.json()
    print(result)
```

---

## ⚠️ 常见问题

### Q1：首次运行很慢？
**A**：首次运行需要下载模型权重（2-3GB），后续启动会快很多。

### Q2：内存占用高？
**A**：PaddleOCR-VL 是深度学习模型，需要一定内存。建议 16GB+ 内存。

### Q3：识别速度慢？
**A**：
- 当前使用 CPU 推理（156 秒/张）
- MLX-VLM 加速待配置（预计提升 3-5x）

### Q4：支持哪些图片格式？
**A**：JPEG、PNG、WebP 等常见格式。

### Q5：可以处理 PDF 吗？
**A**：当前版本不支持直接处理 PDF，需要先转换为图片。

---

## 🔗 相关文档

- 📖 [完整部署指南](./README.md)
- 📊 [部署完成报告](./DEPLOYMENT_REPORT.md)
- 📘 [官方文档](https://github.com/PaddlePaddle/PaddleOCR)

---

## 📞 获取帮助

遇到问题？

1. **查看日志**：`tail -f api_server.log`
2. **检查服务**：`curl http://localhost:8000/health`
3. **参考文档**：查看相关文档
4. **测试功能**：运行测试脚本验证

---

**当前项目路径**：`/Users/daodao/dsl/paddleocr-vl`

**快速测试命令**：
```bash
cd /Users/daodao/dsl/paddleocr-vl
.venv_paddleocr/bin/python test_ocr.py
```

🎉 **开始使用吧！**
