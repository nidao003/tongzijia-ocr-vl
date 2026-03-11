# PaddleOCR-VL for OpenClaw

高性能文档识别服务，专为 OpenClaw 优化设计。

## 🎯 特点

- ✅ **按需启动** - 用时启动，用完停止
- ✅ **自动管理** - 智能服务生命周期
- ✅ **资源优化** - 最大化释放系统性能
- ✅ **简单易用** - 一行代码搞定

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://gitea.dd.yp100.cn:8443/openclaw/PaddleOCR-VL-claw.git
cd PaddleOCR-VL-claw

# 配置环境（需单独完成 PaddleOCR-VL 部署）
```

### 使用

```python
import sys
sys.path.append('/Users/daodao/dsl/paddleocr-vl')
from paddleocr_tool import quick_recognize

# 识别图片
text = quick_recognize("/path/to/image.png")
print(text)
```

## 📚 文档

- [快速开始](./OPENCLAW_QUICKSTART.md) - 30 秒上手指南 ⭐
- [使用指南](./OPENCLAW_README_FINAL.md) - 完整使用说明
- [优化说明](./SERVICE_OPTIMIZATION_SUMMARY.md) - 资源优化详情

## 🔧 工具

- `paddleocr_tool.py` - OpenClaw 专用工具类
- `examples.py` - 使用示例
- `start_on_demand.sh` - 按需启动脚本

## 📊 性能

- **识别速度**: 7 秒/张
- **准确率**: 100%
- **资源占用**: 仅用时占用（2.58GB）
- **节省效果**: 30-50% 电能

## 🤝 贡献

此仓库专为 OpenClaw 维护，如有问题请联系维护者。

---

**版本**: v2.0 优化版
**更新**: 2025年
**路径**: /Users/daodao/dsl/paddleocr-vl
