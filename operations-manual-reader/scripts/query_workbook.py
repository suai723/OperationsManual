#!/usr/bin/env python3
"""
工作手册查询工具
用于查询、浏览、搜索工作手册中已存储的知识条目
支持按分类浏览、关键词搜索、条目ID直读、标签过滤、关联条目追踪等多种检索模式
"""

import os
import re
import yaml
import frontmatter
from pathlib import Path

# 配置文件路径
CONFIG_PATH = Path(__file__).parent.parent / "config.yml"

# 加载配置
def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config

# 获取工作手册根目录
def get_workbook_root():
    config = load_config()
    return Path(config["workbook"]["root_dir"])

# 读取索引文件
def read_index_file(index_path):
    if not index_path.exists():
        return None
    
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

# 解析一级索引（大分类）
def parse_category_index():
    root_dir = get_workbook_root()
    index_path = root_dir / "index.md"
    
    if not index_path.exists():
        return None
    
    index_content = read_index_file(index_path)
    categories = []
    
    # 解析分类信息，只解析分类统计表
    # 格式：| Hive表元数据 | category_ewfvblzs | 6 | 38 | 2026-02-28 | 2026-02-28 |
    
    # 找到分类统计表的开始位置
    category_table_start = index_content.find("## 分类统计")
    if category_table_start == -1:
        return None
        
    # 找到表格的结束位置：在"## 分类统计"之后找到第一个"## "或者"---"
    # 先尝试找到下一个标题
    category_table_end = index_content.find("## ", category_table_start + len("## 分类统计"))
    if category_table_end == -1:
        # 如果没有下一个标题，找到文档结尾
        category_table_end = len(index_content)
        
    # 提取分类统计表内容
    category_table_content = index_content[category_table_start:category_table_end]
    
    category_lines = category_table_content.split("\n")
    for line in category_lines:
        if "category_" in line and "|" in line:
            parts = line.strip().split("|")
            if len(parts) >= 6:
                category_name = parts[1].strip()
                category_dir = parts[2].strip()
                subcategory_count = int(parts[3].strip())
                entry_count = int(parts[4].strip())
                update_time = parts[6].strip()
                
                categories.append({
                    "dir": category_dir,
                    "name": category_name,
                    "update_time": update_time,
                    "subcategory_count": subcategory_count,
                    "entry_count": entry_count
                })
    
    return categories

# 解析二级索引（小分类）
def parse_subcategory_index(category_dir):
    root_dir = get_workbook_root()
    category_path = root_dir / category_dir
    index_path = category_path / "index.md"
    
    if not index_path.exists():
        return None
    
    index_content = read_index_file(index_path)
    subcategories = []
    
    # 解析小分类信息
    # 格式：| subcategory_def5678 | 数据库 | 2026-02-26 10:30:00 | 5 |
    
    subcategory_lines = index_content.split("\n")
    for line in subcategory_lines:
        if "subcategory_" in line and "|" in line:
            parts = line.strip().split("|")
            if len(parts) >= 4:
                subcategory_dir = parts[1].strip()
                subcategory_name = parts[2].strip()
                update_time = parts[3].strip()
                entry_count = int(parts[4].strip())
                
                subcategories.append({
                    "dir": subcategory_dir,
                    "name": subcategory_name,
                    "update_time": update_time,
                    "entry_count": entry_count
                })
    
    return subcategories

# 读取条目文件
def read_entry_file(entry_path):
    if not entry_path.exists():
        return None
    
    try:
        with open(entry_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
        return post
    except Exception as e:
        print(f"Error reading entry file: {e}")
        return None

# 查询条目
def query_entries(category_dir=None, subcategory_dir=None, entry_id=None):
    root_dir = get_workbook_root()
    entries = []
    
    if entry_id:
        # 按条目ID查询
        entry_file = f"entry_{entry_id}.md"
        entry_paths = root_dir.rglob(entry_file)
        for entry_path in entry_paths:
            entry = read_entry_file(entry_path)
            if entry:
                entries.append(entry)
    else:
        # 按分类查询
        search_path = root_dir
        
        if category_dir:
            search_path = search_path / category_dir
            
        if subcategory_dir:
            search_path = search_path / subcategory_dir
            
        entry_files = search_path.rglob("entry_*.md")
        
        for entry_file in entry_files:
            entry = read_entry_file(entry_file)
            if entry:
                entries.append(entry)
    
    return entries

# 关键词搜索
def search_entries(keyword):
    root_dir = get_workbook_root()
    entries = []
    
    # 遍历所有条目文件
    entry_files = root_dir.rglob("entry_*.md")
    
    for entry_file in entry_files:
        entry = read_entry_file(entry_file)
        if entry:
            # 检查标题、标签、内容是否包含关键词
            title_match = keyword.lower() in entry["title"].lower()
            tags_match = any(keyword.lower() in tag.lower() for tag in entry.get("tags", []))
            content_match = keyword.lower() in entry.content.lower()
            
            if title_match or tags_match or content_match:
                # 从文件名中提取条目ID
                filename = entry_file.name
                if filename.startswith("entry_") and filename.endswith(".md"):
                    entry_id = filename[len("entry_"):-len(".md")]
                    entry["id"] = entry_id
                
                # 尝试从路径中提取分类信息
                parts = str(entry_file).split(os.sep)
                category = ""
                subcategory = ""
                
                # 查找 category 和 subcategory
                for i, part in enumerate(parts):
                    if part.startswith("category_"):
                        category = part
                    if part.startswith("subcategory_"):
                        subcategory = part
                
                entry["category"] = category
                entry["subcategory"] = subcategory
                
                entries.append(entry)
    
    return entries

# 标签过滤
def filter_entries_by_tags(tags):
    root_dir = get_workbook_root()
    entries = []
    
    # 遍历所有条目文件
    entry_files = root_dir.rglob("entry_*.md")
    
    for entry_file in entry_files:
        entry = read_entry_file(entry_file)
        if entry:
            entry_tags = entry.get("tags", [])
            # 检查是否包含所有指定标签
            if all(tag in entry_tags for tag in tags):
                entries.append(entry)
    
    return entries

# 统计条目数量
def count_entries():
    root_dir = get_workbook_root()
    entry_files = list(root_dir.rglob("entry_*.md"))
    return len(entry_files)

# 统计分类信息
def count_categories():
    categories = parse_category_index()
    if not categories:
        return 0, 0
    
    subcategory_count = 0
    entry_count = 0
    
    for category in categories:
        subcategory_count += category["subcategory_count"]
        entry_count += category["entry_count"]
    
    return len(categories), subcategory_count, entry_count

# 获取条目详情
def get_entry_details(entry):
    # 重要度映射
    importance_map = {"高": 5, "中": 3, "低": 1}
    importance = entry.get("importance", "中")
    importance_score = importance_map.get(importance, 3)
    
    return {
        "title": entry["title"],
        "entry_id": entry["id"] if entry.get("id") else "-",
        "category": entry.get("category", "-"),
        "subcategory": entry.get("subcategory", "-"),
        "tags": entry.get("tags", []),
        "importance": importance_score,
        "created": entry.get("created_at", "-"),
        "updated": entry.get("updated_at", "-"),
        "source": entry.get("source", "-"),
        "content": entry.content,
        "related_entries": entry.get("related_entries", [])
    }

# 格式化输出条目信息
def format_entry_details(entry):
    details = get_entry_details(entry)
    
    # 生成星级
    stars = "⭐" * details["importance"]
    
    # 格式化标签
    tags_str = "、".join(details["tags"]) if details["tags"] else "-"
    
    # 格式化关联条目
    related_entries_str = "\n".join([f"- entry_{related_id}：{title}" for related_id, title in details["related_entries"]]) if details["related_entries"] else "-"
    
    # 输出格式
    output = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 {details["title"]}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆔  ID：entry_{details["entry_id"]}
📂  分类：{details["category"]} > {details["subcategory"]}
🏷️   标签：{tags_str}
⭐  重要度：{stars}
📅  创建：{details["created"]}  |  更新：{details["updated"]}
📎  来源：{details["source"]}

── 内容 ──────────────────────────────────
{details["content"]}

── 关联条目 ──────────────────────────────
{related_entries_str}

── 备注 ──────────────────────────────────
{entry.get("notes", "-")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return output

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="工作手册查询工具")
    parser.add_argument("action", choices=["list", "search", "read"], help="操作类型：list(列出分类), search(搜索), read(读取条目)")
    parser.add_argument("-k", "--keyword", help="搜索关键词")
    parser.add_argument("-i", "--entry-id", help="条目ID")
    parser.add_argument("-c", "--category", help="分类名称")
    
    args = parser.parse_args()
    
    if args.action == "list":
        categories = parse_category_index()
        if categories:
            print(f"📚 工作手册总览\n")
            print(f"📁 共 {len(categories)} 个大分类，{sum(cat['subcategory_count'] for cat in categories)} 个小分类，{sum(cat['entry_count'] for cat in categories)} 条条目\n")
            print("| 序号 | 大分类名称 | 小分类数 | 条目总数 | 最后更新 |")
            print("|-----|-----------|---------|---------|---------|")
            for i, category in enumerate(categories, 1):
                print(f"| {i} | {category['name']} | {category['subcategory_count']} | {category['entry_count']} | {category['update_time']} |")
        else:
            print("⚠️  工作手册库尚未初始化，未找到 operations_manual/hierarchy/index.md")
    elif args.action == "search":
        if args.keyword:
            results = search_entries(args.keyword)
            print(f"🔍 搜索「{args.keyword}」- 共找到 {len(results)} 条结果\n")
            
            for i, entry in enumerate(results, 1):
                details = get_entry_details(entry)
                stars = "⭐" * details["importance"]
                tags_str = "、".join(details["tags"]) if details["tags"] else "-"
                summary = details["content"][:80] + "..." if len(details["content"]) > 80 else details["content"]
                
                print(f"┌─────────────────────────────────────────────────────────────┐")
                print(f"│ {i}. {details['title']}                                 {stars}        │")
                print(f"│    📂 {details['category']} > {details['subcategory']}                                    │")
                print(f"│    🏷️  标签：{tags_str}                                    │")
                print(f"│    🆔 entry_{details['entry_id']} │ 更新：{details['updated']}                      │")
                print(f"│    📝 摘要：{summary}                                    │")
                print(f"└─────────────────────────────────────────────────────────────┘")
    elif args.action == "read":
        if args.entry_id:
            results = query_entries(entry_id=args.entry_id)
            if results:
                print(format_entry_details(results[0]))
            else:
                print(f"❌ 未找到条目 entry_{args.entry_id}")
