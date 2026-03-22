---
name: knowledge-base
description: This skill should be used when the user wants to create notes, manage a knowledge base, or perform operations like "记笔记", "知识库状态", "同步知识库", "搜索知识库", or "整理知识库". It provides workflows for creating notes with proper categorization, tagging, indexing, and Git synchronization, fully compatible with Obsidian.
---

# Personal Knowledge Base Management

A personal knowledge management system supporting multi-level categorization, tag management, Git synchronization, and full Obsidian compatibility.

## When to Use This Skill

Use this skill when the user requests:
- **Create notes**: "记笔记" or "记笔记: [content]"
- **Check status**: "知识库状态" to view statistics
- **Sync repository**: "同步知识库" to manually trigger Git sync
- **Search notes**: "搜索知识库: [keyword]" to search notes
- **Rebuild index**: "整理知识库" to rebuild index files

## Configuration

- **Base path**: `/Users/coriase/work/knowledge/data/`
- **Config**: `data/.kb-config.yaml`
- **Indexes**: `data/_index/` (categories.yaml, tags.yaml, notes-manifest.yaml)
- **Templates**: `data/_templates/default.md`
- **Attachments**: `data/_attachments/`

## Workflow: Creating a Note

Follow these 7 steps when user requests to create a note:

### Step 1: Parse Input
Extract from user input:
- Title (infer from content)
- URL (if present, e.g., GitHub repo link)
- Tags (recommend 3-6 relevant tags)
- Category (match to existing hierarchy)

### Step 2: Intelligent Categorization
Read `data/_index/categories.yaml` and select:
- Tools/Products → `Resources/Tools`
- Technology/Programming → `Technology/[subcategory]`
- Learning/Tutorials → `Learning/[subcategory]`
- Work-related → `Work`
- Ideas → `Ideas`

### Step 3: Generate Note Content
Use template from `data/_templates/default.md`:
```yaml
---
title: "[Note Title]"
created: "[ISO 8601 timestamp]"
updated: "[ISO 8601 timestamp]"
tags: [tag1, tag2, tag3]
category: "[Category/Subcategory]"
ai_summary: "[50-200 word summary]"
---

# [Note Title]

## Basic Information
(If URL present)
- **Link**: [URL]
- **Type**: [Tool/Article/etc.]

## Content
[User-provided content]

## Related Tags
#tag1 #tag2 #tag3
```

### Step 4: Create File
Write note to: `data/[category-path]/[safe-filename].md`

Filename rules:
- Replace special characters with underscores
- Maintain readability
- Example: `思源笔记_SiYuan_本地优先的笔记系统.md`

### Step 5: Update Index Files

**5.1 Update tags.yaml**
Add entries to `data/_index/tags.yaml`:
```yaml
tags:
  [tag-name]:
    - path: "[category]/[filename].md"
      title: "[Note Title]"
```

**5.2 Update categories.yaml**
Increment count in `data/_index/categories.yaml`:
```yaml
categories:
  [CategoryName]:
    [Subcategory]:
      count: N  # Increment by 1
```

**5.3 Update notes-manifest.yaml**
Add new entry to `data/_index/notes-manifest.yaml`:
```yaml
notes:
  - id: "[N]"  # Increment ID
    title: "[Note Title]"
    path: "[category]/[filename].md"
    category: "[Category/Subcategory]"
    tags: [tag list]
    created: "[timestamp]"
    updated: "[timestamp]"
    ai_summary: "[summary]"
```

### Step 6: Git Local Commit
Execute in data directory:
```bash
cd /Users/coriase/work/knowledge/data
git add -A
git commit -m "📝 新增笔记: [Note Title]"
```

### Step 7: Update Config and Check Push Threshold
Update `data/.kb-config.yaml`:
```yaml
git:
  local_commit_count: N  # Increment by 1
  push_threshold: 10
```

If `local_commit_count >= 10`:
1. Execute `git pull --rebase`
2. Execute `git push`
3. Reset `local_commit_count` to 0

## Using Scripts (Optional)

For batch operations, use Python script located in `scripts/add-note.py`:
```bash
python3 scripts/add-note.py \
  "[Note Title]" \
  "[AI-generated summary]" \
  "[tag1,tag2,tag3]" \
  "[Category/Subcategory]" \
  "[/path/to/source.md]"
```

Features:
- Automatically creates note file
- Updates all three index files
- Commits to Git
- Supports source file copying

## Important Guidelines

### Knowledge Base Structure
- Content in `data/` directory
- Git operations execute in `data/`
- All paths relative to `data/`

### Obsidian Compatibility
- Use standard Markdown format
- Support wiki links: `[[Note Title]]`
- Support bidirectional links

### Dual Tag Format
- Frontmatter: array format `tags: [tag1, tag2]`
- Body: inline format `#tag1 #tag2`

### Git Safety
- Always pull before push: `git pull --rebase`
- Handle conflicts manually
- Use emoji in commits: 📝 新增笔记

### Index Maintenance
- Update all three index files when creating notes
- Keep timestamps synchronized
- Maintain category counts

### Filename Standards
- Use underscores to separate words
- Avoid: `/ : * ? " < > |`
- Keep readable and descriptive

## Best Practices

### Title Naming
- ✅ Clear, concise, describing core content
- ✅ Include keywords for searchability
- ❌ Avoid overly long or vague titles

### Tag Selection
- ✅ 3-6 tags optimal
- ✅ Cover: topic + technology + domain + type
- ✅ Reuse existing tags
- ❌ Avoid overly broad or duplicate tags

### Category Hierarchy
- ✅ Maximum 3 levels deep
- ✅ Example: `Technology/AI/LLM`
- ❌ Avoid overly granular categories

### AI Summary
- ✅ 50-200 words optimal
- ✅ Extract core points
- ❌ Avoid overly brief or verbose

## Troubleshooting

### Issue 1: Index File Format Error
```bash
cp data/_index/tags.yaml data/_index/tags.yaml.bak
bash scripts/update-index.sh all data/
```

### Issue 2: Git Conflict
```bash
cd /Users/coriase/work/knowledge/data
git pull --rebase
git add .
git rebase --continue
git push
```

### Issue 3: Incorrect Category Count
```bash
bash scripts/update-index.sh categories data/
```

## Example: Complete Flow

### User Input
```
记笔记: https://github.com/siyuan-note/siyuan 是一个不错的笔记系统
```

### Processing
1. Parse: Title="思源笔记 (SiYuan)", Category="Resources/Tools", Tags=["笔记系统","开源","本地优先","工具","知识管理"]
2. Generate content using template
3. Create file: `data/Resources/Tools/思源笔记_SiYuan_本地优先的笔记系统.md`
4. Update all 3 index files
5. Git commit: "📝 新增笔记: 思源笔记 (SiYuan) - 本地优先的笔记系统"
6. Update config: `local_commit_count: 1`

### Output Feedback
```
✅ 笔记已成功记录到知识库！

笔记详情:
- 📝 标题: 思源笔记 (SiYuan) - 本地优先的笔记系统
- 📂 分类: Resources/Tools
- 🏷️ 标签: #笔记系统 #开源 #本地优先 #工具 #知识管理
- 📍 位置: data/Resources/Tools/思源笔记_SiYuan_本地优先的笔记系统.md

已完成的操作:
1. ✓ 创建笔记文件
2. ✓ 更新标签索引
3. ✓ 更新分类索引
4. ✓ 更新笔记清单
5. ✓ Git 本地提交

当前进度: 1/10 (达到 10 次提交后自动推送)
```

## Related Resources

Scripts in `scripts/` directory:
- `add-note.py` - Add notes programmatically
- `init-kb.sh` - Initialize knowledge base
- `git-sync.sh` - Git synchronization helper
- `update-index.sh` - Rebuild index files

Documentation:
- `README.md` - Detailed usage instructions
- `USAGE_EXAMPLE.md` - Additional examples
