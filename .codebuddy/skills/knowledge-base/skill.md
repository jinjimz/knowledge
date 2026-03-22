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

- **Base path**: Auto-detected (see Path Detection below)
- **Config**: `$KB_DATA_PATH/.kb-config.yaml` (for push threshold and other settings)
- **Indexes**: `$KB_DATA_PATH/_index/` (categories.yaml, tags.yaml, notes-manifest.yaml)
- **Templates**: `$KB_DATA_PATH/_templates/default.md`
- **Attachments**: `$KB_DATA_PATH/_attachments/`

**Path Detection** (priority order):
1. Environment variable: `$KB_DATA_PATH`
2. Auto-probe from script location (up to 6 levels) for `data/.kb-config.yaml`
3. Default: `$HOME/knowledge/data`

**Note**: Local commit count is tracked via Git history (`git log @{u}..`), not in config file.

## Workflow: Creating a Note

Follow these 6 steps when user requests to create a note:

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

### Step 5: Git Local Commit
Execute in data directory:
```bash
cd $KB_DATA_PATH
git add -A
git commit -m "📝 新增笔记: [Note Title]"
```

### Step 6: Check Push Threshold and Sync
Query local unpushed commits count:
```bash
cd $KB_DATA_PATH
LOCAL_COMMITS=$(git log @{u}.. --oneline 2>/dev/null | wc -l | tr -d ' ')
```

Read push threshold from `$KB_DATA_PATH/.kb-config.yaml` (default: 10).

If `LOCAL_COMMITS >= push_threshold`:
1. Execute `git pull --rebase`
2. Execute `git push`
3. Report sync status

**Note**: No need to update `.kb-config.yaml` for commit count tracking. Git history is the source of truth.

## Manual Index Update

**IMPORTANT**: Index files are NOT automatically updated when creating notes (for performance). You must manually update them using the script.

### Update Index Script

Use `scripts/update-index.py` to update index files:

```bash
# View current index status
python3 scripts/update-index.py --status

# Incremental update (based on git commit history)
python3 scripts/update-index.py --incremental

# Full rebuild (scan all notes)
python3 scripts/update-index.py --full
```

**Shortcut Script** (Recommended):

```bash
# Quick incremental update (default)
bash scripts/update-kb-index.sh

# With options
bash scripts/update-kb-index.sh -i    # incremental
bash scripts/update-kb-index.sh -f    # full
bash scripts/update-kb-index.sh -s    # status
```

### When to Update Index

Recommended scenarios:
- **After batch adding notes**: Update once after multiple notes
- **Before syncing**: Run `--incremental` before `git push`
- **Weekly maintenance**: Run `--status` to check index health
- **After conflicts**: Run `--full` if index seems corrupted

### Index Update Features

- **Incremental mode**: Only processes changed files since last update (tracked via `.index-state`)
- **Full mode**: Scans all notes and rebuilds indexes from scratch
- **Status mode**: Shows index statistics and unindexed changes
- **Automatic fallback**: Incremental mode falls back to full mode if needed

Configuration in `.kb-config.yaml`:
```yaml
index:
  auto_update_on_add_note: false  # Manual update mode
  incremental_update: true        # Support incremental updates
```

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
- **Auto-push when threshold reached** (reads from `.kb-config.yaml`)
- Supports source file copying

**Available scripts:**
- `add-note.py` (Python) - Full-featured, recommended
- `add-note.js` (Node.js) - Requires `js-yaml` package
- `add-note-simple.sh` (Bash) - Lightweight, no index update

All scripts now support automatic push when `push_threshold` is reached.

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
cp $KB_DATA_PATH/_index/tags.yaml $KB_DATA_PATH/_index/tags.yaml.bak
bash scripts/update-index.sh all $KB_DATA_PATH/
```

### Issue 2: Git Conflict
```bash
cd $KB_DATA_PATH
git pull --rebase
git add .
git rebase --continue
git push
```

### Issue 3: Incorrect Category Count
```bash
bash scripts/update-index.sh categories $KB_DATA_PATH/
```

## Example: Complete Flow

### User Input
```
记笔记: https://github.com/siyuan-note/siyuan 是一个不错的笔记系统
```

### Processing
1. Parse: Title="思源笔记 (SiYuan)", Category="Resources/Tools", Tags=["笔记系统","开源","本地优先","工具","知识管理"]
2. Generate content using template
3. Create file: `$KB_DATA_PATH/Resources/Tools/思源笔记_SiYuan_本地优先的笔记系统.md`
4. Update all 3 index files
5. Git commit: "📝 新增笔记: 思源笔记 (SiYuan) - 本地优先的笔记系统"
6. Check unpushed commits: If >= 10, auto push

### Output Feedback
```
✅ 笔记已成功记录到知识库!

笔记详情:
- 📝 标题: 思源笔记 (SiYuan) - 本地优先的笔记系统
- 📂 分类: Resources/Tools
- 🏷️ 标签: #笔记系统 #开源 #本地优先 #工具 #知识管理
- 📍 位置: data/Resources/Tools/思源笔记_SiYuan_本地优先的笔记系统.md

已完成的操作:
1. ✓ 创建笔记文件
2. ✓ Git 本地提交

⚠️  提醒: 索引文件未自动更新，稍后批量更新索引请运行:
   python3 scripts/update-index.py --incremental

当前进度: 1 个未推送提交 (达到 10 次后自动推送)
```

## Related Resources

Scripts in `scripts/` directory:
- `add-note.py` - Add notes programmatically
- `update-index.py` - Update index files (full/incremental)
- `update-kb-index.sh` - Convenient wrapper for index updates
- `init-kb.sh` - Initialize knowledge base
- `git-sync.sh` - Git synchronization helper

Documentation:
- `README.md` - Detailed usage instructions
- `QUICKREF.md` - Quick reference guide for index management
- `USAGE_EXAMPLE.md` - Additional examples

## Performance Notes

**Index Update Performance**:
- Creating a note: ~1s (no index update)
- Incremental update: ~0.5s (1-10 changed notes)
- Full rebuild: ~3s (100 notes)

**Optimization Benefits**:
- 70%+ faster note creation
- Batch operations supported
- Incremental updates minimize overhead
