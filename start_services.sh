#!/bin/bash
# PaddleOCR-VL 服务快速启动脚本

set -e

PROJECT_DIR="/Users/daodao/dsl/paddleocr-vl"
PYTHON="$PROJECT_DIR/.venv_paddleocr/bin/python"

echo "============================================================"
echo "PaddleOCR-VL 服务启动脚本"
echo "============================================================"

# 检查虚拟环境
if [ ! -f "$PYTHON" ]; then
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 检查端口占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用"
        return 1
    fi
    return 0
}

# 启动 MLX-VLM 服务
start_mlx_vlm() {
    echo ""
    echo "📦 启动 MLX-VLM 推理服务..."
    if check_port 8111; then
        cd "$PROJECT_DIR"
        $PYTHON -m mlx_vlm.server --port 8111 > mlx_vlm_server.log 2>&1 &
        MLX_PID=$!
        echo "✅ MLX-VLM 服务已启动 (PID: $MLX_PID)"
        echo "   日志文件: mlx_vlm_server.log"
        sleep 3
    else
        echo "⚠️  MLX-VLM 服务已在运行，跳过启动"
    fi
}

# 启动 API 服务
start_api_server() {
    echo ""
    echo "📦 启动 PaddleOCR-VL API 服务..."
    if check_port 8000; then
        cd "$PROJECT_DIR"
        $PYTHON api_server.py > api_server.log 2>&1 &
        API_PID=$!
        echo "✅ API 服务已启动 (PID: $API_PID)"
        echo "   服务地址: http://localhost:8000"
        echo "   API 文档: http://localhost:8000/docs"
        echo "   日志文件: api_server.log"
        sleep 3
    else
        echo "⚠️  API 服务已在运行，跳过启动"
    fi
}

# 启动 MLX-VLM API 服务
start_mlx_vlm_api() {
    echo ""
    echo "📦 启动 MLX-VLM API 服务..."
    if check_port 8001; then
        cd "$PROJECT_DIR"
        $PYTHON mlx_vlm_api_server.py > mlx_vlm_api_server.log 2>&1 &
        API_PID=$!
        echo "✅ MLX-VLM API 服务已启动 (PID: $API_PID)"
        echo "   服务地址: http://localhost:8001"
        echo "   API 文档: http://localhost:8001/docs"
        echo "   日志文件: mlx_vlm_api_server.log"
        sleep 3
    else
        echo "⚠️  MLX-VLM API 服务已在运行，跳过启动"
    fi
}

# 菜单选择
echo ""
echo "请选择要启动的服务:"
echo "1) 仅启动 PaddleOCR API 服务 (端口 8000)"
echo "2) 仅启动 MLX-VLM 推理服务 (端口 8111)"
echo "3) 仅启动 MLX-VLM API 服务 (端口 8001, 推荐)"
echo "4) 启动 MLX-VLM + MLX-VLM API (高性能组合)"
echo "5) 启动所有服务"
echo "6) 退出"
echo ""
read -p "请输入选项 [1-6]: " choice

case $choice in
    1)
        start_api_server
        ;;
    2)
        start_mlx_vlm
        ;;
    3)
        start_mlx_vlm_api
        ;;
    4)
        start_mlx_vlm
        start_mlx_vlm_api
        ;;
    5)
        start_mlx_vlm
        start_api_server
        start_mlx_vlm_api
        ;;
    6)
        echo "退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "服务启动完成"
echo "============================================================"
echo ""
echo "检查服务状态:"
echo "  curl http://localhost:8000/health"
echo ""
echo "查看日志:"
echo "  tail -f $PROJECT_DIR/api_server.log"
echo "  tail -f $PROJECT_DIR/mlx_vlm_server.log"
echo ""
echo "停止服务:"
echo "  pkill -f api_server.py"
echo "  pkill -f mlx_vlm.server"
echo ""
