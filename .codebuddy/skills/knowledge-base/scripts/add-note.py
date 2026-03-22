#!/usr/bin/env python3
"""
知识库笔记添加脚本 (Python版本)
用法: python3 add-note.py <标题> <摘要> <标签> <分类> [源文件路径]
"""

import os
import sys
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
try:
    import yaml
except ImportError:
    print("❌ 需要安装PyYAML: pip3 install pyyaml")
    sys.exit(1)

# 配置
SCRIPT_DIR = Path(__file__).parent
# 从 .codebuddy/skills/knowledge-base/scripts/ 向上4级到达项目根目录
WORKSPACE_ROOT = (SCRIPT_DIR / '../../../..').resolve()
KB_ROOT = WORKSPACE_ROOT / 'data'
INDEX_DIR = KB_ROOT / '_index'
TEMPLATE_FILE = KB_ROOT / '_templates' / 'default.md'

def get_timestamp():
    """获取当前时间戳"""
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

def sanitize_filename(name):
    """清理文件名"""
    return re.sub(r'[/\\:*?"<>|]', '_', name)

def read_yaml_file(file_path):
    """读取YAML文件"""
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def write_yaml_file(file_path, data):
    """写入YAML文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def update_category_count(categories_dict, category_path, delta=1):
    """更新分类计数"""
    parts = category_path.split('/')
    current = categories_dict.setdefault('categories', {})
    
    for i, part in enumerate(parts):
        if i == len(parts) - 1:
            # 最后一级
            if part not in current:
                current[part] = {'count': 0}
            current[part]['count'] = current[part].get('count', 0) + delta
        else:
            # 中间级别
            if part not in current:
                current[part] = {}
            elif 'count' in current[part]:
                # 如果这一级有count，说明它既是分类又是父目录，需要重构
                count = current[part].pop('count')
                current[part] = {}
            current = current[part]

def main():
    """主函数"""
    # 解析参数
    if len(sys.argv) < 5:
        print("用法: python3 add-note.py <标题> <摘要> <标签> <分类> [源文件路径]")
        print("示例: python3 add-note.py '标题' '摘要' '标签1,标签2' 'Technology/AI' '/path/to/source.md'")
        sys.exit(1)
    
    title = sys.argv[1]
    ai_summary = sys.argv[2]
    tags_str = sys.argv[3]
    category = sys.argv[4]
    source_file = sys.argv[5] if len(sys.argv) > 5 else None
    
    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
    
    print('📝 开始添加笔记...')
    
    try:
        # 1. 确定目标路径
        category_path = Path(category)
        target_dir = KB_ROOT / category_path
        filename = sanitize_filename(title) + '.md'
        target_file = target_dir / filename
        relative_path = target_file.relative_to(KB_ROOT)
        
        print(f'📂 目标路径: {relative_path}')
        
        # 2. 创建目录
        target_dir.mkdir(parents=True, exist_ok=True)
        if not target_dir.exists():
            print(f'✓ 创建目录: {category_path}')
        
        # 3. 处理笔记内容
        timestamp = get_timestamp()
        
        if source_file and Path(source_file).exists():
            print(f'📄 复制源文件: {source_file}')
            source_path = Path(source_file)
            
            with open(source_path, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            # 检查是否已有frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', source_content, re.DOTALL)
            
            if frontmatter_match:
                # 已有frontmatter，合并
                existing_frontmatter = yaml.safe_load(frontmatter_match.group(1))
                merged_frontmatter = {
                    'title': title,
                    'created': existing_frontmatter.get('created', timestamp),
                    'updated': timestamp,
                    'tags': tags,
                    'category': category,
                    'ai_summary': ai_summary,
                    **{k: v for k, v in existing_frontmatter.items() 
                       if k not in ['title', 'created', 'updated', 'tags', 'category', 'ai_summary']}
                }
                note_content = f"---\n{yaml.dump(merged_frontmatter, allow_unicode=True, default_flow_style=False)}---\n{frontmatter_match.group(2)}"
            else:
                # 无frontmatter，添加
                frontmatter = {
                    'title': title,
                    'created': timestamp,
                    'updated': timestamp,
                    'tags': tags,
                    'category': category,
                    'ai_summary': ai_summary
                }
                tag_line = ' '.join(f'#{tag}' for tag in tags)
                note_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)}---\n\n# {title}\n\n{tag_line}\n\n{source_content}"
        else:
            # 使用模板
            print('📝 使用模板创建笔记')
            if TEMPLATE_FILE.exists():
                with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                    template = f.read()
            else:
                template = '''---
title: "{{title}}"
created: "{{created}}"
updated: "{{updated}}"
tags: {{tags}}
category: "{{category}}"
ai_summary: "{{ai_summary}}"
---

# {{title}}

{{content}}
'''
            
            tag_line = ' '.join(f'#{tag}' for tag in tags)
            note_content = (template
                .replace('{{title}}', title)
                .replace('{{created}}', timestamp)
                .replace('{{updated}}', timestamp)
                .replace('{{tags}}', str(tags))
                .replace('{{category}}', category)
                .replace('{{ai_summary}}', ai_summary)
                .replace('{{content}}', f'{tag_line}\n\n> {ai_summary}'))
        
        # 4. 写入笔记
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(note_content)
        print(f'✓ 笔记已创建: {filename}')
        
        # 5. 更新索引
        print('📑 更新索引...')
        
        categories_file = INDEX_DIR / 'categories.yaml'
        tags_file = INDEX_DIR / 'tags.yaml'
        manifest_file = INDEX_DIR / 'notes-manifest.yaml'
        
        # 读取索引
        categories_data = read_yaml_file(categories_file)
        tags_data = read_yaml_file(tags_file)
        manifest_data = read_yaml_file(manifest_file)
        
        # 更新分类
        update_category_count(categories_data, category, 1)
        
        # 更新标签
        if 'tags' not in tags_data:
            tags_data['tags'] = {}
        for tag in tags:
            if tag not in tags_data['tags']:
                tags_data['tags'][tag] = []
            tags_data['tags'][tag].append({
                'path': str(relative_path),
                'title': title
            })
        
        # 更新笔记清单
        if 'notes' not in manifest_data:
            manifest_data['notes'] = []
        max_id = max([int(n['id']) for n in manifest_data['notes']], default=0)
        manifest_data['notes'].append({
            'id': str(max_id + 1),
            'title': title,
            'path': str(relative_path),
            'category': category,
            'tags': tags,
            'created': timestamp,
            'updated': timestamp,
            'ai_summary': ai_summary
        })
        
        # 更新时间戳
        categories_data['# 更新时间'] = timestamp
        tags_data['# 更新时间'] = timestamp
        manifest_data['# 更新时间'] = timestamp
        
        # 写回索引
        write_yaml_file(categories_file, categories_data)
        write_yaml_file(tags_file, tags_data)
        write_yaml_file(manifest_file, manifest_data)
        
        print('✓ 索引更新完成')
        
        # 6. Git提交
        print('📦 提交到Git...')
        try:
            subprocess.run(['git', 'add', str(relative_path), '_index/'], 
                          cwd=KB_ROOT, check=True, capture_output=True)
            commit_msg = f"添加笔记: {title}\n\n- 分类: {category}\n- 标签: {', '.join(tags)}"
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                          cwd=KB_ROOT, check=True, capture_output=True)
            print('✓ Git提交成功')
        except subprocess.CalledProcessError as e:
            print(f'⚠ Git提交失败: {e}')
        
        print('\n✅ 笔记添加完成!')
        print(f'📍 位置: {relative_path}')
        
    except Exception as e:
        print(f'❌ 错误: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
