# 知识库管理 Skill

个人知识库管理系统，支持多级分类、标签管理、Git同步，兼容Obsidian。

## 快速开始

### 📁 重要：知识库结构说明

当前知识库采用**分离式结构**：

```
$KB_ROOT/                               # Git 仓库根目录 (e.g., ~/knowledge)
├── .codebuddy/                         # CodeBuddy 配置（不参与知识库内容）
│   └── skills/knowledge-base/          # 本 Skill 及脚本
├── data/                               # 📁 知识库数据目录（核心）
│   ├── .kb-config.yaml                 # 知识库配置文件
│   ├── _index/                         # 索引文件
│   ├── _templates/                     # 笔记模板
│   ├── _attachments/                   # 附件存储
│   └── [分类目录]/                     # 笔记内容
└── .gitignore
```

**所有脚本操作都基于 `data/` 目录!**
**路径自动探测**: 脚本会自动查找 `$KB_DATA_PATH` 环境变量或从当前位置向上查找。

### 安装依赖

```bash
# Python依赖（推荐）
pip3 install pyyaml

# Node.js依赖（可选）
npm install js-yaml
```

### 添加笔记

#### 方法一：使用Python脚本（推荐）✨

```bash
cd $KB_ROOT  # 或者任意位置，脚本会自动探测
python3 .codebuddy/skills/knowledge-base/scripts/add-note.py \
  "笔记标题" \
  "这是一段AI生成的摘要..." \
  "标签1,标签2,标签3" \
  "Technology/AI" \
  "/path/to/source.md"
```

**注意**：脚本已自动配置为操作 `data/` 目录，无需手动指定路径。

**参数说明**：
1. **标题**：笔记标题
2. **摘要**：50-200字的简短摘要
3. **标签**：逗号分隔，3-6个标签
4. **分类**：层级分类，用 `/` 分隔，如 `Technology/AI`
5. **源文件**（可选）：如果提供，直接复制源文件内容

**功能特性**：
- ✅ 自动从源文件复制内容
- ✅ 智能处理frontmatter（保留或新增）
- ✅ 自动更新三个索引文件
- ✅ 自动Git提交
- ✅ 分类计数自动维护

#### 方法二：使用Bash脚本（简化版）

```bash
cd $KB_ROOT  # 或任意位置,脚本会自动探测
chmod +x .codebuddy/skills/knowledge-base/scripts/add-note-simple.sh
./.codebuddy/skills/knowledge-base/scripts/add-note-simple.sh \
  "笔记标题" \
  "摘要" \
  "标签1,标签2" \
  "Technology/AI" \
  "/path/to/source.md"
```

**注意**：Bash版本不会自动更新索引文件，需要手动处理。

#### 方法三：通过AI辅助

直接对AI说：

```
记笔记：我有一个OpenClaw架构分析文档，路径是/path/to/架构.md
```

AI会：
1. 读取源文件
2. 生成AI摘要
3. 提取合适的标签和分类
4. 调用脚本添加笔记
5. 更新索引并提交Git

## 工作流程示例

### 示例1：从现有文件创建笔记

```bash
# 你有一个现成的Markdown文件
SOURCE_FILE="/path/to/your/notes/架构.md"

# 运行脚本(可在任意位置)
python3 .codebuddy/skills/knowledge-base/scripts/add-note.py \
  "OpenClaw技术架构分析" \
  "OpenClaw是个人AI助手网关，采用TypeScript+Node.js实现，支持多Agent协作..." \
  "架构,AI,Agent,Gateway,TypeScript" \
  "Technology/AI" \
  "$SOURCE_FILE"

# 输出：
# 📍 知识库路径: /path/to/knowledge/data
# 📝 开始添加笔记...
# 📂 目标路径: Technology/AI/OpenClaw技术架构分析.md
# 📄 复制源文件: /path/to/your/notes/架构.md
# ✓ 笔记已创建: OpenClaw技术架构分析.md
# 📑 更新索引...
# ✓ 索引更新完成
# 📦 提交到Git...
# ✓ Git提交成功
# 
# ✅ 笔记添加完成!
# 📍 位置: Technology/AI/OpenClaw技术架构分析.md
```

### 示例2：创建新笔记

```bash
python3 .codebuddy/skills/knowledge-base/scripts/add-note.py \
  "Python装饰器学习笔记" \
  "学习了Python装饰器的原理和使用方法，包括函数装饰器和类装饰器" \
  "Python,编程,装饰器" \
  "Learning/Python"

# 会创建一个使用模板的新笔记
```

## 目录结构

```
$KB_ROOT/                        # 项目根目录（Git仓库, 如 ~/knowledge）
├── .codebuddy/                  # CodeBuddy配置
│   └── skills/knowledge-base/   # 本Skill及脚本
├── data/                        # 📁 知识库数据目录
│   ├── .kb-config.yaml         # 知识库配置
│   ├── _index/                 # 索引目录
│   │   ├── categories.yaml    # 分类索引
│   │   ├── tags.yaml         # 标签索引
│   │   └── notes-manifest.yaml # 笔记清单
│   ├── _templates/            # 模板目录
│   │   └── default.md        # 默认模板
│   ├── _attachments/         # 附件目录
│   │   └── YYYY-MM-DD/      # 按日期组织
│   ├── Technology/           # 分类目录
│   │   ├── AI/
│   │   ├── Programming/
│   │   └── ...
│   ├── Learning/
│   ├── Work/
│   └── ...
└── .gitignore
```

## 索引文件说明

### categories.yaml

记录分类层级和笔记计数：

```yaml
# 分类索引
# 更新时间: 2026-03-22T10:30:00
categories:
  Technology:
    AI:
      count: 2
    Programming:
      count: 5
  Learning:
    count: 3
```

### tags.yaml

记录每个标签关联的笔记：

```yaml
# 标签索引
# 更新时间: 2026-03-22T10:30:00
tags:
  架构:
    - path: "Technology/AI/OpenClaw技术架构分析.md"
      title: "OpenClaw技术架构分析"
    - path: "Technology/System/微服务架构.md"
      title: "微服务架构设计"
```

### notes-manifest.yaml

所有笔记的完整清单：

```yaml
# 笔记清单
# 更新时间: 2026-03-22T10:30:00
notes:
  - id: "1"
    title: "OpenClaw技术架构分析"
    path: "Technology/AI/OpenClaw技术架构分析.md"
    category: "Technology/AI"
    tags:
      - 架构
      - AI
      - Agent
    created: "2026-03-22T10:30:00"
    updated: "2026-03-22T10:30:00"
    ai_summary: "OpenClaw是个人AI助手网关..."
```

## 笔记格式

### Frontmatter（YAML元数据）

```yaml
---
title: "笔记标题"
created: "2026-03-22T10:30:00"
updated: "2026-03-22T10:30:00"
tags:
  - 标签1
  - 标签2
category: "分类/子分类"
ai_summary: "AI生成的摘要"
---
```

### 正文格式

```markdown
# 笔记标题

#标签1 #标签2 #标签3

> AI摘要内容

## 内容

笔记正文...
```

## Git工作流

脚本会自动：
1. `git add` 新笔记和索引文件（在 `data/` 目录下）
2. `git commit` 提交变更（在项目根目录）
3. 提交信息格式：
   ```
   添加笔记: 笔记标题
   
   - 分类: Technology/AI
   - 标签: 标签1, 标签2, 标签3
   ```

需要手动推送：
```bash
cd $KB_ROOT
git push
```

## 与Obsidian集成

1. 在Obsidian中打开 `$KB_ROOT/data` 目录（如 `~/knowledge/data`）作为vault
2. 所有笔记自动同步显示
3. 支持：
   - Wiki链接：`[[笔记标题]]`
   - 标签：`#标签名`
   - 反向链接
   - 图谱视图
   - 搜索

## 故障排除

### PyYAML未安装

```bash
pip3 install pyyaml
```

### 索引文件损坏

运行更新索引脚本：
```bash
cd $KB_ROOT
bash .codebuddy/skills/knowledge-base/scripts/update-index.sh all data/
```

### Git冲突

```bash
cd $KB_ROOT
git pull --rebase
# 解决冲突后
git push
```

## 最佳实践

1. **标题命名**：清晰简洁，描述核心内容
2. **标签选择**：3-6个标签，涵盖主题、技术、领域
3. **分类层级**：不超过3层，如 `Technology/AI/LLM`
4. **AI摘要**：50-200字，提炼核心要点
5. **源文件**：有现成文档时优先使用源文件复制
6. **定期推送**：及时推送到远程仓库备份

## 脚本对比

| 特性 | add-note.py | add-note-simple.sh | add-note.js |
|------|-------------|-------------------|-------------|
| 源文件复制 | ✅ | ✅ | ✅ |
| 自动更新索引 | ✅ | ❌ | ✅ |
| Git自动提交 | ✅ | ✅ | ✅ |
| 依赖 | PyYAML | 无 | js-yaml |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## 更新日志

### 2026-03-22 v2
- ✅ **重构目录结构**：采用分离式结构，知识库数据位于 `data/` 目录
- ✅ 更新 add-note.py 路径配置
- ✅ 更新 init-kb.sh 支持新结构
- ✅ 完善文档说明

### 2026-03-22 v1
- ✅ 创建add-note.py核心脚本
- ✅ 添加源文件复制功能
- ✅ 智能frontmatter处理
- ✅ 自动索引维护
- ✅ Git自动提交
- ✅ 创建bash简化版本
- ✅ 完善文档和示例

## 许可证

MIT
