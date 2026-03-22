#!/usr/bin/env node

/**
 * 知识库笔记添加脚本
 * 用法: node add-note.js <标题> <摘要> <标签> <分类> [源文件路径]
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// 配置
const KB_ROOT = path.resolve(__dirname, '../../../knowledge');
const INDEX_DIR = path.join(KB_ROOT, '_index');
const TEMPLATE_FILE = path.join(KB_ROOT, '_templates/default.md');

// 参数解析
const args = process.argv.slice(2);
if (args.length < 4) {
  console.error('用法: node add-note.js <标题> <摘要> <标签> <分类> [源文件路径]');
  console.error('示例: node add-note.js "标题" "摘要" "标签1,标签2" "分类/子分类" "/path/to/source.md"');
  process.exit(1);
}

const [title, aiSummary, tagsStr, category, sourceFile] = args;
const tags = tagsStr.split(',').map(t => t.trim()).filter(t => t);

// 工具函数
function getCurrentTimestamp() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, '');
}

function sanitizeFilename(str) {
  return str.replace(/[\/\\:*?"<>|]/g, '_');
}

function readYamlFile(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`文件不存在: ${filePath}`);
  }
  const content = fs.readFileSync(filePath, 'utf8');
  return yaml.load(content);
}

function writeYamlFile(filePath, data) {
  const yamlStr = yaml.dump(data, {
    indent: 2,
    lineWidth: -1,
    quotingType: '"',
    forceQuotes: false
  });
  fs.writeFileSync(filePath, yamlStr, 'utf8');
}

// 主逻辑
async function main() {
  try {
    console.log('📝 开始添加笔记...');
    
    // 1. 确定目标路径
    const categoryPath = category.split('/').join('/');
    const targetDir = path.join(KB_ROOT, categoryPath);
    const filename = sanitizeFilename(title) + '.md';
    const targetFile = path.join(targetDir, filename);
    const relativePath = path.relative(KB_ROOT, targetFile);
    
    console.log(`📂 目标路径: ${relativePath}`);
    
    // 2. 创建目录
    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
      console.log(`✓ 创建目录: ${categoryPath}`);
    }
    
    // 3. 处理笔记内容
    const timestamp = getCurrentTimestamp();
    let noteContent;
    
    if (sourceFile && fs.existsSync(sourceFile)) {
      console.log(`📄 复制源文件: ${sourceFile}`);
      const sourceContent = fs.readFileSync(sourceFile, 'utf8');
      
      // 检查源文件是否已有frontmatter
      const frontmatterMatch = sourceContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
      
      if (frontmatterMatch) {
        // 已有frontmatter，合并更新
        const existingFrontmatter = yaml.load(frontmatterMatch[1]);
        const mergedFrontmatter = {
          title: title,
          created: existingFrontmatter.created || timestamp,
          updated: timestamp,
          tags: tags,
          category: category,
          ai_summary: aiSummary,
          ...existingFrontmatter
        };
        noteContent = `---\n${yaml.dump(mergedFrontmatter)}---\n${frontmatterMatch[2]}`;
      } else {
        // 无frontmatter，添加frontmatter
        const frontmatter = {
          title: title,
          created: timestamp,
          updated: timestamp,
          tags: tags,
          category: category,
          ai_summary: aiSummary
        };
        noteContent = `---\n${yaml.dump(frontmatter)}---\n\n# ${title}\n\n${tags.map(t => `#${t}`).join(' ')}\n\n${sourceContent}`;
      }
    } else {
      // 无源文件，使用模板
      console.log('📝 使用模板创建笔记');
      const template = fs.existsSync(TEMPLATE_FILE) 
        ? fs.readFileSync(TEMPLATE_FILE, 'utf8')
        : `---
title: "{{title}}"
created: "{{created}}"
updated: "{{updated}}"
tags: {{tags}}
category: "{{category}}"
ai_summary: "{{ai_summary}}"
---

# {{title}}

{{content}}`;
      
      noteContent = template
        .replace(/\{\{title\}\}/g, title)
        .replace(/\{\{created\}\}/g, timestamp)
        .replace(/\{\{updated\}\}/g, timestamp)
        .replace(/\{\{tags\}\}/g, JSON.stringify(tags))
        .replace(/\{\{category\}\}/g, category)
        .replace(/\{\{ai_summary\}\}/g, aiSummary)
        .replace(/\{\{content\}\}/g, `${tags.map(t => `#${t}`).join(' ')}\n\n> ${aiSummary}`);
    }
    
    // 4. 写入笔记文件
    fs.writeFileSync(targetFile, noteContent, 'utf8');
    console.log(`✓ 笔记已创建: ${filename}`);
    
    // 5. 更新索引
    console.log('📑 更新索引...');
    
    // 5.1 读取现有索引
    const categoriesFile = path.join(INDEX_DIR, 'categories.yaml');
    const tagsFile = path.join(INDEX_DIR, 'tags.yaml');
    const manifestFile = path.join(INDEX_DIR, 'notes-manifest.yaml');
    
    const categoriesData = readYamlFile(categoriesFile);
    const tagsData = readYamlFile(tagsFile);
    const manifestData = readYamlFile(manifestFile);
    
    // 5.2 更新分类索引
    const categoryParts = category.split('/');
    let currentLevel = categoriesData.categories;
    for (let i = 0; i < categoryParts.length; i++) {
      const part = categoryParts[i];
      if (!currentLevel[part]) {
        currentLevel[part] = i === categoryParts.length - 1 ? { count: 0 } : {};
      }
      if (i === categoryParts.length - 1) {
        currentLevel[part].count = (currentLevel[part].count || 0) + 1;
      } else {
        if (!currentLevel[part] || typeof currentLevel[part].count === 'number') {
          currentLevel[part] = {};
        }
        currentLevel = currentLevel[part];
      }
    }
    
    // 5.3 更新标签索引
    if (!tagsData.tags) tagsData.tags = {};
    tags.forEach(tag => {
      if (!tagsData.tags[tag]) {
        tagsData.tags[tag] = [];
      }
      tagsData.tags[tag].push({
        path: relativePath,
        title: title
      });
    });
    
    // 5.4 更新笔记清单
    if (!manifestData.notes) manifestData.notes = [];
    const maxId = manifestData.notes.length > 0 
      ? Math.max(...manifestData.notes.map(n => parseInt(n.id))) 
      : 0;
    manifestData.notes.push({
      id: String(maxId + 1),
      title: title,
      path: relativePath,
      category: category,
      tags: tags,
      created: timestamp,
      updated: timestamp,
      ai_summary: aiSummary
    });
    
    // 5.5 更新时间戳
    categoriesData['# 更新时间'] = timestamp;
    tagsData['# 更新时间'] = timestamp;
    manifestData['# 更新时间'] = timestamp;
    
    // 5.6 写回索引文件
    writeYamlFile(categoriesFile, categoriesData);
    writeYamlFile(tagsFile, tagsData);
    writeYamlFile(manifestFile, manifestData);
    
    console.log('✓ 索引更新完成');
    
    // 6. Git提交
    console.log('📦 提交到Git...');
    const { execSync } = require('child_process');
    
    try {
      execSync(`git add "${relativePath}" _index/`, { cwd: KB_ROOT });
      const commitMsg = `添加笔记: ${title}\n\n- 分类: ${category}\n- 标签: ${tags.join(', ')}`;
      execSync(`git commit -m "${commitMsg}"`, { cwd: KB_ROOT });
      console.log('✓ Git提交成功');
    } catch (err) {
      console.warn('⚠ Git提交失败:', err.message);
    }
    
    console.log('\n✅ 笔记添加完成!');
    console.log(`📍 位置: ${relativePath}`);
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    process.exit(1);
  }
}

main();
