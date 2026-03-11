#!/bin/bash
# PaddleOCR-VL 服务停止脚本

echo "============================================================"
echo "PaddleOCR-VL 服务停止脚本"
echo "============================================================"

# 停止 API 服务
stop_api_server() {
    echo ""
    echo "🛑 停止 API 服务..."
    if pkill -f api_server.py; then
        echo "✅ API 服务已停止"
    else
        echo "⚠️  API 服务未运行"
    fi
}

# 停止 MLX-VLM API 服务
stop_mlx_vlm_api() {
    echo ""
    echo "🛑 停止 MLX-VLM API 服务..."
    if pkill -f mlx_vlm_api_server.py; then
        echo "✅ MLX-VLM API 服务已停止"
    else
        echo "⚠️  MLX-VLM API 服务未运行"
    fi
}

# 停止 MLX-VLM 服务
stop_mlx_vlm() {
    echo ""
    echo "🛑 停止 MLX-VLM 服务..."
    if pkill -f mlx_vlm.server; then
        echo "✅ MLX-VLM 服务已停止"
    else
        echo "⚠️  MLX-VLM 服务未运行"
    fi
}

# 菜单选择
echo ""
echo "请选择要停止的服务:"
echo "1) 仅停止 PaddleOCR API 服务 (端口 8000)"
echo "2) 仅停止 MLX-VLM 推理服务 (端口 8111)"
echo "3) 仅停止 MLX-VLM API 服务 (端口 8001)"
echo "4) 停止所有服务"
echo "5) 退出"
echo ""
read -p "请输入选项 [1-5]: " choice

case $choice in
    1)
        stop_api_server
        ;;
    2)
        stop_mlx_vlm
        ;;
    3)
        stop_mlx_vlm_api
        ;;
    4)
        stop_api_server
        stop_mlx_vlm
        stop_mlx_vlm_api
        ;;
    5)
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
echo "服务停止完成"
echo "============================================================"
echo ""
echo "确认服务已停止:"
echo "  lsof -i :8000"
echo "  lsof -i :8111"
echo ""
