## 索引文件格式

> 所有 `index.md` 文件由 `scripts/rebuild_hierarchy_index.py` 脚本自动生成，禁止手动编辑映射表和概述章节。

### 一级索引 `{WORKSPACE}/operations_manual/hierarchy/index.md`

```markdown
# 工作手册一级索引

> 最后更新：<YYYY-MM-DD HH:MM>
> 一级分类数：2 | 二级分类数：5 | 条目总数：17

## 全库条目总表

| 一级分类 | 二级分类 | 条目ID | 标题 | 相对路径 | 重要性 | 创建时间 | 最后更新 | 概述 |
|---------|---------|--------|------|---------|--------|---------|---------|------|
| 技术规程 | Python编程 | entry_a1b2c3d4 | Python异步编程最佳实践 | category_a1b2c3d4/subcategory_i9j0k1l2/entry_a1b2c3d4.md | 5 | 2026-02-26 | 2026-02-26 | 介绍 asyncio 核心用法… |
| 日常运营 | 巡检管理 | entry_x1y2z3w4 | 每日设备巡检规程 | category_e5f6g7h8/subcategory_q1r2s3t4/entry_x1y2z3w4.md | 4 | 2026-02-26 | 2026-02-26 | 开班前设备点检流程… |

---
```

### 二级索引 `{WORKSPACE}/operations_manual/hierarchy/category_<ID>/index.md`

```markdown
# <一级分类名称> - 二级索引

> 所属一级分类：<一级分类名称>
> 最后更新：<YYYY-MM-DD HH:MM>
> 二级分类数：2 | 条目总数：6

## 条目总表

| 二级分类 | 条目ID | 标题 | 相对路径 | 重要性 | 创建时间 | 最后更新 | 概述 |
|---------|--------|------|---------|--------|---------|---------|------|
| Python编程 | entry_a1b2c3d4 | Python异步编程最佳实践 | subcategory_i9j0k1l2/entry_a1b2c3d4.md | 5 | 2026-02-26 | 2026-02-26 | 介绍 asyncio 核心用法… |
| Python编程 | entry_e5f6g7h8 | Django 部署指南 | subcategory_i9j0k1l2/entry_e5f6g7h8.md | 4 | 2026-02-26 | 2026-02-26 | 生产环境 Django 部署… |
| 系统设计 | entry_m3n4o5p6 | 微服务架构设计指南 | subcategory_m3n4o5p6/entry_m3n4o5p6.md | 5 | 2026-02-26 | 2026-02-26 | 微服务拆分原则… |

---
```

### 二级分类目录索引 `{WORKSPACE}/operations_manual/hierarchy/category_<ID>/subcategory_<ID>/index.md`

```markdown
# <二级分类名称> - 条目索引

> 所属一级分类：<一级分类名称>
> 所属二级分类：<二级分类名称>
> 最后更新：<YYYY-MM-DD HH:MM>
> 条目数：<N>

## 条目列表

| 条目ID | 标题 | 相对路径 | 重要性 | 创建时间 | 最后更新 | 概述 |
|--------|------|---------|--------|---------|---------|------|
| entry_a1b2c3d4 | Python异步编程最佳实践 | category_a1b2c3d4/subcategory_i9j0k1l2/entry_a1b2c3d4.md | 5 | 2026-02-26 | 2026-02-26 | 介绍 asyncio 核心用法… |
| entry_e5f6g7h8 | Django 部署指南 | category_a1b2c3d4/subcategory_i9j0k1l2/entry_e5f6g7h8.md | 4 | 2026-02-26 | 2026-02-26 | 生产环境 Django 部署… |

---
```

### 条目文件 `entry_<ID>.md`

```markdown
---
id: entry_<8位随机ID>
title: <条目标题，20字以内>
category: <一级分类名称>
subcategory: <二级分类名称>
tags: [标签1, 标签2, 标签3]
created: <YYYY-MM-DD HH:MM>
updated: <YYYY-MM-DD HH:MM>
importance: <1-5，5最重要>
source: <来源文档名（可选）>
source_url: <原始文档链接（可选）>
related: [entry_xxxxxxxx, entry_yyyyyyyy]  # 关联条目ID列表（可选）
replaces: <entry_旧ID>                      # 若本文件为旧版本更新，填写被替代的条目ID（可选）
summary: <50～120字单行概述（必填，由模型理解内容后撰写，脚本将原样写入索引概述区块）>
---

# <条目标题>

## 来源
- **文档**：<来源文档名>
- **链接**：<原始文档链接（若有）>

## 内容
<具体条目内容，保持原始信息完整，不得删减关键信息>

## 关联条目
- <关联条目文件ID及简述（如有）>

## 备注
<补充说明（可选）>
```

> **字段说明**：`category` 和 `subcategory` 字段名保持不变以兼容存量条目，语义上分别对应一级分类和二级分类。`summary` 为必填字段，由模型在创建条目时理解内容后撰写（50～120 字），重建脚本会将其原样纳入索引概述区块。若存量条目缺少此字段，脚本从「## 内容」正文截取首段（最多 120 字）兜底。
