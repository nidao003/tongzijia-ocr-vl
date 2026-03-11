#!/bin/bash

# 测试主 Agent 创建子 Agent 的流程
# 用于验证 agents/README.md 中的指令是否完整可用

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   测试：主 Agent 创建子 Agent 流程${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# 源路径
SRC="/Users/daodao/dsl/PaddleOCR-VL/agents/invoice-agent"
DST="$HOME/.openclaw/workspace-invoice-agent"

# 检查源文件是否存在
echo -e "${YELLOW}📋 步骤 0：验证源文件${NC}"
if [ ! -d "$SRC" ]; then
    echo -e "${RED}❌ 源目录不存在: $SRC${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 源目录存在${NC}"

required_files=(
    "$SRC/SOUL.md"
    "$SRC/config.json"
    "$SRC/skills/invoice-processor/SKILL.md"
    "$SRC/learning/init_learning_system.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ 缺少文件: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ 所有必需文件存在${NC}"
echo ""

# 执行 README.md 中的创建步骤
echo -e "${YELLOW}📋 步骤 1：创建工作空间${NC}"
mkdir -p "$DST"/{skills/invoice-processor/learning,memory,logs}
echo -e "${GREEN}✅ 工作空间已创建: $DST${NC}"
echo ""

echo -e "${YELLOW}📋 步骤 2：复制核心文件${NC}"
cp "$SRC/SOUL.md" "$DST/"
cp "$SRC/config.json" "$DST/"
cp "$SRC/skills/invoice-processor/SKILL.md" "$DST/skills/invoice-processor/"
echo -e "${GREEN}✅ 核心文件已复制${NC}"
echo ""

echo -e "${YELLOW}📋 步骤 3：初始化学习系统${NC}"
if ! python3 "$SRC/learning/init_learning_system.py"; then
    echo -e "${RED}❌ 学习系统初始化失败${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 学习系统已初始化${NC}"
echo ""

echo -e "${YELLOW}📋 步骤 4：创建技能链接${NC}"
mkdir -p "$DST/skills/paddleocr-vl"
cat > "$DST/skills/paddleocr-vl/SKILL.md" << 'EOF'
---
name: paddleocr-vl
external: true
source: /Users/daodao/dsl/PaddleOCR-VL/openclaw_config.json
---
# PaddleOCR-VL OCR 服务
EOF
echo -e "${GREEN}✅ 技能链接已创建${NC}"
echo ""

echo -e "${YELLOW}📋 步骤 5：注册 Agent${NC}"
mkdir -p ~/.openclaw/agents
cat > ~/.openclaw/agents/invoice-agent.json << EOF
{
  "id": "invoice-agent",
  "name": "发票处理专员",
  "workspace": "$DST",
  "skills": ["paddleocr-vl", "invoice-processor"],
  "auto_learning": true,
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
echo -e "${GREEN}✅ Agent 已注册${NC}"
echo ""

# 验证
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   验证创建结果${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

echo -e "${YELLOW}📊 验证 1：文件结构${NC}"
ls -l "$DST"
echo ""

echo -e "${YELLOW}📊 验证 2：学习数据${NC}"
if command -v jq &> /dev/null; then
    total_types=$(jq '.total_types' "$DST/memory/known_invoices.json")
    echo -e "${GREEN}✅ 已支持发票类型: $total_types 种${NC}"
else
    echo -e "${YELLOW}⚠️  jq 未安装，跳过 JSON 验证${NC}"
fi
echo ""

echo -e "${YELLOW}📊 验证 3：技能链接${NC}"
ls -l "$DST/skills/"
echo ""

echo -e "${YELLOW}📊 验证 4：Agent 注册${NC}"
if [ -f ~/.openclaw/agents/invoice-agent.json ]; then
    echo -e "${GREEN}✅ Agent 已注册${NC}"
    cat ~/.openclaw/agents/invoice-agent.json | jq .
else
    echo -e "${RED}❌ Agent 注册文件不存在${NC}"
fi
echo ""

# 完成
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   ✅ 创建流程测试通过！${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}📝 测试摘要：${NC}"
echo -e "   工作空间: ${DST}"
echo -e "   SOUL 文件: $(ls -l "$DST/SOUL.md" | awk '{print $5}') 字节"
echo -e "   配置文件: $(ls -l "$DST/config.json" | awk '{print $5}') 字节"
echo -e "   技能文件: $(ls "$DST/skills/"*/*.md 2>/dev/null | wc -l | tr -d ' ') 个"
echo -e "   学习数据: $(ls "$DST/memory/"*.json 2>/dev/null | wc -l | tr -d ' ') 个"
echo ""
echo -e "${BLUE}🚀 下一步：${NC}"
echo -e "   1. 启动 PaddleOCR-VL 服务"
echo -e "   2. 主 Agent 可以开始调用 invoice-agent"
echo -e "   3. 处理发票时会自动学习和优化"
echo ""
