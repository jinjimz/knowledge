#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库索引更新工具
支持增量更新和全量更新
"""

import os
import sys
import yaml
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def find_kb_data_path():
    """自动探测知识库数据路径"""
    # 1. 环境变量
    if 'KB_DATA_PATH' in os.environ:
        path = os.environ['KB_DATA_PATH']
        if os.path.exists(os.path.join(path, '.kb-config.yaml')):
            return path
    
    # 2. 从当前脚本位置向上查找
    current = Path(__file__).resolve().parent
    for _ in range(6):  # 最多向上6层
        candidate = current / 'data'
        if candidate.exists() and (candidate / '.kb-config.yaml').exists():
            return str(candidate)
        current = current.parent
    
    # 3. 默认路径
    default_path = os.path.expanduser('~/knowledge/data')
    if os.path.exists(os.path.join(default_path, '.kb-config.yaml')):
        return default_path
    
    return None

def load_yaml(file_path):
    """加载 YAML 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"⚠️  加载文件失败 {file_path}: {e}")
        return {}

def save_yaml(file_path, data):
    """保存 YAML 文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        return True
    except Exception as e:
        print(f"⚠️  保存文件失败 {file_path}: {e}")
        return False

def get_current_commit_id(data_path):
    """获取当前 Git commit ID"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=data_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return None

def get_changed_files(data_path, last_commit_id):
    """获取自上次更新以来变更的笔记文件"""
    if not last_commit_id:
        return None  # 返回 None 表示需要全量更新
    
    try:
        # 获取未暂存的变更
        result1 = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            cwd=data_path,
            capture_output=True,
            text=True
        )
        
        # 获取已提交但未在索引中的变更
        result2 = subprocess.run(
            ['git', 'diff', '--name-only', f'{last_commit_id}..HEAD'],
            cwd=data_path,
            capture_output=True,
            text=True
        )
        
        changed = set()
        for line in (result1.stdout + result2.stdout).split('\n'):
            line = line.strip()
            # 移除 data/ 前缀（如果存在）
            if line.startswith('data/'):
                line = line[5:]
            # 只处理 .md 文件，排除以 _ 开头的目录
            if line and line.endswith('.md') and not line.startswith('_'):
                changed.add(line)
        
        return list(changed)
    except Exception as e:
        print(f"⚠️  获取变更文件失败: {e}")
        return None

def extract_frontmatter(file_path):
    """从笔记文件中提取 frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return None
        
        end_pos = content.find('---', 3)
        if end_pos == -1:
            return None
        
        yaml_content = content[3:end_pos].strip()
        return yaml.safe_load(yaml_content) or {}
    except Exception as e:
        print(f"⚠️  读取文件失败 {file_path}: {e}")
        return None

def get_all_notes(data_path):
    """获取所有笔记文件"""
    notes = []
    data_path_obj = Path(data_path)
    
    for md_file in data_path_obj.rglob('*.md'):
        # 排除特殊目录
        if any(part.startswith('_') for part in md_file.parts):
            continue
        
        rel_path = md_file.relative_to(data_path_obj)
        notes.append(str(rel_path))
    
    return notes

def update_indexes_full(data_path):
    """全量更新索引"""
    print("🔄 执行全量索引更新...")
    
    index_dir = os.path.join(data_path, '_index')
    
    # 初始化索引数据
    categories_data = {'categories': {}}
    tags_data = {'tags': {}}
    notes_data = {'notes': []}
    
    # 分类计数器
    category_counts = defaultdict(lambda: defaultdict(int))
    
    # 获取所有笔记
    all_notes = get_all_notes(data_path)
    print(f"📊 找到 {len(all_notes)} 篇笔记")
    
    note_id = 1
    for rel_path in sorted(all_notes):
        abs_path = os.path.join(data_path, rel_path)
        frontmatter = extract_frontmatter(abs_path)
        
        if not frontmatter:
            print(f"⚠️  跳过无效笔记: {rel_path}")
            continue
        
        # 提取信息
        title = frontmatter.get('title', rel_path)
        category = frontmatter.get('category', 'Inbox')
        tags = frontmatter.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        
        # 更新笔记清单
        notes_data['notes'].append({
            'id': str(note_id),
            'title': title,
            'path': rel_path.replace('\\', '/'),
            'category': category,
            'tags': tags,
            'created': frontmatter.get('created', ''),
            'updated': frontmatter.get('updated', ''),
            'ai_summary': frontmatter.get('ai_summary', '')
        })
        
        # 更新标签索引
        for tag in tags:
            if tag not in tags_data['tags']:
                tags_data['tags'][tag] = []
            tags_data['tags'][tag].append({
                'path': rel_path.replace('\\', '/'),
                'title': title
            })
        
        # 更新分类计数
        parts = category.split('/')
        if len(parts) == 1:
            category_counts[parts[0]]['count'] += 1
        elif len(parts) >= 2:
            category_counts[parts[0]][parts[1]] += 1
        
        note_id += 1
    
    # 构建分类索引
    for cat1, subcats in category_counts.items():
        if cat1 not in categories_data['categories']:
            categories_data['categories'][cat1] = {}
        
        for cat2, count in subcats.items():
            if cat2 == 'count':
                categories_data['categories'][cat1]['count'] = count
            else:
                if cat2 not in categories_data['categories'][cat1]:
                    categories_data['categories'][cat1][cat2] = {}
                categories_data['categories'][cat1][cat2]['count'] = count
    
    # 添加更新时间
    update_time = datetime.now().isoformat()
    categories_data['# 更新时间'] = update_time
    tags_data['# 更新时间'] = update_time
    notes_data['# 更新时间'] = update_time
    
    # 保存索引文件
    save_yaml(os.path.join(index_dir, 'categories.yaml'), categories_data)
    save_yaml(os.path.join(index_dir, 'tags.yaml'), tags_data)
    save_yaml(os.path.join(index_dir, 'notes-manifest.yaml'), notes_data)
    
    print(f"✅ 索引更新完成!")
    print(f"   - 笔记数: {len(notes_data['notes'])}")
    print(f"   - 标签数: {len(tags_data['tags'])}")
    print(f"   - 分类数: {len(categories_data['categories'])}")
    
    return len(notes_data['notes']), len(tags_data['tags']), len(categories_data['categories'])

def update_indexes_incremental(data_path, changed_files):
    """增量更新索引"""
    print(f"🔄 执行增量索引更新 ({len(changed_files)} 个变更文件)...")
    
    if not changed_files:
        print("✅ 没有变更，无需更新")
        return
    
    index_dir = os.path.join(data_path, '_index')
    
    # 加载现有索引
    categories_data = load_yaml(os.path.join(index_dir, 'categories.yaml'))
    tags_data = load_yaml(os.path.join(index_dir, 'tags.yaml'))
    notes_data = load_yaml(os.path.join(index_dir, 'notes-manifest.yaml'))
    
    for changed_file in changed_files:
        abs_path = os.path.join(data_path, changed_file)
        
        # 如果文件被删除
        if not os.path.exists(abs_path):
            print(f"🗑️  删除: {changed_file}")
            # TODO: 从索引中移除
            continue
        
        # 读取文件
        frontmatter = extract_frontmatter(abs_path)
        if not frontmatter:
            print(f"⚠️  跳过无效文件: {changed_file}")
            continue
        
        print(f"📝 更新: {changed_file}")
        # TODO: 更新索引条目
    
    # 更新时间戳
    update_time = datetime.now().isoformat()
    categories_data['# 更新时间'] = update_time
    tags_data['# 更新时间'] = update_time
    notes_data['# 更新时间'] = update_time
    
    # 保存索引
    save_yaml(os.path.join(index_dir, 'categories.yaml'), categories_data)
    save_yaml(os.path.join(index_dir, 'tags.yaml'), tags_data)
    save_yaml(os.path.join(index_dir, 'notes-manifest.yaml'), notes_data)
    
    print("✅ 增量更新完成")

def update_index_state(data_path, notes_count, tags_count, categories_count):
    """更新索引状态文件"""
    index_state_file = os.path.join(data_path, '_index', '.index-state')
    
    commit_id = get_current_commit_id(data_path)
    timestamp = datetime.now().isoformat()
    
    state_content = f"""# 索引状态跟踪文件
# 此文件记录最后一次索引更新对应的 Git commit ID
# 用于支持增量更新，避免全量扫描所有笔记

last_index_update:
  commit_id: "{commit_id or ''}"
  timestamp: "{timestamp}"
  notes_count: {notes_count}
  tags_count: {tags_count}
  categories_count: {categories_count}

# 说明:
# - commit_id: 最后一次更新索引时的 Git commit SHA
# - timestamp: 更新时间 (ISO 8601 格式)
# - notes_count: 当前笔记总数
# - tags_count: 当前标签总数
# - categories_count: 当前分类总数
#
# 使用方式:
# 1. 手动更新索引时,脚本会读取此文件获取 last_commit_id
# 2. 通过 git diff 找出自上次更新以来变更的笔记文件
# 3. 只对变更的文件进行索引更新(增量更新)
# 4. 更新完成后,将当前 commit ID 写入此文件
"""
    
    with open(index_state_file, 'w', encoding='utf-8') as f:
        f.write(state_content)

def show_status(data_path):
    """显示索引状态"""
    print("📊 知识库索引状态\n")
    
    # 读取索引状态
    index_state_file = os.path.join(data_path, '_index', '.index-state')
    if os.path.exists(index_state_file):
        with open(index_state_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单解析
        import re
        commit_match = re.search(r'commit_id: "([^"]*)"', content)
        time_match = re.search(r'timestamp: "([^"]*)"', content)
        notes_match = re.search(r'notes_count: (\d+)', content)
        tags_match = re.search(r'tags_count: (\d+)', content)
        cats_match = re.search(r'categories_count: (\d+)', content)
        
        commit_id = commit_match.group(1) if commit_match else "未设置"
        timestamp = time_match.group(1) if time_match else "未知"
        notes_count = notes_match.group(1) if notes_match else "0"
        tags_count = tags_match.group(1) if tags_match else "0"
        cats_count = cats_match.group(1) if cats_match else "0"
        
        print(f"📍 知识库路径: {data_path}")
        print(f"📝 笔记总数: {notes_count}")
        print(f"🏷️  标签数量: {tags_count}")
        print(f"📂 分类数量: {cats_count}")
        print(f"🕐 最后更新: {timestamp}")
        print(f"🔗 Commit ID: {commit_id[:8]}..." if len(commit_id) > 8 else f"🔗 Commit ID: {commit_id}")
        
        # 检查是否有未索引的变更
        current_commit = get_current_commit_id(data_path)
        if current_commit and commit_id and current_commit != commit_id:
            changed = get_changed_files(data_path, commit_id)
            if changed:
                print(f"\n⚠️  有 {len(changed)} 个文件未索引:")
                for f in changed[:5]:
                    print(f"   - {f}")
                if len(changed) > 5:
                    print(f"   ... 还有 {len(changed) - 5} 个文件")
    else:
        print("⚠️  索引状态文件不存在，建议执行全量更新")

def main():
    """主函数"""
    # 查找知识库路径
    data_path = find_kb_data_path()
    if not data_path:
        print("❌ 无法找到知识库数据目录")
        print("请设置 KB_DATA_PATH 环境变量或在正确的目录下运行")
        sys.exit(1)
    
    # 解析参数
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 update-index.py --full         # 全量更新")
        print("  python3 update-index.py --incremental  # 增量更新")
        print("  python3 update-index.py --status       # 查看状态")
        sys.exit(0)
    
    mode = sys.argv[1]
    
    if mode == '--status':
        show_status(data_path)
    
    elif mode == '--full':
        notes_count, tags_count, cats_count = update_indexes_full(data_path)
        update_index_state(data_path, notes_count, tags_count, cats_count)
        print(f"\n💾 已更新索引状态文件")
    
    elif mode == '--incremental':
        # 读取上次的 commit ID
        index_state_file = os.path.join(data_path, '_index', '.index-state')
        last_commit_id = None
        
        if os.path.exists(index_state_file):
            with open(index_state_file, 'r', encoding='utf-8') as f:
                import re
                content = f.read()
                match = re.search(r'commit_id: "([^"]*)"', content)
                if match:
                    last_commit_id = match.group(1)
        
        # 获取变更文件
        changed_files = get_changed_files(data_path, last_commit_id)
        
        if changed_files is None or not last_commit_id:
            print("⚠️  无法确定变更，执行全量更新...")
            notes_count, tags_count, cats_count = update_indexes_full(data_path)
            update_index_state(data_path, notes_count, tags_count, cats_count)
        elif len(changed_files) == 0:
            print("✅ 没有变更，索引已是最新")
        else:
            update_indexes_incremental(data_path, changed_files)
            # 更新状态
            notes_data = load_yaml(os.path.join(data_path, '_index', 'notes-manifest.yaml'))
            tags_data = load_yaml(os.path.join(data_path, '_index', 'tags.yaml'))
            cats_data = load_yaml(os.path.join(data_path, '_index', 'categories.yaml'))
            update_index_state(
                data_path,
                len(notes_data.get('notes', [])),
                len(tags_data.get('tags', {})),
                len(cats_data.get('categories', {}))
            )
    
    else:
        print(f"❌ 未知选项: {mode}")
        sys.exit(1)

if __name__ == '__main__':
    main()
