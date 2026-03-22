# 个人知识库 (Personal Knowledge Base)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Knowledge Base](https://img.shields.io/badge/Notes-7-blue.svg)](#)
[![Categories](https://img.shields.io/badge/Categories-9-green.svg)](#)

一个基于 Git 的个人知识管理系统，支持多级分类、智能标签、增量索引、自动同步，完全兼容 Obsidian。

## ✨ 核心特性

- 📂 **多级分类体系** - 灵活的分类层级，最多支持 3 层嵌套
- 🏷️ **智能标签管理** - 自动维护标签索引，快速检索相关笔记
- 🔄 **Git 版本控制** - 所有笔记自动版本管理，支持历史回溯
- 📊 **增量索引更新** - 基于 Git diff 的增量更新，高效处理大量笔记
- 🤖 **AI 辅助创建** - 通过 CodeBuddy Skill 智能生成笔记和摘要
- 💎 **Obsidian 兼容** - 完全兼容 Obsidian，支持双向链接和图谱视图
- 🔒 **本地优先** - 数据完全存储在本地，可选同步到 GitHub
- 🚀 **自动化推送** - 达到阈值自动推送到远程仓库

## 📁 目录结构

```
knowledge/                          # 项目根目录 (Git 仓库)
├── README.md                       # 本文档
├── .gitignore                      # Git 忽略规则
├── .codebuddy/                     # CodeBuddy 配置目录
│   └── skills/knowledge-base/      # 知识库管理 Skill
│       ├── SKILL.md               # Skill 定义文件
│       ├── README.md              # Skill 使用文档
│       └── scripts/               # 自动化脚本
│           ├── add-note.py        # 添加笔记 (推荐)
│           ├── add-note.js        # Node.js 版本
│           ├── add-note-simple.sh # Bash 简化版
│           ├── update-index.py    # 更新索引 (支持增量)
│           ├── init-kb.sh         # 初始化知识库
│           └── git-sync.sh        # Git 同步助手
├── data/                          # 📁 知识库数据目录 (核心)
│   ├── .kb-config.yaml           # 知识库配置文件
│   ├── _index/                   # 索引文件目录
│   │   ├── .index-state          # 索引状态跟踪 (记录 commit ID)
│   │   ├── categories.yaml       # 分类索引
│   │   ├── tags.yaml            # 标签索引
│   │   └── notes-manifest.yaml  # 笔记清单
│   ├── _templates/               # 笔记模板
│   │   └── default.md           # 默认模板
│   ├── _attachments/            # 附件存储
│   │   └── YYYY-MM-DD/         # 按日期组织
│   ├── Technology/              # 技术分类
│   │   ├── AI/                 # AI 相关
│   │   ├── Programming/        # 编程相关
│   │   └── DevOps/            # 运维相关
│   ├── Learning/               # 学习笔记
│   ├── Resources/              # 资源收藏
│   │   └── Tools/             # 工具集合
│   ├── Work/                   # 工作相关
│   ├── Life/                   # 生活记录
│   ├── Ideas/                  # 想法创意
│   └── Inbox/                  # 临时收件箱
└── tmp/                        # 临时文件 (项目产出物)
```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/jinjimz/knowledge.git
cd knowledge
```

### 2. 安装依赖

```bash
# Python 依赖 (推荐)
pip3 install pyyaml

# Node.js 依赖 (可选)
npm install js-yaml
```

### 3. 初始化知识库

如果是第一次使用，运行初始化脚本：

```bash
bash .codebuddy/skills/knowledge-base/scripts/init-kb.sh
```

### 4. 配置 Git 远程仓库

```bash
cd data
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd ..
```

### 5. 开始使用

#### 方法 A: 通过 AI 助手 (推荐) 🤖

在 CodeBuddy 中直接说：

```
记笔记: 我今天学习了 Python 装饰器，路径是 /path/to/decorator-notes.md
```

AI 会自动：
1. 读取源文件内容
2. 生成智能摘要
3. 推荐合适的标签和分类
4. 创建笔记并提交到 Git
5. 根据配置决定是否更新索引

#### 方法 B: 使用脚本

```bash
# 从现有文件创建笔记
python3 .codebuddy/skills/knowledge-base/scripts/add-note.py \
  "Python装饰器学习笔记" \
  "学习了Python装饰器的工作原理、使用场景和最佳实践" \
  "Python,编程,装饰器,学习" \
  "Learning/Python" \
  "/path/to/source.md"

# 创建新笔记 (不提供源文件)
python3 .codebuddy/skills/knowledge-base/scripts/add-note.py \
  "今日想法" \
  "关于项目架构的一些思考" \
  "想法,架构" \
  "Ideas"
```

#### 方法 C: 手动更新索引 (可选)

当配置文件中 `index.auto_update_on_add_note` 设为 `false` 时，需要手动更新索引：

```bash
# 增量更新索引 (推荐 - 只处理变更的文件)
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --incremental

# 全量更新索引 (首次使用或索引损坏时)
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --full

# 查看索引状态
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --status
```

## ⚙️ 配置说明

### 知识库配置 (`data/.kb-config.yaml`)

```yaml
# Git 同步配置
git:
  push_threshold: 1              # 未推送提交达到此数量时自动推送
  auto_pull_before_push: true    # 推送前自动拉取

# 索引更新配置
index:
  auto_update_on_add_note: false # 记笔记时是否自动更新索引
  incremental_update: true       # 支持增量更新

# 分类别名 (中文 -> 英文映射)
categories:
  aliases:
    技术: "Technology"
    工具: "Resources/Tools"
    学习: "Learning"
```

### 索引状态追踪 (`data/_index/.index-state`)

此文件自动维护，记录最后一次索引更新对应的 Git commit ID，用于支持增量更新：

```yaml
last_index_update:
  commit_id: "abc123def456..."    # Git commit SHA
  timestamp: "2026-03-22T12:30:00"
  notes_count: 7
  tags_count: 24
  categories_count: 9
```

**工作原理**：
1. 增量更新时，读取 `commit_id`
2. 通过 `git diff` 找出自上次更新以来的变更文件
3. 只对变更的笔记进行索引更新
4. 更新完成后，将当前 commit ID 写入文件

## 📝 笔记格式

### Frontmatter (YAML 元数据)

```yaml
---
title: "笔记标题"
created: "2026-03-22T10:30:00"
updated: "2026-03-22T10:30:00"
tags:
  - 标签1
  - 标签2
  - 标签3
category: "Technology/AI"
ai_summary: "这是 AI 生成的摘要，简要描述笔记内容..."
---
```

### 正文格式

```markdown
# 笔记标题

#标签1 #标签2 #标签3

> AI 摘要内容

## 核心内容

笔记正文...

## 相关链接

- [[相关笔记1]]
- [[相关笔记2]]
```

## 🔍 索引系统

### 三个核心索引文件

1. **categories.yaml** - 分类索引
   - 记录分类层级结构
   - 维护每个分类的笔记数量

2. **tags.yaml** - 标签索引
   - 记录每个标签关联的所有笔记
   - 支持快速按标签检索

3. **notes-manifest.yaml** - 笔记清单
   - 所有笔记的完整元数据
   - 包含标题、路径、标签、分类、摘要等

### 索引更新策略

#### 自动更新模式 (默认关闭)

设置 `index.auto_update_on_add_note: true` 时，每次添加笔记都会立即更新索引。

**优点**: 索引始终保持最新  
**缺点**: 频繁添加笔记时会产生大量提交

#### 手动更新模式 (推荐)

设置 `index.auto_update_on_add_note: false` 时，只在需要时手动更新索引。

**优点**: 
- 减少 Git 提交噪音
- 批量处理更高效
- 可选择增量或全量更新

**使用场景**:
```bash
# 场景1: 一次性添加了 10 篇笔记，统一更新索引
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --incremental

# 场景2: 索引文件损坏，需要重建
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --full

# 场景3: 检查索引状态和统计信息
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --status
```

### 增量更新原理

```bash
# 1. 读取上次更新的 commit ID
LAST_COMMIT=$(cat data/_index/.index-state | grep commit_id)

# 2. 找出变更的笔记文件
git diff $LAST_COMMIT..HEAD --name-only -- "*.md" | grep -v "_index/"

# 3. 只对变更的文件更新索引
# - 新增文件: 添加到索引
# - 修改文件: 更新索引条目
# - 删除文件: 从索引中移除

# 4. 更新 .index-state 记录当前 commit ID
```

## 🔄 Git 工作流

### 自动提交

每次添加笔记时，脚本会自动：

```bash
cd data
git add [new-note].md
git commit -m "📝 新增笔记: 笔记标题

- 分类: Technology/AI
- 标签: 标签1, 标签2, 标签3"
```

### 自动推送

当未推送的提交数量达到 `push_threshold` 时，自动执行：

```bash
git pull --rebase
git push
```

### 手动同步

```bash
cd data
git pull --rebase  # 拉取远程更新
git push          # 推送本地提交
```

## 🎨 Obsidian 集成

### 打开知识库

在 Obsidian 中：
1. 点击 "打开文件夹作为仓库"
2. 选择 `~/knowledge/data` 目录
3. 开始使用！

### 支持的功能

- ✅ Wiki 链接: `[[笔记标题]]`
- ✅ 标签: `#标签名`
- ✅ 反向链接
- ✅ 图谱视图
- ✅ 搜索和过滤
- ✅ 日常笔记
- ✅ 模板插入

## 🛠️ 脚本工具对比

| 功能 | add-note.py | add-note.js | add-note-simple.sh | update-index.py |
|------|-------------|-------------|-------------------|-----------------|
| 添加笔记 | ✅ | ✅ | ✅ | ❌ |
| 复制源文件 | ✅ | ✅ | ✅ | ❌ |
| 自动更新索引 | ⚙️ 可配置 | ⚙️ 可配置 | ❌ | ✅ (主要功能) |
| 增量更新 | ❌ | ❌ | ❌ | ✅ |
| Git 提交 | ✅ | ✅ | ✅ | ✅ |
| 自动推送 | ✅ | ✅ | ❌ | ✅ |
| 依赖 | PyYAML | js-yaml | 无 | PyYAML |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 📚 最佳实践

### 1. 标题命名

- ✅ **好**: "Python装饰器使用指南"
- ✅ **好**: "Redis缓存优化实践"
- ❌ **差**: "学习笔记1"
- ❌ **差**: "2026-03-22"

### 2. 标签选择

- ✅ **推荐**: 3-6 个标签
- ✅ **覆盖**: 主题 + 技术 + 领域 + 类型
- ✅ **复用**: 优先使用已有标签
- ❌ **避免**: 过于宽泛 (如: "技术")
- ❌ **避免**: 过于具体 (如: "Python3.11装饰器")

### 3. 分类层级

- ✅ **推荐**: `Technology/AI/LLM` (最多 3 层)
- ✅ **推荐**: `Learning/Python`
- ❌ **避免**: `Technology/Backend/Python/Web/Django/ORM` (过深)

### 4. AI 摘要

- ✅ **长度**: 50-200 字
- ✅ **内容**: 提炼核心要点和关键信息
- ❌ **避免**: "这是一篇关于xxx的笔记" (废话)

### 5. 索引更新时机

- ✅ **批量操作后**: 一次性添加多篇笔记后更新
- ✅ **定期维护**: 每周或每月统一更新一次
- ✅ **首次使用**: 导入大量笔记后全量更新
- ❌ **避免**: 每添加一篇笔记就更新 (产生噪音)

## 🔧 故障排除

### 问题 1: PyYAML 未安装

```bash
pip3 install pyyaml
```

### 问题 2: 索引文件损坏

```bash
# 备份现有索引
cp data/_index/tags.yaml data/_index/tags.yaml.bak

# 全量重建索引
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --full
```

### 问题 3: Git 冲突

```bash
cd data
git pull --rebase
# 手动解决冲突
git add .
git rebase --continue
git push
```

### 问题 4: 索引状态不同步

```bash
# 查看当前状态
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --status

# 强制全量更新
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --full
```

### 问题 5: 找不到知识库路径

```bash
# 设置环境变量
export KB_DATA_PATH="$HOME/knowledge/data"

# 或在配置文件中指定
echo "KB_DATA_PATH=$HOME/knowledge/data" >> ~/.zshrc
source ~/.zshrc
```

## 📊 统计信息

当前知识库状态 (2026-03-22):

- 📝 **笔记总数**: 7
- 🏷️ **标签数量**: 24
- 📂 **分类数量**: 9
- 🔗 **Git 提交**: 15+

查看实时统计：

```bash
python3 .codebuddy/skills/knowledge-base/scripts/update-index.py --status
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境

```bash
# 克隆仓库
git clone https://github.com/jinjimz/knowledge.git
cd knowledge

# 安装依赖
pip3 install pyyaml

# 运行测试
bash .codebuddy/skills/knowledge-base/scripts/test.sh
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关资源

- [Obsidian 官网](https://obsidian.md/)
- [CodeBuddy 文档](https://www.codebuddy.ai/docs/zh/)
- [Git 文档](https://git-scm.com/doc)
- [YAML 规范](https://yaml.org/)

## 📮 联系方式

- GitHub: [@jinjimz](https://github.com/jinjimz)
- Issue: [提交问题](https://github.com/jinjimz/knowledge/issues)

---

**Made with ❤️ by [CodeBuddy](https://www.codebuddy.ai/)**
