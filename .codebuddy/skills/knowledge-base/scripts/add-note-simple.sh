#!/bin/bash

# 知识库笔记添加脚本 (Bash简化版本)
# 用法: ./add-note-simple.sh "标题" "摘要" "标签1,标签2" "分类" [源文件路径]

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KB_ROOT="$(cd "$SCRIPT_DIR/../../../knowledge" && pwd)"
INDEX_DIR="$KB_ROOT/_index"
TEMPLATE_FILE="$KB_ROOT/_templates/default.md"

# 参数检查
if [ $# -lt 4 ]; then
    echo "用法: $0 <标题> <摘要> <标签> <分类> [源文件路径]"
    echo "示例: $0 '标题' '摘要' '标签1,标签2' 'Technology/AI' '/path/to/source.md'"
    exit 1
fi

TITLE="$1"
AI_SUMMARY="$2"
TAGS_STR="$3"
CATEGORY="$4"
SOURCE_FILE="${5:-}"

# 工具函数
get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%S"
}

sanitize_filename() {
    echo "$1" | sed 's/[\/\\:*?"<>|]/_/g'
}

# 主逻辑
echo "📝 开始添加笔记..."

# 1. 确定目标路径
CATEGORY_PATH="${CATEGORY//\//$'/'}"
TARGET_DIR="$KB_ROOT/$CATEGORY_PATH"
FILENAME="$(sanitize_filename "$TITLE").md"
TARGET_FILE="$TARGET_DIR/$FILENAME"
RELATIVE_PATH="${TARGET_FILE#$KB_ROOT/}"

echo "📂 目标路径: $RELATIVE_PATH"

# 2. 创建目录
mkdir -p "$TARGET_DIR"

# 3. 处理笔记内容
TIMESTAMP=$(get_timestamp)

# 转换标签为数组格式和行内格式
IFS=',' read -ra TAGS_ARRAY <<< "$TAGS_STR"
TAG_LINE=""
TAG_YAML="["
for i in "${!TAGS_ARRAY[@]}"; do
    tag="${TAGS_ARRAY[$i]}"
    tag=$(echo "$tag" | xargs) # trim
    TAG_LINE="$TAG_LINE #$tag"
    if [ $i -eq 0 ]; then
        TAG_YAML="${TAG_YAML}\"$tag\""
    else
        TAG_YAML="$TAG_YAML, \"$tag\""
    fi
done
TAG_YAML="${TAG_YAML}]"
TAG_LINE=$(echo "$TAG_LINE" | xargs)

if [ -n "$SOURCE_FILE" ] && [ -f "$SOURCE_FILE" ]; then
    echo "📄 复制源文件: $SOURCE_FILE"
    
    # 检查源文件是否有frontmatter
    if head -n 1 "$SOURCE_FILE" | grep -q "^---$"; then
        # 有frontmatter，提取内容部分
        CONTENT=$(sed '1,/^---$/d' "$SOURCE_FILE" | sed '1,/^---$/d')
        
        # 创建新的frontmatter
        cat > "$TARGET_FILE" <<EOF
---
title: "$TITLE"
created: "$TIMESTAMP"
updated: "$TIMESTAMP"
tags: $TAG_YAML
category: "$CATEGORY"
ai_summary: "$AI_SUMMARY"
---

$CONTENT
EOF
    else
        # 无frontmatter，直接添加
        cat > "$TARGET_FILE" <<EOF
---
title: "$TITLE"
created: "$TIMESTAMP"
updated: "$TIMESTAMP"
tags: $TAG_YAML
category: "$CATEGORY"
ai_summary: "$AI_SUMMARY"
---

# $TITLE

$TAG_LINE

$(cat "$SOURCE_FILE")
EOF
    fi
else
    echo "📝 使用模板创建笔记"
    
    # 使用模板或默认内容
    cat > "$TARGET_FILE" <<EOF
---
title: "$TITLE"
created: "$TIMESTAMP"
updated: "$TIMESTAMP"
tags: $TAG_YAML
category: "$CATEGORY"
ai_summary: "$AI_SUMMARY"
---

# $TITLE

$TAG_LINE

> $AI_SUMMARY

## 内容

TODO: 添加笔记内容
EOF
fi

echo "✓ 笔记已创建: $FILENAME"

# 4. Git提交
echo "📦 提交到Git..."
cd "$KB_ROOT"

if git rev-parse --git-dir > /dev/null 2>&1; then
    git add "$RELATIVE_PATH" _index/ 2>/dev/null || true
    
    COMMIT_MSG="添加笔记: $TITLE

- 分类: $CATEGORY
- 标签: $TAGS_STR"
    
    if git commit -m "$COMMIT_MSG" > /dev/null 2>&1; then
        echo "✓ Git提交成功"
    else
        echo "⚠ Git提交跳过（可能没有变更）"
    fi
else
    echo "⚠ 不是Git仓库，跳过提交"
fi

echo ""
echo "✅ 笔记添加完成!"
echo "📍 位置: $RELATIVE_PATH"
echo ""
echo "⚠️  注意: 索引文件需要手动更新或使用Python脚本自动更新"
