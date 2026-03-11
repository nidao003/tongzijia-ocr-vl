# PaddleOCR-VL 部署指南

## 📋 部署摘要

**部署时间**：2025年（根据当前日期）
**系统环境**：Mac mini M4，macOS
**Python 版本**：3.11.14
**部署方案**：完整部署 + API 服务化

---

## ✅ 已完成功能

### 1. 环境配置
- ✅ Python 3.11.14 虚拟环境
- ✅ PaddlePaddle 3.2.1
- ✅ PaddleOCR-VL 3.4.0
- ✅ MLX-VLM 0.4.0（推理加速框架）
- ✅ NumPy 1.26.4（兼容性修复）

### 2. 核心功能
- ✅ CLI 命令行工具
- ✅ Python API 调用
- ✅ REST API 服务（FastAPI）
- ✅ 文件上传识别
- ✅ Base64 识别

### 3. API 服务端点
- `GET /` - 服务信息
- `GET /health` - 健康检查
- `POST /ocr` - 文件上传 OCR
- `POST /ocr/base64` - Base64 OCR
- `GET /docs` - Swagger API 文档

---

## 🚀 使用指南

### 启动服务

#### 1. 启动 PaddleOCR-VL API 服务
```bash
cd /Users/daodao/dsl/paddleocr-vl
.venv_paddleocr/bin/python api_server.py
```

#### 2. 启动 MLX-VLM 推理服务（可选）
```bash
.venv_paddleocr/bin/mlx_vlm.server --port 8111
```

### 使用方法

#### CLI 命令行
```bash
.venv_paddleocr/bin/paddleocr doc_parser --input image.png
```

#### Python API
```python
from paddleocr import PaddleOCRVL

# 原生推理
ocr = PaddleOCRVL()
result = ocr.predict("image.png")

# MLX-VLM 加速推理（需要 MLX-VLM 服务运行）
ocr = PaddleOCRVL(
    vl_rec_backend="mlx-vlm-server",
    vl_rec_server_url="http://localhost:8111/",
    vl_rec_api_model_name="PaddlePaddle/PaddleOCR-VL-1.5"
)
result = ocr.predict("image.png")
```

#### REST API
```bash
# 健康检查
curl http://localhost:8000/health

# 文件上传
curl -X POST -F "file=@image.png" http://localhost:8000/ocr

# Base64 识别
curl -X POST -F "image_base64=$(base64 -i image.png)" http://localhost:8000/ocr/base64
```

---

## 📊 性能基准

### 测试环境
- 硬件：Mac mini M4
- 图片：测试图片（800x400 像素）
- 内容：3 行文本（英文 + 中文）

### 性能数据

| 推理方式 | 耗时 | 状态 |
|---------|------|------|
| 原生推理（PaddlePaddle CPU） | 156.59 秒 | ✅ 成功 |
| MLX-VLM 加速 | - | ❌ 集成问题 |

### 识别结果
```
1. text: "Hello PaddleOCR-VL!"
2. paragraph_title: "00000000"
3. text: "Testing OCR on Mac M4"
```

---

## ⚠️ 已知问题

### 1. MLX-VLM 集成问题
- **问题**：Error code: 502 when using MLX-VLM backend
- **原因**：可能需要预先下载模型权重或配置问题
- **状态**：待解决
- **影响**：无法使用 MLX-VLM 推理加速

### 2. NumPy 版本兼容性
- **问题**：NumPy 2.x 与 PaddlePaddle 不兼容
- **解决方案**：降级到 NumPy 1.26.4
- **影响**：opencv-python 有版本警告，但不影响功能

### 3. MLX-VLM 服务配置
- **问题**：服务启动但无法正确处理请求
- **可能原因**：
  - 模型权重未下载
  - API 端点配置不正确
  - 版本兼容性问题

---

## 📁 项目结构

```
/Users/daodao/dsl/paddleocr-vl/
├── .venv_paddleocr/          # Python 虚拟环境
├── api_server.py             # FastAPI 服务
├── test_ocr.py              # 基础功能测试
├── test_api_client.py       # API 客户端测试
├── test_mlx_vlm.py          # MLX-VLM 集成测试
├── test_image.png           # 测试图片
├── api_server.log           # API 服务日志
├── mlx_vlm_server.log       # MLX-VLM 服务日志
└── README.md                # 本文档
```

---

## 🔧 故障排除

### 服务无法启动
1. 检查端口占用：`lsof -i :8000` 或 `lsof -i :8111`
2. 检查日志文件：`tail -f api_server.log`
3. 确认虚拟环境激活：`.venv_paddleocr/bin/python --version`

### OCR 识别失败
1. 检查图片格式（支持 JPEG、PNG、WebP）
2. 查看错误日志
3. 确认模型文件已下载：`ls ~/.paddlex/official_models/`

### MLX-VLM 集成问题
1. 确认 MLX-VLM 服务运行：`curl http://localhost:8111/`
2. 检查服务日志：`tail -f mlx_vlm_server.log`
3. 尝试重新安装 MLX-VLM：`.venv_paddleocr/bin/python -m pip install --force-reinstall "mlx-vlm>=0.3.11"`

---

## 📝 开发建议

### 性能优化
1. **使用 MLX-VLM 加速**：解决集成问题后可显著提升性能
2. **批量处理**：对多张图片进行批量识别
3. **缓存机制**：对相同图片进行结果缓存
4. **并发处理**：使用多进程/多线程处理多个请求

### 生产部署
1. **进程管理**：使用 systemd、supervisord 或 PM2
2. **反向代理**：使用 Nginx 处理负载均衡
3. **监控告警**：添加日志记录和性能监控
4. **容器化**：使用 Docker 进行容器化部署

---

## 📚 参考资料

- [PaddleOCR-VL 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [MLX-VLM GitHub](https://github.com/Blaizzy/mlx-vlm)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Apple Silicon 优化指南](./PaddleOCR-VL\ Apple\ Silicon.md)

---

## 📞 支持与反馈

如遇到问题，请：
1. 检查本文档的故障排除部分
2. 查看相关日志文件
3. 参考官方文档
4. 提交 Issue 或寻求社区支持

---

**部署完成时间**：2025年
**文档版本**：1.0.0
**维护者**：Claude Code
