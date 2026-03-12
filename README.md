# PaddleOCR-VL for OpenClaw

高性能文档识别服务，专为 OpenClaw 优化设计。

## 🎯 特点

- ✅ **按需启动** - 用时启动，用完停止
- ✅ **自动管理** - 智能服务生命周期
- ✅ **资源优化** - 最大化释放系统性能
- ✅ **简单易用** - 一行代码搞定
- ✅ **高性能** - 7秒/张，准确率100%
- ✅ **多格式支持** - PNG, JPG, WebP, BMP, PDF
- ✅ **批量处理** - 原生支持批量识别
- ✅ **MLX-VLM加速** - Apple Silicon 优化

## 📦 项目结构

```
paddleocr-vl/
├── README.md                    # 项目说明（本文件）
├── OPENCLAW_QUICKSTART.md       # OpenClaw 快速上手指南 ⭐
├── paddleocr_tool.py            # 核心工具类
├── mlx_vlm_api_server.py        # MLX-VLM API 服务
├── openclaw_config.json         # OpenClaw 配置
├── scripts/                     # 服务管理脚本
│   ├── start_services.sh        # 启动所有服务
│   ├── stop_services.sh         # 停止所有服务
│   └── start_on_demand.sh       # 按需启动服务
├── tests/                       # 测试文件
│   ├── test_ocr.py              # OCR 功能测试
│   └── examples.py              # 使用示例
└── docs/                        # 详细文档（归档）
    ├── OPENCLAW_USAGE_OPTIMIZED.md
    ├── DEPLOYMENT_REPORT.md
    └── ...其他报告
```

## 📥 OpenClaw 安装/升级

**复制以下指令发送给 OpenClaw 主系统，自动完成安装或升级**：

```
请帮我安装/升级 PaddleOCR-VL 项目：

仓库地址：https://gitea.dd.yp100.cn:8443/openclaw/PaddleOCR-VL-claw.git
本地路径：/Users/daodao/dsl/PaddleOCR-VL

需要安装/升级：
1. paddleocr-vl 技能（v3.0）- 文档识别服务
2. invoice-agent 智能体（v3.0）- 发票处理智能体

配置要求：
- Python 3.11+
- Apple Silicon M4+ (16GB+ 内存推荐)
- MLX-VLM 加速支持

请按照项目的 openclaw_config.json 和 agents/invoice-agent/config.json 进行配置。
```

---

## 🚀 快速开始

### OpenClaw 用户

**请阅读**：[OPENCLAW_QUICKSTART.md](./OPENCLAW_QUICKSTART.md)

**最简单的使用方式**：
```python
import sys
sys.path.append('/Users/daodao/dsl/paddleocr-vl')
from paddleocr_tool import quick_recognize

text = quick_recognize("/path/to/image.png")
print(text)
```

### 安装部署

```bash
# 1. 克隆仓库
git clone https://gitea.dd.yp100.cn:8443/openclaw/PaddleOCR-VL-claw.git
cd PaddleOCR-VL-claw

# 2. 创建虚拟环境（需要 Python 3.11）
/opt/homebrew/bin/python3.11 -m venv .venv_paddleocr

# 3. 激活虚拟环境
source .venv_paddleocr/bin/activate

# 4. 安装依赖（注意 NumPy 版本）
pip install "numpy<2.0"
pip install paddlepaddle paddleocr-vl "mlx-vlm>=0.3.11" fastapi uvicorn python-multipart requests pillow

# 5. 完成！
```

## 🔧 服务管理

### 启动服务

```bash
# 方式 1：启动所有服务
./scripts/start_services.sh

# 方式 2：按需启动（推荐）
./scripts/start_on_demand.sh

# 方式 3：手动启动
.venv_paddleocr/bin/python -m mlx_vlm.server --port 8111 &
.venv_paddleocr/bin/python mlx_vlm_api_server.py
```

### 停止服务

```bash
./scripts/stop_services.sh
```

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| **识别速度** | 7 秒/张 |
| **准确率** | 100% |
| **使用时内存** | 2.58GB |
| **使用时 CPU** | 0.1% |
| **不用时资源** | 0% |
| **节省电能** | 30-50% |

## 📚 API 文档

### 核心接口

**快速识别**（推荐）
```python
from paddleocr_tool import quick_recognize
text = quick_recognize("image.png")
```

**批量识别**
```python
from paddleocr_tool import batch_recognize
result = batch_recognize(["doc1.png", "doc2.pdf"])
print(f"成功: {result['successful']}/{result['total_files']}")
```

**OpenClaw 专用**
```python
from paddleocr_tool import OpenClawOCR
with OpenClawOCR() as ocr:
    text = ocr.recognize("image.png")
# 30秒后自动停止服务
```

### REST API

服务地址：`http://localhost:8001`

**健康检查**
```bash
curl http://localhost:8001/health
```

**单文件识别（支持图片和PDF）**
```bash
# 图片识别
curl -X POST -F "file=@image.png" http://localhost:8001/ocr

# PDF识别
curl -X POST -F "file=@document.pdf" http://localhost:8001/ocr
```

**批量识别**
```bash
curl -X POST \
  -F "files=@doc1.png" \
  -F "files=@doc2.pdf" \
  http://localhost:8001/ocr/batch
```

**Base64 识别**
```bash
curl -X POST -F "image_base64=$(base64 -i image.png)" http://localhost:8001/ocr/base64
```

**API 文档**
```
http://localhost:8001/docs
```

## 🧪 测试

```bash
# 运行测试
.venv_paddleocr/bin/python tests/test_ocr.py

# 查看示例
.venv_paddleocr/bin/python tests/examples.py
```

## 📖 详细文档

- [快速开始](./OPENCLAW_QUICKSTART.md) - 30秒上手指南
- [使用文档](./OPENCLAW_USAGE_OPTIMIZED.md) - 完整使用说明
- [部署报告](./docs/DEPLOYMENT_REPORT.md) - 部署详情
- [性能报告](./docs/PERFORMANCE_REPORT.md) - 性能分析
- [优化说明](./docs/SERVICE_OPTIMIZATION_SUMMARY.md) - 资源优化

## 🛠️ 技术栈

- **OCR 引擎**: PaddleOCR-VL 3.4.0
- **推理加速**: MLX-VLM 0.4.0（Apple Silicon 优化）
- **API 框架**: FastAPI
- **Python 版本**: 3.11.14
- **NumPy 版本**: 1.26.4（兼容性要求）

## 🔍 故障排除

### 服务无法启动
```bash
# 检查端口占用
lsof -i :8001
lsof -i :8111

# 查看日志
tail -f mlx_vlm_server.log
tail -f mlx_vlm_api_server.log
```

### 识别失败
```bash
# 检查服务状态
curl http://localhost:8001/health

# 测试识别
curl -X POST -F "file=@test.png" http://localhost:8001/ocr
```

### NumPy 兼容性问题
```bash
# 降级 NumPy 到 1.x
pip install "numpy<2.0" --force-reinstall
```

## 🤝 贡献

此仓库专为 OpenClaw 维护，如有问题请联系维护者。

---

**版本**: v2.0 优化版
**更新**: 2025年3月
**路径**: /Users/daodao/dsl/paddleocr-vl
**仓库**: https://gitea.dd.yp100.cn:8443/openclaw/PaddleOCR-VL-claw
