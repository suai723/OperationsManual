#!/usr/bin/env python3
"""
rebuild_hierarchy_index.py - 重建工作手册分级索引

扫描 operations_manual/hierarchy/ 下所有 entry_*.md，解析 YAML frontmatter，
生成稳定、确定性的一级索引、二级索引和二级分类目录索引（含概述区块）。

根目录解析优先级：
  1. --root 命令行参数
  2. OPERATIONS_MANUAL_HIERARCHY_ROOT 环境变量
  3. WORKSPACE 环境变量 + operations_manual/hierarchy
  4. 脚本位置推断（脚本所在仓库的 operations_manual/hierarchy）

仅依赖 Python 标准库。
"""

import argparse
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CATEGORY_RE = re.compile(r'^category_[a-z0-9]{8}$')
SUBCATEGORY_RE = re.compile(r'^subcategory_[a-z0-9]{8}$')
ENTRY_RE = re.compile(r'^entry_[a-z0-9]{8}\.md$')

SUMMARY_MAX_CHARS = 120
OVERVIEW_MAX_ENTRIES = 50
OVERVIEW_MAX_RECENT = 5
OVERVIEW_MAX_TAGS = 10


def parse_frontmatter(filepath):
    """从 Markdown 文件中解析 YAML frontmatter，返回 (dict, body_str)。"""
    content = filepath.read_text(encoding='utf-8')
    if not content.startswith('---'):
        return {}, content

    end = content.find('---', 3)
    if end == -1:
        return {}, content

    fm_text = content[3:end].strip()
    body = content[end + 3:].strip()

    meta = {}
    for line in fm_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' not in line:
            continue
        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()
        if value.startswith('[') and value.endswith(']'):
            items = [i.strip().strip('"').strip("'") for i in value[1:-1].split(',')]
            meta[key] = [i for i in items if i]
        else:
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            meta[key] = value

    return meta, body


def extract_summary(meta, body, max_chars=SUMMARY_MAX_CHARS):
    """从 frontmatter 或正文中提取单行概述。"""
    for field in ('summary', 'brief'):
        if field in meta and meta[field]:
            text = str(meta[field])
            return text[:max_chars] if len(text) > max_chars else text

    content_match = re.search(
        r'^##\s*内容\s*\n(.*?)(?=^##|\Z)', body, re.MULTILINE | re.DOTALL
    )
    text = content_match.group(1) if content_match else body

    text = re.sub(r'[#*`\[\]()>_~]', '', text)
    text = re.sub(r'\n+', ' ', text).strip()

    if not text:
        return ''
    if len(text) > max_chars:
        text = text[:max_chars - 1] + '…'
    return text


def format_date(dt_str):
    """保持日期字符串格式不变，仅做基本清理。"""
    return str(dt_str).strip() if dt_str else ''


def min_date(dates):
    valid = sorted(d for d in dates if d)
    return valid[0] if valid else ''


def max_date(dates):
    valid = sorted(d for d in dates if d)
    return valid[-1] if valid else ''


def top_tags(tags, n=OVERVIEW_MAX_TAGS):
    return [t for t, _ in Counter(tags).most_common(n)]


def scan_hierarchy(root):
    """扫描整个分级目录树，返回按目录名排序的分类字典。"""
    root = Path(root)
    categories = {}

    for cat_dir in sorted(root.iterdir()):
        if not cat_dir.is_dir() or not CATEGORY_RE.match(cat_dir.name):
            continue

        cat = {
            'dir_name': cat_dir.name,
            'name': None,
            'subcategories': {},
            'all_entries': [],
            'all_tags': [],
        }

        for sub_dir in sorted(cat_dir.iterdir()):
            if not sub_dir.is_dir() or not SUBCATEGORY_RE.match(sub_dir.name):
                continue

            sub = {
                'dir_name': sub_dir.name,
                'name': None,
                'entries': [],
            }

            for entry_file in sorted(sub_dir.iterdir()):
                if not entry_file.is_file() or not ENTRY_RE.match(entry_file.name):
                    continue

                meta, body = parse_frontmatter(entry_file)
                entry = {
                    'id': meta.get('id', entry_file.stem),
                    'title': meta.get('title', ''),
                    'category': meta.get('category', ''),
                    'subcategory': meta.get('subcategory', ''),
                    'tags': meta.get('tags', []),
                    'created': format_date(meta.get('created', '')),
                    'updated': format_date(meta.get('updated', '')),
                    'importance': meta.get('importance', ''),
                    'summary': extract_summary(meta, body),
                    'filename': entry_file.name,
                }

                sub['entries'].append(entry)
                cat['all_entries'].append(entry)

                if isinstance(entry['tags'], list):
                    cat['all_tags'].extend(entry['tags'])

                if not sub['name'] and entry['subcategory']:
                    sub['name'] = entry['subcategory']
                if not cat['name'] and entry['category']:
                    cat['name'] = entry['category']

            cat['subcategories'][sub_dir.name] = sub

        categories[cat_dir.name] = cat

    return categories


def generate_root_index(categories, last_update):
    """生成根级 index.md 全文——单表含所有条目与相对路径。"""
    total_cats = len(categories)
    total_entries = sum(len(c['all_entries']) for c in categories.values())
    total_subs = sum(len(c['subcategories']) for c in categories.values())

    lines = [
        '# 工作手册一级索引',
        '',
        f'> 最后更新：{last_update}',
        f'> 一级分类数：{total_cats} | 二级分类数：{total_subs} | 条目总数：{total_entries}',
        '',
        '## 全库条目总表',
        '',
        '| 一级分类 | 二级分类 | 条目ID | 标题 | 相对路径 | 重要性 | 创建时间 | 最后更新 | 概述 |',
        '|---------|---------|--------|------|---------|--------|---------|---------|------|',
    ]

    count = 0
    for dir_name in sorted(categories):
        cat = categories[dir_name]
        cat_name = cat['name'] or dir_name
        for sub_dir in sorted(cat['subcategories']):
            sub = cat['subcategories'][sub_dir]
            sub_name = sub['name'] or sub_dir
            for e in sub['entries']:
                if count >= OVERVIEW_MAX_ENTRIES:
                    lines.append(f'| ... | ... | ... | ... | ... | ... | ... | ... | 共 {total_entries} 条，其余见各 category 索引 |')
                    break
                rel_path = f'{dir_name}/{sub_dir}/{e["filename"]}'
                summary = e['summary'].replace('|', '\\|')
                importance = e.get('importance', '')
                lines.append(
                    f'| {cat_name} | {sub_name} | {e["id"]} | {e["title"]} '
                    f'| {rel_path} | {importance} | {e["created"]} | {e["updated"]} | {summary} |'
                )
                count += 1
            else:
                continue
            break
        else:
            continue
        break

    lines += ['', '---', '']
    return '\n'.join(lines)


def generate_category_index(cat, last_update):
    """生成一级分类目录内的 index.md 全文——单表含所有条目与相对路径。"""
    cat_name = cat['name'] or cat['dir_name']
    cat_dir = cat['dir_name']
    total_entries = len(cat['all_entries'])
    total_subs = len(cat['subcategories'])

    lines = [
        f'# {cat_name} - 二级索引',
        '',
        f'> 所属一级分类：{cat_name}',
        f'> 最后更新：{last_update}',
        f'> 二级分类数：{total_subs} | 条目总数：{total_entries}',
        '',
        '## 条目总表',
        '',
        '| 二级分类 | 条目ID | 标题 | 相对路径 | 重要性 | 创建时间 | 最后更新 | 概述 |',
        '|---------|--------|------|---------|--------|---------|---------|------|',
    ]

    count = 0
    for sub_dir in sorted(cat['subcategories']):
        sub = cat['subcategories'][sub_dir]
        sub_name = sub['name'] or sub_dir
        for e in sub['entries']:
            if count >= OVERVIEW_MAX_ENTRIES:
                lines.append(
                    f'| ... | ... | ... | ... | ... | ... | ... '
                    f'| 共 {total_entries} 条，其余见 subcategory 索引 |'
                )
                break
            rel_path = f'{sub_dir}/{e["filename"]}'
            summary = e['summary'].replace('|', '\\|')
            importance = e.get('importance', '')
            lines.append(
                f'| {sub_name} | {e["id"]} | {e["title"]} '
                f'| {rel_path} | {importance} | {e["created"]} | {e["updated"]} | {summary} |'
            )
            count += 1
        else:
            continue
        break

    lines += ['', '---', '']
    return '\n'.join(lines)


def generate_subcategory_index(sub, cat_name, cat_dir_name, last_update):
    """生成二级分类目录内的 index.md 全文。"""
    sub_name = sub['name'] or sub['dir_name']
    sub_dir = sub['dir_name']
    entries = sub['entries']
    lines = [
        f'# {sub_name} - 条目索引',
        '',
        f'> 所属一级分类：{cat_name}',
        f'> 所属二级分类：{sub_name}',
        f'> 最后更新：{last_update}',
        f'> 条目数：{len(entries)}',
        '',
        '## 条目列表',
        '',
    ]

    if not entries:
        lines.append('尚无条目。')
    else:
        lines += [
            '| 条目ID | 标题 | 相对路径 | 重要性 | 创建时间 | 最后更新 | 概述 |',
            '|--------|------|---------|--------|---------|---------|------|',
        ]
        for e in entries[:OVERVIEW_MAX_ENTRIES]:
            summary = e['summary'].replace('|', '\\|')
            importance = e.get('importance', '')
            rel_path = f'{cat_dir_name}/{sub_dir}/{e["filename"]}'
            lines.append(
                f'| {e["id"]} | {e["title"]} | {rel_path} '
                f'| {importance} | {e["created"]} | {e["updated"]} | {summary} |'
            )
        if len(entries) > OVERVIEW_MAX_ENTRIES:
            lines.append(f'| ... | ... | ... | ... | ... | ... | 共 {len(entries)} 条 |')

    lines += ['', '---', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='重建工作手册分级索引')
    parser.add_argument(
        '--root', type=str, default=None,
        help='工作手册分级库根目录（默认从环境变量或脚本位置推断）'
    )
    args = parser.parse_args()

    root = args.root
    if root is None:
        root = os.environ.get('OPERATIONS_MANUAL_HIERARCHY_ROOT')
    if root is None:
        workspace = os.environ.get('WORKSPACE')
        if workspace:
            candidate = Path(workspace) / 'operations_manual' / 'hierarchy'
            if candidate.is_dir():
                root = str(candidate)
    if root is None:
        script_dir = Path(__file__).resolve().parent
        candidates = [
            script_dir.parent.parent / 'operations_manual' / 'hierarchy',
        ]
        for c in candidates:
            if c.is_dir():
                root = str(c)
                break

    if root is None:
        print(
            '错误：无法确定工作手册根目录。'
            '请通过 --root 参数或 OPERATIONS_MANUAL_HIERARCHY_ROOT 环境变量指定。',
            file=sys.stderr,
        )
        sys.exit(1)

    root_path = Path(root)
    if not root_path.is_dir():
        print(f'错误：指定的根目录不存在：{root}', file=sys.stderr)
        sys.exit(1)

    categories = scan_hierarchy(root_path)

    all_updated = [
        e['updated'] for cat in categories.values() for e in cat['all_entries'] if e['updated']
    ]
    global_last = max(all_updated) if all_updated else ''

    root_index = generate_root_index(categories, global_last)
    (root_path / 'index.md').write_text(root_index, encoding='utf-8')
    print(f'✅ 已更新一级索引：{root_path / "index.md"}')

    sub_index_count = 0
    for dir_name, cat in categories.items():
        cat_name = cat['name'] or dir_name
        cat_updated = max_date(e['updated'] for e in cat['all_entries'])
        cat_index = generate_category_index(cat, cat_updated or global_last)
        idx_path = root_path / dir_name / 'index.md'
        idx_path.write_text(cat_index, encoding='utf-8')
        print(f'✅ 已更新二级索引：{idx_path}')

        for sub_dir_name, sub in cat['subcategories'].items():
            sub_updated = max_date(e['updated'] for e in sub['entries'])
            sub_index = generate_subcategory_index(
                sub, cat_name, dir_name, sub_updated or cat_updated or global_last
            )
            sub_idx_path = root_path / dir_name / sub_dir_name / 'index.md'
            sub_idx_path.write_text(sub_index, encoding='utf-8')
            sub_index_count += 1
            print(f'✅ 已更新二级分类目录索引：{sub_idx_path}')

    total_entries = sum(len(c['all_entries']) for c in categories.values())
    total_subs = sum(len(c['subcategories']) for c in categories.values())
    print(f'\n📊 索引重建完成')
    print(f'├── 一级分类数：{len(categories)}')
    print(f'├── 二级分类数：{total_subs}')
    print(f'├── 条目总数：{total_entries}')
    print(f'├── 索引文件数：{1 + len(categories) + sub_index_count}')
    print(f'└── 最后更新：{global_last}')


if __name__ == '__main__':
    main()
