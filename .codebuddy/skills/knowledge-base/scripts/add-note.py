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

# 配置 - 自动探测知识库路径
SCRIPT_DIR = Path(__file__).parent

def find_kb_root():
    """自动探测知识库数据目录"""
    # 1. 环境变量
    env_path = os.environ.get('KB_DATA_PATH')
    if env_path and Path(env_path, '.kb-config.yaml').exists():
        return Path(env_path).resolve()
    
    # 2. 从脚本位置向上探测（最多6级）
    probe = SCRIPT_DIR
    for _ in range(6):
        probe = probe.parent
        candidate = probe / 'data'
        if (candidate / '.kb-config.yaml').exists():
            return candidate.resolve()
    
    # 3. 家目录默认位置
    home_kb = Path.home() / 'knowledge' / 'data'
    if (home_kb / '.kb-config.yaml').exists():
        return home_kb

    return None

KB_ROOT = find_kb_root()
if not KB_ROOT:
    print("❌ 找不到知识库数据目录")
    print("提示: 请确保知识库已初始化（包含 .kb-config.yaml 文件）")
    print("     或设置环境变量: export KB_DATA_PATH=/path/to/knowledge/data")
    sys.exit(1)

INDEX_DIR = KB_ROOT / '_index'
TEMPLATE_FILE = KB_ROOT / '_templates' / 'default.md'

print(f'📍 知识库路径: {KB_ROOT}')

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
            commit_msg = f"📝 新增笔记: {title}\n\n- 分类: {category}\n- 标签: {', '.join(tags)}"
            subprocess.run(['git', 'commit', '-m', commit_msg], 
                          cwd=KB_ROOT, check=True, capture_output=True)
            print('✓ Git提交成功')
            
            # 7. 检查是否需要自动推送
            try:
                # 读取配置文件获取push_threshold
                config_file = KB_ROOT / '.kb-config.yaml'
                config_data = read_yaml_file(config_file)
                push_threshold = config_data.get('git', {}).get('push_threshold', 10)
                auto_pull = config_data.get('git', {}).get('auto_pull_before_push', True)
                
                # 获取未推送的提交数
                result = subprocess.run(['git', 'log', '@{u}..', '--oneline'], 
                                      cwd=KB_ROOT, capture_output=True, text=True)
                unpushed_count = len([line for line in result.stdout.strip().split('\n') if line])
                
                print(f'📊 当前进度: {unpushed_count} 个未推送提交 (阈值: {push_threshold})')
                
                if unpushed_count >= push_threshold:
                    print(f'📤 达到推送阈值，开始推送到远程...')
                    
                    # 先拉取（如果配置了auto_pull_before_push）
                    if auto_pull:
                        try:
                            subprocess.run(['git', 'pull', '--rebase'], 
                                         cwd=KB_ROOT, check=True, capture_output=True)
                            print('✓ 远程更新已拉取')
                        except subprocess.CalledProcessError:
                            print('⚠️ 拉取远程更新失败（可能是新仓库或无远程）')
                    
                    # 推送
                    try:
                        subprocess.run(['git', 'push'], 
                                     cwd=KB_ROOT, check=True, capture_output=True)
                        print('✓ 推送成功!')
                    except subprocess.CalledProcessError as e:
                        print(f'⚠️ 推送失败: {e.stderr.decode() if e.stderr else str(e)}')
                        print(f'   提示: 可以稍后手动运行 "git push" 推送')
                        
            except Exception as e:
                print(f'⚠️ 自动推送检查失败: {e}')
                
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
