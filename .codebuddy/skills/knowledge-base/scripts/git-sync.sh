#!/bin/bash
# Git 同步脚本
# 用法: 
#   git-sync.sh commit <路径> <消息>  - 本地提交
#   git-sync.sh push <路径>           - 远程推送
#   git-sync.sh sync <路径>           - 强制同步（拉取+推送）

set -e

ACTION="$1"
KB_PATH="$2"
MESSAGE="$3"

if [ -z "$KB_PATH" ]; then
    echo "❌ 错误: 请指定知识库路径"
    echo "用法: git-sync.sh <commit|push|sync> <路径> [消息]"
    exit 1
fi

cd "$KB_PATH"

# 读取配置
CONFIG_FILE=".kb-config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 错误: 配置文件不存在: $CONFIG_FILE"
    exit 1
fi

# 简单解析 YAML 获取配置值
get_config() {
    grep "$1:" "$CONFIG_FILE" | head -1 | awk -F': ' '{print $2}' | tr -d '"' | tr -d "'"
}

PUSH_THRESHOLD=$(get_config "push_threshold")
BRANCH=$(get_config "default_branch")

PUSH_THRESHOLD=${PUSH_THRESHOLD:-10}
BRANCH=${BRANCH:-main}

# 获取本地未推送的提交数
get_unpushed_count() {
    git log @{u}.. --oneline 2>/dev/null | wc -l | tr -d ' '
}

case "$ACTION" in
    commit)
        if [ -z "$MESSAGE" ]; then
            echo "❌ 错误: 请提供提交消息"
            exit 1
        fi
        
        git add .
        git commit -m "$MESSAGE" || echo "没有需要提交的更改"
        
        # 获取未推送的提交数
        UNPUSHED_COUNT=$(get_unpushed_count)
        
        echo "✅ 本地提交完成 ($UNPUSHED_COUNT 个未推送提交,阈值: $PUSH_THRESHOLD)"
        
        # 检查是否需要推送
        if [ $UNPUSHED_COUNT -ge $PUSH_THRESHOLD ]; then
            echo "📤 达到推送阈值，开始推送..."
            "$0" push "$KB_PATH"
        fi
        ;;
        
    push)
        echo "📤 推送到远程..."
        
        # 先拉取
        git pull --rebase origin "$BRANCH" 2>/dev/null || echo "⚠️ 无法拉取远程（可能是新仓库）"
        
        # 推送
        git push -u origin "$BRANCH" 2>/dev/null || {
            echo "⚠️ 推送失败，请检查远程仓库配置"
            exit 1
        }
        
        echo "✅ 推送完成"
        ;;
        
    sync)
        echo "🔄 强制同步..."
        
        # 提交本地更改
        git add .
        git commit -m "📝 同步前自动提交" 2>/dev/null || true
        
        # 拉取远程
        git pull --rebase origin "$BRANCH" 2>/dev/null || echo "⚠️ 无法拉取远程"
        
        # 推送
        git push -u origin "$BRANCH" 2>/dev/null || echo "⚠️ 推送失败"
        
        echo "✅ 同步完成"
        ;;
        
    *)
        echo "用法: git-sync.sh <commit|push|sync> <路径> [消息]"
        echo ""
        echo "命令:"
        echo "  commit <路径> <消息>  - 本地提交"
        echo "  push <路径>           - 远程推送"
        echo "  sync <路径>           - 强制同步（拉取+推送）"
        exit 1
        ;;
esac
