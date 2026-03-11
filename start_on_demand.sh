#!/bin/bash
# 按需启动 PaddleOCR-VL 服务
# 仅在需要时启动，使用完成后自动停止

set -e

PROJECT_DIR="/Users/daodao/dsl/paddleocr-vl"
PYTHON="$PROJECT_DIR/.venv_paddleocr/bin/python"

echo "============================================================"
echo "PaddleOCR-VL 按需启动服务"
echo "============================================================"

# 检查虚拟环境
if [ ! -f "$PYTHON" ]; then
    echo "❌ 虚拟环境不存在"
    exit 1
fi

# 检查是否已在运行
check_running() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    fi
    return 1
}

# 启动 MLX-VLM 推理服务
start_mlx_vlm() {
    echo ""
    echo "📦 启动 MLX-VLM 推理服务..."

    if check_running 8111; then
        echo "⚠️  MLX-VLM 推理服务已在运行"
        return
    fi

    cd "$PROJECT_DIR"
    $PYTHON -m mlx_vlm.server --port 8111 > mlx_vlm_server.log 2>&1 &
    MLX_PID=$!
    echo "✅ MLX-VLM 推理服务已启动 (PID: $MLX_PID)"

    # 等待服务就绪
    echo "⏳ 等待服务就绪..."
    sleep 5

    # 验证服务
    if curl -s http://localhost:8111/ >/dev/null 2>&1; then
        echo "✅ 服务就绪"
    else
        echo "⚠️  服务可能未完全就绪"
    fi
}

# 启动 MLX-VLM API 服务
start_mlx_vlm_api() {
    echo ""
    echo "📦 启动 MLX-VLM API 服务..."

    if check_running 8001; then
        echo "⚠️  MLX-VLM API 服务已在运行"
        return
    fi

    cd "$PROJECT_DIR"
    $PYTHON mlx_vlm_api_server.py > mlx_vlm_api_server.log 2>&1 &
    API_PID=$!
    echo "✅ MLX-VLM API 服务已启动 (PID: $API_PID)"
    echo "   服务地址: http://localhost:8001"
    echo "   API 文档: http://localhost:8001/docs"

    # 等待服务就绪
    sleep 3

    # 验证服务
    if curl -s http://localhost:8001/health >/dev/null 2>&1; then
        echo "✅ 服务就绪"
    else
        echo "⚠️  服务可能未完全就绪"
    fi
}

# 自动停止函数
auto_stop() {
    local wait_time=$1
    echo ""
    echo "⏰ 服务将在 $wait_time 秒后自动停止..."
    echo "（按 Ctrl+C 取消自动停止）"

    sleep $wait_time

    echo ""
    echo "🛑 自动停止服务..."

    # 停止 API 服务
    if pkill -f mlx_vlm_api_server.py; then
        echo "✅ MLX-VLM API 服务已停止"
    fi

    # 停止推理服务
    if pkill -f mlx_vlm.server; then
        echo "✅ MLX-VLM 推理服务已停止"
    fi

    echo "✅ 所有服务已停止，资源已释放"
}

# 主函数
main() {
    local auto_stop_after=${1:-0}  # 默认不自动停止

    # 启动服务
    start_mlx_vlm
    start_mlx_vlm_api

    echo ""
    echo "============================================================"
    echo "✅ 服务启动完成"
    echo "============================================================"
    echo ""
    echo "📍 服务地址:"
    echo "   - API: http://localhost:8001"
    echo "   - 推理: http://localhost:8111"
    echo ""
    echo "📖 快速测试:"
    echo "   curl -X POST -F 'file=@test_image.png' http://localhost:8001/ocr"
    echo ""
    echo "🛑 停止服务:"
    echo "   ./stop_services.sh"
    echo "   或按 Ctrl+C（如果启用了自动停止）"
    echo ""

    # 如果设置了自动停止时间
    if [ "$auto_stop_after" -gt 0 ]; then
        auto_stop $auto_stop_after
    fi
}

# 检查参数
case "${1:-}" in
    --auto-stop=*)
        main "${1#--auto-stop=}"
        ;;
    *)
        main 0
        ;;
esac
