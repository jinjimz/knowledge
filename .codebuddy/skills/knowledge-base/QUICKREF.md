# 知识库 Skill 快速参考

## 索引管理 🔍

### 基本命令

```bash
# 查看索引状态
bash scripts/update-kb-index.sh -s

# 增量更新索引 (推荐)
bash scripts/update-kb-index.sh -i

# 全量重建索引
bash scripts/update-kb-index.sh -f

# 显示帮助
bash scripts/update-kb-index.sh -h
```

### 完整命令 (Python)

```bash
# 查看状态
python3 scripts/update-index.py --status

# 增量更新
python3 scripts/update-index.py --incremental

# 全量更新
python3 scripts/update-index.py --full
```

## 记笔记流程 📝

### 1. AI辅助记笔记

直接对AI说:

```
记笔记: https://github.com/user/repo 这是一个很好的工具
```

AI会自动:
- ✅ 创建笔记文件
- ✅ 生成标题、标签、分类
- ✅ 提交到Git
- ⚠️ **不会**自动更新索引(需手动)

### 2. 手动更新索引

记完笔记后运行:

```bash
# 方式1: 快捷命令 (推荐)
bash scripts/update-kb-index.sh

# 方式2: Python命令
python3 scripts/update-index.py --incremental
```

### 3. 推送到远程

```bash
git push
```

## 工作流模式 🔄

### 模式A: 单笔记流程

```bash
# 1. 记笔记 (通过AI)
# 2. 更新索引
bash scripts/update-kb-index.sh -i
# 3. 推送
git push
```

### 模式B: 批量笔记流程 (推荐)

```bash
# 1. 记多条笔记 (通过AI)
# 2. 批量更新索引一次
bash scripts/update-kb-index.sh -i
# 3. 推送
git push
```

## 索引更新机制 ⚙️

### 增量更新

- 基于Git提交历史
- 仅处理变更的笔记文件
- 速度快,推荐日常使用

工作原理:
1. 读取 `.index-state` 文件中的上次commit ID
2. 使用 `git diff` 找出变更的笔记
3. 只更新变更的笔记索引
4. 保存当前commit ID

### 全量更新

- 扫描所有笔记文件
- 重建完整索引
- 用于索引损坏或初始化

## 配置说明 ⚙️

### .kb-config.yaml

```yaml
# 索引更新配置
index:
  auto_update_on_add_note: false  # 记笔记时不自动更新
  incremental_update: true        # 支持增量更新
```

### Git推送配置

```yaml
git:
  push_threshold: 1               # 自动推送阈值
  auto_pull_before_push: true
```

## 常见场景 💡

### 场景1: 每天记几条笔记

```bash
# 早上记笔记
AI> 记笔记: 今天学到的知识...

# 中午记笔记  
AI> 记笔记: 午间阅读笔记...

# 晚上统一更新索引
bash scripts/update-kb-index.sh -i
git push
```

### 场景2: 迁移大量笔记

```bash
# 批量复制文件到 data/ 目录
# ...

# 提交到Git
git add -A
git commit -m "📝 批量导入笔记"

# 全量重建索引
bash scripts/update-kb-index.sh -f

# 推送
git push
```

### 场景3: 定期维护

```bash
# 每周检查索引状态
bash scripts/update-kb-index.sh -s

# 如果有未索引的文件,运行增量更新
bash scripts/update-kb-index.sh -i
```

## 故障排除 🔧

### 问题1: 索引不是最新的

```bash
# 检查状态
bash scripts/update-kb-index.sh -s

# 如果有未索引文件,运行增量更新
bash scripts/update-kb-index.sh -i
```

### 问题2: 索引文件损坏

```bash
# 重建索引
bash scripts/update-kb-index.sh -f
```

### 问题3: Git冲突

```bash
# 拉取远程
git pull --rebase

# 解决冲突后
git push

# 重建索引(确保一致性)
bash scripts/update-kb-index.sh -f
```

## 性能对比 ⚡

| 操作 | 笔记数 | 耗时 | 说明 |
|------|--------|------|------|
| 记笔记 | 1篇 | ~1s | 不更新索引 |
| 增量更新 | 1-10篇变更 | ~0.5s | 基于Git diff |
| 全量更新 | 100篇总量 | ~3s | 扫描所有文件 |
| 增量更新 | 100篇总量 | ~0.5s | 仅处理变更 |

**优化效果**: 记笔记速度提升 70%+

## 最佳实践 ⭐

1. **批量更新**: 记多条笔记后统一更新索引
2. **增量优先**: 日常使用增量更新,速度快
3. **定期检查**: 每周运行一次状态检查
4. **全量重建**: 仅在索引损坏时使用
5. **及时推送**: 更新索引后及时推送到远程

## 快捷命令别名 (可选) 🚀

添加到 `~/.zshrc` 或 `~/.bashrc`:

```bash
# 知识库别名
alias kb-status='bash ~/knowledge/.codebuddy/skills/knowledge-base/scripts/update-kb-index.sh -s'
alias kb-update='bash ~/knowledge/.codebuddy/skills/knowledge-base/scripts/update-kb-index.sh -i'
alias kb-rebuild='bash ~/knowledge/.codebuddy/skills/knowledge-base/scripts/update-kb-index.sh -f'
alias kb-sync='kb-update && cd ~/knowledge && git push && cd -'
```

使用:

```bash
kb-status   # 查看状态
kb-update   # 增量更新
kb-rebuild  # 重建索引
kb-sync     # 更新并推送
```
