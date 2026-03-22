# Knowledge-Base Skill 使用示例

本文档展示如何在AI对话中使用knowledge-base skill。

## 场景1: 从现有文件创建笔记

### 用户输入

```
记笔记：我通过codebuddy分析openclaw源码生成的openclaw架构文档：/Users/coriase/work/obsidian/tech/tech/架构.md
```

### AI处理流程

1. **读取源文件**
   ```python
   read_file("/Users/coriase/work/obsidian/tech/tech/架构.md")
   ```

2. **分析内容生成元数据**
   - 标题: "OpenClaw技术架构分析"
   - AI摘要: 提取核心要点（50-200字）
   - 标签: 识别关键技术标签
   - 分类: 确定合适的分类

3. **调用脚本创建笔记**
   ```python
   execute_command(
       command='python3 /Users/coriase/work/knowledge/.codebuddy/skills/knowledge-base/scripts/add-note.py '
               '"OpenClaw技术架构分析" '
               '"OpenClaw是个人AI助手网关，采用TypeScript+Node.js..." '
               '"架构,AI,Agent,Gateway,TypeScript,多Agent协作" '
               '"Technology/AI" '
               '"/Users/coriase/work/obsidian/tech/tech/架构.md"'
   )
   ```

4. **确认完成**
   向用户报告：
   - ✅ 笔记已创建
   - 📍 位置: Technology/AI/OpenClaw技术架构分析.md
   - 📦 Git已提交

### 实际代码示例

```python
import subprocess

# 元数据
title = "OpenClaw技术架构分析"
ai_summary = "OpenClaw是个人AI助手网关，运行在本地设备上，通过20+消息渠道提供AI对话能力..."
tags = "架构,AI,Agent,Gateway,TypeScript,多Agent协作"
category = "Technology/AI"
source_file = "/Users/coriase/work/obsidian/tech/tech/架构.md"

# 调用脚本
result = subprocess.run([
    'python3',
    '/Users/coriase/work/knowledge/.codebuddy/skills/knowledge-base/scripts/add-note.py',
    title,
    ai_summary,
    tags,
    category,
    source_file
], cwd='/Users/coriase/work/knowledge', capture_output=True, text=True)

print(result.stdout)
```

---

## 场景2: 创建新笔记（无源文件）

### 用户输入

```
记笔记：今天学习了Python装饰器，包括函数装饰器和类装饰器的使用方法
```

### AI处理流程

1. **生成元数据**
   - 标题: "Python装饰器学习笔记"
   - AI摘要: "学习了Python装饰器的原理和使用方法..."
   - 标签: "Python,编程,装饰器"
   - 分类: "Learning/Python"

2. **调用脚本（不提供源文件）**
   ```bash
   python3 add-note.py \
     "Python装饰器学习笔记" \
     "学习了Python装饰器的原理..." \
     "Python,编程,装饰器" \
     "Learning/Python"
   ```

3. **笔记内容**
   脚本会使用模板创建笔记，AI可以后续补充内容

---

## 场景3: 批量导入笔记

### 用户输入

```
我有一个包含多个Markdown文件的目录：/Users/xxx/notes/
帮我批量导入到知识库
```

### AI处理流程

1. **列出目录中的文件**
   ```python
   import os
   files = [f for f in os.listdir('/Users/xxx/notes/') if f.endswith('.md')]
   ```

2. **逐个处理**
   ```python
   for file in files:
       # 读取文件
       content = read_file(f'/Users/xxx/notes/{file}')
       
       # 分析内容，提取标题、标签等
       title = extract_title(content)
       tags = extract_tags(content)
       category = suggest_category(content)
       ai_summary = generate_summary(content)
       
       # 调用脚本
       subprocess.run([
           'python3', 'add-note.py',
           title, ai_summary, tags, category,
           f'/Users/xxx/notes/{file}'
       ])
   ```

---

## 场景4: 更新现有笔记

### 用户输入

```
更新笔记"OpenClaw技术架构分析"，添加新的章节
```

### AI处理流程

1. **查找笔记**
   ```python
   # 搜索笔记清单
   import yaml
   manifest = yaml.safe_load(open('knowledge/_index/notes-manifest.yaml'))
   note = next(n for n in manifest['notes'] if n['title'] == 'OpenClaw技术架构分析')
   note_path = note['path']
   ```

2. **直接编辑文件**
   ```python
   # 读取现有内容
   content = read_file(f'knowledge/{note_path}')
   
   # 添加新章节
   new_content = content + "\n\n## 新章节\n\n新内容..."
   
   # 写回文件
   write_to_file(f'knowledge/{note_path}', new_content)
   
   # Git提交
   execute_command('cd knowledge && git add . && git commit -m "更新笔记: OpenClaw技术架构分析"')
   ```

---

## 场景5: 搜索知识库

### 用户输入

```
搜索知识库：Agent协作
```

### AI处理流程

1. **搜索标签索引**
   ```python
   import yaml
   tags_data = yaml.safe_load(open('knowledge/_index/tags.yaml'))
   
   results = []
   for tag, notes in tags_data['tags'].items():
       if 'agent' in tag.lower() or '协作' in tag:
           results.extend(notes)
   ```

2. **全文搜索**
   ```python
   search_content(
       pattern='Agent.*协作',
       path='knowledge/',
       recursive=True
   )
   ```

3. **返回结果**
   列出匹配的笔记列表，包括标题、路径、摘要

---

## 辅助函数示例

### 提取标题

```python
def extract_title(content):
    """从内容中提取标题"""
    # 优先从frontmatter提取
    if content.startswith('---'):
        frontmatter = content.split('---')[1]
        import yaml
        meta = yaml.safe_load(frontmatter)
        if 'title' in meta:
            return meta['title']
    
    # 否则从第一个一级标题提取
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    
    return "未命名笔记"
```

### 生成AI摘要

```python
def generate_summary(content, max_length=200):
    """生成AI摘要"""
    # 使用LLM生成摘要
    prompt = f"请用50-200字总结以下内容的核心要点:\n\n{content[:2000]}"
    summary = llm.generate(prompt)
    return summary[:max_length]
```

### 智能分类建议

```python
def suggest_category(content, title):
    """智能建议分类"""
    # 读取现有分类
    import yaml
    categories = yaml.safe_load(open('knowledge/_index/categories.yaml'))
    
    # 使用LLM判断
    prompt = f"""
    现有分类：{list(categories['categories'].keys())}
    
    笔记标题：{title}
    笔记内容摘要：{content[:500]}
    
    请选择最合适的分类（可以是现有分类或建议新分类）：
    """
    
    suggested = llm.generate(prompt)
    return suggested.strip()
```

### 提取标签

```python
def extract_tags(content, title):
    """提取标签"""
    # 1. 从frontmatter提取
    if content.startswith('---'):
        frontmatter = content.split('---')[1]
        import yaml
        meta = yaml.safe_load(frontmatter)
        if 'tags' in meta:
            return meta['tags']
    
    # 2. 从行内标签提取
    import re
    inline_tags = re.findall(r'#(\w+)', content)
    
    # 3. 使用LLM生成
    if not inline_tags:
        prompt = f"请为以下内容生成3-6个关键标签（逗号分隔）：\n标题：{title}\n内容：{content[:500]}"
        tags_str = llm.generate(prompt)
        return [t.strip() for t in tags_str.split(',')]
    
    return inline_tags[:6]
```

---

## 完整示例：AI处理"记笔记"请求

```python
def handle_note_request(user_message):
    """处理用户的记笔记请求"""
    
    # 1. 解析用户输入
    match = re.match(r'记笔记[：:]\s*(.*)', user_message)
    if not match:
        return "请使用格式：记笔记：内容或文件路径"
    
    content_or_path = match.group(1)
    
    # 2. 判断是文件路径还是内容
    if os.path.exists(content_or_path):
        # 是文件路径
        source_file = content_or_path
        content = read_file(source_file)
    else:
        # 是内容描述
        source_file = None
        content = content_or_path
    
    # 3. 生成元数据
    title = extract_title(content) if source_file else generate_title(content)
    ai_summary = generate_summary(content)
    tags = extract_tags(content, title)
    category = suggest_category(content, title)
    
    # 4. 调用脚本
    cmd = [
        'python3',
        '/Users/coriase/work/knowledge/.codebuddy/skills/knowledge-base/scripts/add-note.py',
        title,
        ai_summary,
        ','.join(tags),
        category
    ]
    
    if source_file:
        cmd.append(source_file)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # 5. 返回结果
    if result.returncode == 0:
        return f"""
✅ 笔记已添加到知识库！

📝 **标题**: {title}
📂 **分类**: {category}
🏷️  **标签**: {', '.join(tags)}
📍 **位置**: knowledge/{category}/{sanitize_filename(title)}.md
📦 **Git**: 已自动提交

💡 **摘要**: {ai_summary}
"""
    else:
        return f"❌ 添加笔记失败：{result.stderr}"

# 使用
response = handle_note_request("记笔记：/Users/xxx/架构.md")
print(response)
```

---

## 最佳实践

### 1. AI摘要质量

生成高质量的AI摘要：
- 长度控制在50-200字
- 提炼核心要点，不要照抄原文
- 突出文档的价值和适用场景

### 2. 标签选择

- 3-6个标签为宜
- 包含技术栈、领域、主题等维度
- 使用一致的标签词汇（避免同义词）

### 3. 分类策略

- 不超过3层：`一级/二级/三级`
- 遵循现有分类体系
- 新分类需慎重，避免碎片化

### 4. 错误处理

```python
try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("✅ 成功:", result.stdout)
except subprocess.CalledProcessError as e:
    print("❌ 失败:", e.stderr)
    # 尝试备选方案或提示用户手动处理
```

---

## 总结

knowledge-base skill提供了完整的知识管理能力：

1. **添加笔记**：支持源文件复制和模板创建
2. **自动索引**：维护分类、标签、清单三个索引
3. **Git集成**：自动提交变更
4. **AI辅助**：智能提取元数据、生成摘要

通过合理使用，可以构建一个高效的个人知识库系统！
