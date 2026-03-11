#!/bin/bash

# 发票处理 Agent 快速安装脚本
# 用途：将 invoice-agent 配置复制到 OpenClaw 工作空间

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/Users/daodao/dsl/PaddleOCR-VL"
AGENT_DIR="${PROJECT_DIR}/agents/invoice-agent"
OPENCLAW_DIR="${HOME}/.openclaw"
WORKSPACE_DIR="${OPENCLAW_DIR}/workspace-invoice-agent"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   发票处理 Agent 安装脚本${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 检查 OpenClaw 目录
if [ ! -d "$OPENCLAW_DIR" ]; then
    echo -e "${YELLOW}⚠️  OpenClaw 目录不存在: $OPENCLAW_DIR${NC}"
    echo -e "${YELLOW}   请确保 OpenClaw 已正确安装${NC}"
    exit 1
fi

# 创建工作空间
echo -e "${GREEN}📁 创建工作空间...${NC}"
mkdir -p "$WORKSPACE_DIR/skills/invoice-processor"
mkdir -p "$WORKSPACE_DIR/logs"
mkdir -p "$WORKSPACE_DIR/output"

# 复制 SOUL.md
echo -e "${GREEN}📄 复制 SOUL.md...${NC}"
cp "$AGENT_DIR/SOUL.md" "$WORKSPACE_DIR/"

# 复制技能文件
echo -e "${GREEN}📄 复制 invoice-processor 技能...${NC}"
cp "$AGENT_DIR/skills/invoice-processor/SKILL.md" \
   "$WORKSPACE_DIR/skills/invoice-processor/"

# 复制配置文件
echo -e "${GREEN}📄 复制配置文件...${NC}"
cp "$AGENT_DIR/config.json" "$WORKSPACE_DIR/"

# 创建符号链接指向 PaddleOCR-VL 配置
echo -e "${GREEN}🔗 创建 PaddleOCR-VL 技能链接...${NC}"
mkdir -p "$WORKSPACE_DIR/skills/paddleocr-vl"
cat > "$WORKSPACE_DIR/skills/paddleocr-vl/SKILL.md" << 'EOF'
---
name: paddleocr-vl
description: PaddleOCR-VL 高性能文档识别服务
version: 1.0.0
external: true
config: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
---

# PaddleOCR-VL OCR 服务

本技能提供高精度文档文字识别能力。

## 工具

- `recognize_document(image_path)` - 识别单张图片
- `batch_recognize(image_paths)` - 批量识别多张图片
- `health_check()` - 检查服务状态

## 配置

- 服务端点: http://localhost:8001
- 支持格式: PNG, JPEG, WebP
- 识别速度: ~7 秒/张

详细配置见: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
EOF

# 创建 Agent 注册文件
echo -e "${GREEN}📝 注册 Agent...${NC}"
cat > "$OPENCLAW_DIR/agents/invoice-agent.json" << EOF
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "role": "户部·发票司",
  "version": "1.0.0",
  "soul_path": "$WORKSPACE_DIR/SOUL.md",
  "config_path": "$WORKSPACE_DIR/config.json",
  "workspace": "$WORKSPACE_DIR",
  "skills": [
    {
      "name": "paddleocr-vl",
      "path": "$WORKSPACE_DIR/skills/paddleocr-vl/SKILL.md",
      "enabled": true
    },
    {
      "name": "invoice-processor",
      "path": "$WORKSPACE_DIR/skills/invoice-processor/SKILL.md",
      "enabled": true
    }
  ],
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

# 创建输出目录
mkdir -p "$HOME/invoices_output"

# 完成信息
echo ""
echo -e "${GREEN}✅ 安装完成！${NC}"
echo ""
echo -e "${BLUE}📋 安装摘要：${NC}"
echo -e "   工作空间: ${WORKSPACE_DIR}"
echo -e "   SOUL文件: ${WORKSPACE_DIR}/SOUL.md"
echo -e "   配置文件: ${WORKSPACE_DIR}/config.json"
echo -e "   输出目录: ${HOME}/invoices_output"
echo ""
echo -e "${BLUE}🚀 下一步：${NC}"
echo -e "   1. 确保 PaddleOCR-VL 服务运行中："
echo -e "      cd ${PROJECT_DIR} && ./start_services.sh"
echo ""
echo -e "   2. 在 OpenClaw 中使用 invoice-agent"
echo ""
echo -e "${BLUE}📖 更多信息：${NC}"
echo -e "   查看 README: ${AGENT_DIR}/README.md"
echo ""
echo -e "${BLUE}================================================${NC}"
