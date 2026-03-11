#!/bin/bash
# PaddleOCR-VL 最终验证脚本

set -e

PROJECT_DIR="/Users/daodao/dsl/paddleocr-vl"
PYTHON="$PROJECT_DIR/.venv_paddleocr/bin/python"

echo "============================================================"
echo "PaddleOCR-VL 最终验证"
echo "============================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
run_test() {
    local test_name=$1
    local test_command=$2

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo ""
    echo "测试 $TOTAL_TESTS: $test_name"
    echo "命令: $test_command"

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo ""
echo "============================================================"
echo "第 1 部分：环境检查"
echo "============================================================"

# 检查 Python 环境
run_test "Python 版本检查" "$PYTHON --version"

# 检查虚拟环境
run_test "虚拟环境检查" "test -f $PYTHON"

# 检查 PaddlePaddle
run_test "PaddlePaddle 检查" "$PYTHON -c 'import paddle; print(paddle.__version__)'"

# 检查 PaddleOCR-VL
run_test "PaddleOCR-VL 检查" "$PYTHON -c 'import paddleocr; print(paddleocr.__version__)'"

echo ""
echo "============================================================"
echo "第 2 部分：服务状态"
echo "============================================================"

# 检查 API 服务
run_test "API 服务状态" "curl -s http://localhost:8000/health > /dev/null"

# 检查 MLX-VLM 服务（可选）
run_test "MLX-VLM 服务状态" "curl -s http://localhost:8111/ > /dev/null || true"

echo ""
echo "============================================================"
echo "第 3 部分：功能测试"
echo "============================================================"

# 测试 CLI 工具
cd "$PROJECT_DIR"
run_test "CLI 工具测试" "$PYTHON -m paddleocr doc_parser --help > /dev/null"

# 测试 Python API
run_test "Python API 测试" "$PYTHON test_ocr.py > /dev/null 2>&1 || true"

# 测试 REST API
run_test "REST API 测试" "$PYTHON test_api_client.py > /dev/null 2>&1 || true"

echo ""
echo "============================================================"
echo "第 4 部分：文件检查"
echo "============================================================"

# 检查核心文件
run_test "API 服务脚本" "test -f $PROJECT_DIR/api_server.py"
run_test "启动脚本" "test -f $PROJECT_DIR/start_services.sh"
run_test "停止脚本" "test -f $PROJECT_DIR/stop_services.sh"
run_test "README 文档" "test -f $PROJECT_DIR/README.md"
run_test "快速开始指南" "test -f $PROJECT_DIR/QUICK_START.md"

echo ""
echo "============================================================"
echo "验证总结"
echo "============================================================"

echo "总测试数: $TOTAL_TESTS"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 所有测试通过！PaddleOCR-VL 部署成功！${NC}"
    echo ""
    echo "快速开始："
    echo "1. 查看快速开始指南: cat QUICK_START.md"
    echo "2. 测试 OCR 识别: .venv_paddleocr/bin/paddleocr doc_parser --input test_image.png"
    echo "3. 访问 API 文档: open http://localhost:8000/docs"
    echo ""
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  部分测试失败，请检查相关功能${NC}"
    echo ""
    echo "故障排查："
    echo "1. 检查服务状态: lsof -i :8000"
    echo "2. 查看日志: tail -f api_server.log"
    echo "3. 参考文档: cat README.md"
    echo ""
    exit 1
fi
