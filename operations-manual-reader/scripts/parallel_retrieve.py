#!/usr/bin/env python3
"""
parallel_retrieve.py - 工作手册多路并行检索脚本

索引路 / 元数据路 / 全文路以 concurrent.futures 线程池真并行执行，
输出 JSON 供 Agent 合并排序。仅依赖 Python 标准库。

用法:
  python parallel_retrieve.py --root <库根目录> --query "<用户查询>"
  python parallel_retrieve.py --root <库根目录> --query "<用户查询>" --json-only
"""

import argparse
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def parse_frontmatter(filepath: Path) -> dict:
    """解析 entry 的 YAML frontmatter，无 frontmatter 时返回 yaml_absent 标记。"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {"yaml_absent": True, "error": "read_failed"}

    if not text.startswith("---"):
        return {"yaml_absent": True}

    end = text.find("---", 3)
    if end == -1:
        return {"yaml_absent": True}

    fm_text = text[3:end].strip()
    result = {"yaml_absent": False}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key in ("title", "summary", "category", "subcategory", "importance", "id"):
            result[key] = val
        elif key == "tags":
            tags = re.findall(r"[\w\u4e00-\u9fff]+", val)
            result["tags"] = tags
    return result


def search_index_files(root: Path, query: str) -> list:
    """索引路：在各级 index.md 中 grep 关键词。"""
    hits = []
    keywords = query.lower().split()
    if not keywords:
        return hits

    for index_path in root.rglob("index.md"):
        try:
            content = index_path.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = str(index_path.relative_to(root))
        for i, line in enumerate(content.splitlines(), 1):
            line_lower = line.lower()
            matched = [kw for kw in keywords if kw in line_lower]
            if matched:
                entry_ids = re.findall(r"entry_[a-z0-9]{8}", line)
                cat_ids = re.findall(r"category_[a-z0-9]{8}", line)
                hits.append({
                    "lane": "index",
                    "file": rel,
                    "line_num": i,
                    "line": line.strip()[:200],
                    "matched_keywords": matched,
                    "entry_ids": entry_ids,
                    "category_ids": cat_ids,
                })
    return hits


def search_metadata(root: Path, query: str) -> list:
    """元数据路：解析 entry frontmatter 并匹配。"""
    hits = []
    keywords = query.lower().split()
    if not keywords:
        return hits

    for entry_path in root.rglob("entry_*.md"):
        rel = str(entry_path.relative_to(root))
        fm = parse_frontmatter(entry_path)
        fm["file"] = rel
        fm["lane"] = "metadata"

        if fm.get("yaml_absent"):
            fm["matched_keywords"] = []
            hits.append(fm)
            continue

        searchable = " ".join([
            fm.get("title", ""),
            fm.get("summary", ""),
            " ".join(fm.get("tags", [])),
            fm.get("category", ""),
            fm.get("subcategory", ""),
        ]).lower()

        matched = [kw for kw in keywords if kw in searchable]
        if matched:
            fm["matched_keywords"] = matched
            hits.append(fm)
    return hits


def search_fulltext(root: Path, query: str) -> list:
    """全文路：对 entry 正文做受控 grep。"""
    hits = []
    keywords = query.lower().split()
    if not keywords:
        return hits

    for entry_path in root.rglob("entry_*.md"):
        try:
            content = entry_path.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = str(entry_path.relative_to(root))
        content_lower = content.lower()
        matched = [kw for kw in keywords if kw in content_lower]
        if matched:
            snippet_lines = []
            for line in content.splitlines():
                if any(kw in line.lower() for kw in matched):
                    snippet_lines.append(line.strip()[:200])
                    if len(snippet_lines) >= 3:
                        break
            hits.append({
                "lane": "fulltext",
                "file": rel,
                "matched_keywords": matched,
                "snippets": snippet_lines,
            })
    return hits


def main():
    parser = argparse.ArgumentParser(description="工作手册多路并行检索")
    parser.add_argument("--root", required=True, help="工作手册库根目录")
    parser.add_argument("--query", required=True, help="用户查询")
    parser.add_argument("--json-only", action="store_true", help="仅输出 JSON，不打印摘要")
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        result = {
            "error": "root_not_found",
            "message": f"库根目录不存在: {root}",
            "index_hits": [],
            "metadata_hits": [],
            "fulltext_hits": [],
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(search_index_files, root, args.query): "index_hits",
            executor.submit(search_metadata, root, args.query): "metadata_hits",
            executor.submit(search_fulltext, root, args.query): "fulltext_hits",
        }
        for future in as_completed(futures):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = [{"error": str(e)}]

    output = {
        "query": args.query,
        "root": str(root),
        "index_hits": results.get("index_hits", []),
        "metadata_hits": results.get("metadata_hits", []),
        "fulltext_hits": results.get("fulltext_hits", []),
        "total_hits": (
            len(results.get("index_hits", []))
            + len([h for h in results.get("metadata_hits", []) if h.get("matched_keywords")])
            + len(results.get("fulltext_hits", []))
        ),
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
