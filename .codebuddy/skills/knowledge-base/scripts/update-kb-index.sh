#!/bin/bash
# 知识库索引更新脚本 - 便捷入口

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/update-index.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示使用帮助
show_help() {
    echo -e "${BLUE}知识库索引更新工具${NC}"
    echo ""
    echo "用法:"
    echo "  $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -i, --incremental    增量更新 (推荐,仅处理变更的笔记)"
    echo "  -f, --full           全量更新 (重建所有索引)"
    echo "  -s, --status         查看索引状态"
    echo "  -h, --help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -i                # 快速增量更新"
    echo "  $0 --full            # 完整重建索引"
    echo "  $0 --status          # 查看当前状态"
    echo ""
    echo "说明:"
    echo "  - 增量更新基于 Git 提交历史,速度快"
    echo "  - 全量更新扫描所有笔记,确保索引完整"
    echo "  - 建议每次记完笔记后运行增量更新"
}

# 检查 Python 脚本是否存在
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}❌ 错误: 找不到 update-index.py 脚本${NC}"
    echo "路径: $PYTHON_SCRIPT"
    exit 1
fi

# 解析参数
MODE=""
if [ $# -eq 0 ]; then
    # 默认执行增量更新
    MODE="--incremental"
else
    case "$1" in
        -i|--incremental)
            MODE="--incremental"
            ;;
        -f|--full)
            MODE="--full"
            ;;
        -s|--status)
            MODE="--status"
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 未知选项: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
fi

# 执行 Python 脚本
echo -e "${BLUE}🚀 执行索引更新...${NC}"
echo ""

python3 "$PYTHON_SCRIPT" "$MODE"
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 索引更新完成!${NC}"
else
    echo -e "${RED}❌ 索引更新失败 (退出码: $EXIT_CODE)${NC}"
fi

exit $EXIT_CODE
