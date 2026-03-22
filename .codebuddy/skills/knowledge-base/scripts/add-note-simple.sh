#!/bin/bash

# 知识库笔记添加脚本 (Bash简化版本)
# 用法: ./add-note-simple.sh "标题" "摘要" "标签1,标签2" "分类" [源文件路径]

set -e

# 配置 - 自动探测知识库路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 探测知识库路径（优先级从高到低）
find_kb_root() {
    # 1. 环境变量
    if [ -n "$KB_DATA_PATH" ] && [ -f "$KB_DATA_PATH/.kb-config.yaml" ]; then
        echo "$KB_DATA_PATH"
        return 0
    fi
    
    # 2. 从脚本位置向上探测（最多6级）
    local probe="$SCRIPT_DIR"
    for i in $(seq 1 6); do
        probe="$(dirname "$probe")"
        if [ -f "$probe/data/.kb-config.yaml" ]; then
            echo "$probe/data"
            return 0
        fi
    done
    
    # 3. 家目录默认位置
    if [ -f "$HOME/knowledge/data/.kb-config.yaml" ]; then
        echo "$HOME/knowledge/data"
        return 0
    fi
    
    return 1
}

KB_ROOT="$(find_kb_root)"
if [ -z "$KB_ROOT" ]; then
    echo "❌ 找不到知识库数据目录"
    echo "提示: 请确保知识库已初始化（包含 .kb-config.yaml 文件）"
    echo "     或设置环境变量: export KB_DATA_PATH=/path/to/knowledge/data"
    exit 1
fi

INDEX_DIR="$KB_ROOT/_index"
TEMPLATE_FILE="$KB_ROOT/_templates/default.md"

echo "📍 知识库路径: $KB_ROOT"

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
    
    COMMIT_MSG="📝 新增笔记: $TITLE

- 分类: $CATEGORY
- 标签: $TAGS_STR"
    
    if git commit -m "$COMMIT_MSG" > /dev/null 2>&1; then
        echo "✓ Git提交成功"
        
        # 5. 检查是否需要自动推送
        # 读取配置文件获取push_threshold
        get_config_value() {
            local key="$1"
            grep "$key:" "$KB_ROOT/.kb-config.yaml" | head -1 | awk -F': ' '{print $2}' | tr -d ' "'
        }
        
        PUSH_THRESHOLD=$(get_config_value "push_threshold")
        AUTO_PULL=$(get_config_value "auto_pull_before_push")
        
        PUSH_THRESHOLD=${PUSH_THRESHOLD:-10}
        AUTO_PULL=${AUTO_PULL:-true}
        
        # 获取未推送的提交数
        UNPUSHED_COUNT=$(git log @{u}.. --oneline 2>/dev/null | wc -l | tr -d ' ')
        
        echo "📊 当前进度: $UNPUSHED_COUNT 个未推送提交 (阈值: $PUSH_THRESHOLD)"
        
        if [ "$UNPUSHED_COUNT" -ge "$PUSH_THRESHOLD" ]; then
            echo "📤 达到推送阈值，开始推送到远程..."
            
            # 先拉取（如果配置了auto_pull_before_push）
            if [ "$AUTO_PULL" = "true" ]; then
                if git pull --rebase > /dev/null 2>&1; then
                    echo "✓ 远程更新已拉取"
                else
                    echo "⚠️ 拉取远程更新失败（可能是新仓库或无远程）"
                fi
            fi
            
            # 推送
            if git push > /dev/null 2>&1; then
                echo "✓ 推送成功!"
            else
                echo "⚠️ 推送失败"
                echo "   提示: 可以稍后手动运行 'git push' 推送"
            fi
        fi
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
