#!/bin/bash
# 初始化知识库
# 用法: init-kb.sh [路径] [远程地址]
# 
# 参数说明：
#   - [路径] 可选，默认使用 $KB_DATA_PATH 环境变量或 ~/knowledge/data
#   - [远程地址] 可选，默认使用 $KB_REMOTE_URL 环境变量
# 
# 示例：
#   - init-kb.sh                                    # 使用默认路径
#   - init-kb.sh ~/my-notes/data                    # 指定路径
#   - init-kb.sh ~/my-notes/data https://github.com/user/repo  # 指定路径和远程地址

set -e

# 优先使用环境变量，然后是命令行参数，最后是默认值
KB_PATH="${1:-${KB_DATA_PATH:-$HOME/knowledge/data}}"
REMOTE_URL="${2:-${KB_REMOTE_URL:-}}"

echo "📚 初始化知识库: $KB_PATH"

# 创建目录结构
mkdir -p "$KB_PATH"/{_index,_templates,_attachments,Inbox}
mkdir -p "$KB_PATH"/Technology/{Programming,DevOps,AI,Database}
mkdir -p "$KB_PATH"/Learning/{Courses,Books,Tutorials}
mkdir -p "$KB_PATH"/{Work,Life,Ideas}
mkdir -p "$KB_PATH"/Resources/Tools
mkdir -p "$KB_PATH"/scripts

# 创建配置文件
if [ ! -f "$KB_PATH/.kb-config.yaml" ]; then
cat > "$KB_PATH/.kb-config.yaml" << EOF
# 知识库基本信息
knowledge_base:
  name: "我的知识库"
  version: "1.0.0"
  created_at: "$(date +%Y-%m-%d)"

# Skill 配置
skill:
  search_paths:
    - "."
    - "~/knowledge"
  language: "zh-CN"

# Git 同步配置
git:
  remote_url: "$REMOTE_URL"
  default_branch: "main"
  push_threshold: 10
  auto_pull_before_push: true
  conflict_resolution: "manual"
  commit_message_template: "📝 {action}: {title}"

# 分类配置
categories:
  default: "Inbox"
  aliases:
    技术: "Technology"
    编程: "Technology/Programming"
    工具: "Resources/Tools"
    学习: "Learning"
    读书: "Learning/Books"
    工作: "Work"
    生活: "Life"
    想法: "Ideas"

# 附件配置
attachments:
  large_file_threshold: 1048576
  date_folder_format: "YYYY-MM-DD"
EOF
fi

# 创建索引文件
if [ ! -f "$KB_PATH/_index/tags.yaml" ]; then
cat > "$KB_PATH/_index/tags.yaml" << EOF
# 标签索引
# 更新时间: $(date +%Y-%m-%d)
tags: {}
EOF
fi

if [ ! -f "$KB_PATH/_index/categories.yaml" ]; then
cat > "$KB_PATH/_index/categories.yaml" << EOF
# 分类索引
# 更新时间: $(date +%Y-%m-%d)
categories:
  Inbox: { count: 0 }
  Technology:
    Programming: { count: 0 }
    DevOps: { count: 0 }
    AI: { count: 0 }
    Database: { count: 0 }
  Learning:
    Courses: { count: 0 }
    Books: { count: 0 }
    Tutorials: { count: 0 }
  Work: { count: 0 }
  Life: { count: 0 }
  Ideas: { count: 0 }
  Resources:
    Tools: { count: 0 }
EOF
fi

if [ ! -f "$KB_PATH/_index/notes-manifest.yaml" ]; then
cat > "$KB_PATH/_index/notes-manifest.yaml" << EOF
# 笔记清单
# 更新时间: $(date +%Y-%m-%d)
notes: []
EOF
fi

# 创建默认模板
if [ ! -f "$KB_PATH/_templates/default.md" ]; then
cat > "$KB_PATH/_templates/default.md" << 'EOF'
---
title: "{{title}}"
created: "{{created}}"
updated: "{{updated}}"
tags: {{tags}}
category: "{{category}}"
ai_summary: "{{ai_summary}}"
---

# {{title}}

{{content}}
EOF
fi

# 创建 .gitignore
if [ ! -f "$KB_PATH/.gitignore" ]; then
cat > "$KB_PATH/.gitignore" << 'EOF'
.DS_Store
*.swp
*.swo
*~
.obsidian/workspace.json
.obsidian/workspace-mobile.json
EOF
fi

# 初始化 Git（在父目录，即整个项目根目录）
PARENT_DIR=$(dirname "$KB_PATH")
cd "$PARENT_DIR"
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "📚 初始化知识库"
    if [ -n "$REMOTE_URL" ]; then
        git remote add origin "$REMOTE_URL" 2>/dev/null || true
    fi
fi

echo "✅ 知识库初始化完成: $KB_PATH"
echo "💡 Git 仓库位于: $PARENT_DIR"
