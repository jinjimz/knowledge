#!/bin/bash
# 更新索引脚本
# 用法: update-index.sh <all|tags|categories|manifest> <路径>

set -e

ACTION="$1"
KB_PATH="$2"

if [ -z "$KB_PATH" ]; then
    echo "❌ 错误: 请指定知识库路径"
    echo "用法: update-index.sh <all|tags|categories|manifest> <路径>"
    exit 1
fi

cd "$KB_PATH"

INDEX_DIR="_index"
TODAY=$(date +%Y-%m-%d)

# 更新标签索引
update_tags() {
    echo "📝 更新标签索引..."
    
    cat > "$INDEX_DIR/tags.yaml" << EOF
# 标签索引
# 更新时间: $TODAY
tags:
EOF

    # 查找所有 markdown 文件并提取标签
    find . -name "*.md" -not -path "./_*" -not -path "./.git/*" | while read -r file; do
        # 从 frontmatter 提取标签
        if grep -q "^tags:" "$file" 2>/dev/null; then
            title=$(grep "^title:" "$file" 2>/dev/null | head -1 | sed 's/title: *"\?\([^"]*\)"\?/\1/')
            path="${file#./}"
            
            # 提取标签列表
            awk '/^tags:/,/^[a-z]/' "$file" | grep "^  - " | sed 's/^  - //' | while read -r tag; do
                echo "  $tag:" >> "$INDEX_DIR/tags.yaml"
                echo "    - path: \"$path\"" >> "$INDEX_DIR/tags.yaml"
                echo "      title: \"$title\"" >> "$INDEX_DIR/tags.yaml"
            done
        fi
    done
    
    echo "✅ 标签索引更新完成"
}

# 更新分类索引
update_categories() {
    echo "📁 更新分类索引..."
    
    cat > "$INDEX_DIR/categories.yaml" << EOF
# 分类索引
# 更新时间: $TODAY
categories:
EOF

    # 遍历顶级分类目录
    for dir in Inbox Technology Learning Work Life Ideas Resources; do
        if [ -d "$dir" ]; then
            count=$(find "$dir" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
            echo "  $dir:" >> "$INDEX_DIR/categories.yaml"
            echo "    count: $count" >> "$INDEX_DIR/categories.yaml"
            
            # 检查子目录
            for subdir in "$dir"/*/; do
                if [ -d "$subdir" ]; then
                    subname=$(basename "$subdir")
                    subcount=$(find "$subdir" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
                    echo "    $subname:" >> "$INDEX_DIR/categories.yaml"
                    echo "      count: $subcount" >> "$INDEX_DIR/categories.yaml"
                fi
            done
        fi
    done
    
    echo "✅ 分类索引更新完成"
}

# 更新笔记清单
update_manifest() {
    echo "📋 更新笔记清单..."
    
    cat > "$INDEX_DIR/notes-manifest.yaml" << EOF
# 笔记清单
# 更新时间: $TODAY
notes:
EOF

    id=1
    find . -name "*.md" -not -path "./_*" -not -path "./.git/*" | sort | while read -r file; do
        path="${file#./}"
        
        # 提取 frontmatter 信息
        title=$(grep "^title:" "$file" 2>/dev/null | head -1 | sed 's/title: *"\?\([^"]*\)"\?/\1/' || basename "$file" .md)
        category=$(grep "^category:" "$file" 2>/dev/null | head -1 | sed 's/category: *"\?\([^"]*\)"\?/\1/' || dirname "$path")
        created=$(grep "^created:" "$file" 2>/dev/null | head -1 | sed 's/created: *"\?\([^"]*\)"\?/\1/' || echo "$TODAY")
        updated=$(grep "^updated:" "$file" 2>/dev/null | head -1 | sed 's/updated: *"\?\([^"]*\)"\?/\1/' || echo "$TODAY")
        summary=$(grep "^ai_summary:" "$file" 2>/dev/null | head -1 | sed 's/ai_summary: *"\?\([^"]*\)"\?/\1/' || echo "")
        
        cat >> "$INDEX_DIR/notes-manifest.yaml" << EOF
  - id: "$id"
    title: "$title"
    path: "$path"
    category: "$category"
    created: "$created"
    updated: "$updated"
    ai_summary: "$summary"
EOF
        
        id=$((id + 1))
    done
    
    echo "✅ 笔记清单更新完成"
}

case "$ACTION" in
    all)
        update_tags
        update_categories
        update_manifest
        echo "✅ 所有索引更新完成"
        ;;
    tags)
        update_tags
        ;;
    categories)
        update_categories
        ;;
    manifest)
        update_manifest
        ;;
    *)
        echo "用法: update-index.sh <all|tags|categories|manifest> <路径>"
        echo ""
        echo "命令:"
        echo "  all         - 重建所有索引"
        echo "  tags        - 仅更新标签索引"
        echo "  categories  - 仅更新分类索引"
        echo "  manifest    - 仅更新笔记清单"
        exit 1
        ;;
esac
