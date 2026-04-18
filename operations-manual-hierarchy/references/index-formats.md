## 索引文件格式

### 一级索引 `operations_manual/hierarchy/index.md`

```markdown
# 工作手册一级索引

> 最后更新：<YYYY-MM-DD HH:MM>
> 总一级分类数：<N>

## 分类映射表

| 一级分类名称 | 概要 | 目录名 | 二级分类数 | 条目总数 | 创建时间 | 最后更新 |
|---------|------|--------|---------|---------|---------|---------|
| 技术规程 | 记录开发与系统工程相关规程、最佳实践、排错手册与常用脚本。 | category_a1b2c3d4 | 3 | 12 | 2026-02-26 | 2026-02-26 |
| 日常运营 | 记录日常协作流程、会议纪要模板、SOP与跨团队沟通要点。 | category_e5f6g7h8 | 2 | 5  | 2026-02-26 | 2026-02-26 |
```

### 二级索引 `operations_manual/hierarchy/category_<ID>/index.md`

```markdown
# <一级分类名称> - 二级索引

> 所属一级分类：<一级分类名称>
> 最后更新：<YYYY-MM-DD HH:MM>
> 总二级分类数：<N>

## 二级分类映射表

| 二级分类名称 | 概要 | 目录名 | 条目数 | 创建时间 | 最后更新 |
|-----------|------|--------|-------|---------|---------|
| Python编程 | 收录 Python 语言用法、工程化实践、常见坑位与可复用代码片段。 | subcategory_i9j0k1l2 | 4 | 2026-02-26 | 2026-02-26 |
| 系统设计   | 收录架构决策记录、模块拆分思路、容量评估与关键权衡说明。 | subcategory_m3n4o5p6 | 2 | 2026-02-26 | 2026-02-26 |
```

### 三级索引 `operations_manual/hierarchy/category_<ID>/subcategory_<ID>/index.md`

```markdown
# <二级分类名称> - 条目索引

> 所属路径：<一级分类> > <二级分类>
> 最后更新：<YYYY-MM-DD HH:MM>
> 条目总数：<N>

## 条目清单

| ID | 标题 | 概要 | 重要度 | 标签 | 创建时间 |
|----|------|------|-------|------|---------|
| entry_a1b2c3d4 | Python异步编程注意事项 | 涵盖async/await协程定义、运行入口、阻塞操作包装与异常处理等5个核心要点。 | ⭐⭐⭐ | Python, 异步编程 | 2026-04-02 |
| entry_e5f6g7h8 | Django REST Framework配置 | 记录DRF项目的Serializer、ViewSet、Router配置最佳实践与常见坑位。 | ⭐⭐⭐⭐⭐ | Python, Django, API | 2026-04-02 |
```

**三级索引是 Agent 了解每个条目内容的主要入口**，通过读取该文件即可判断是否需要打开具体条目，避免盲读所有 entry 文件。

### 概要字段规范（一/二/三级索引通用）

- 目标：让 Agent 仅通过读取索引即可判断该目录大概包含什么，从而决定是否继续读取下钻目录或条目文件。
- 形态：1 句话为主，30–60 字，优先写"通常包含什么/解决什么问题/典型主题关键词或条目形态"。
- 生成与更新（混合策略）：
  - 默认自动聚合：从该分类下条目标题、tags、条目内语义摘要抽样归纳生成。
  - 置信度低才追问用户：例如条目数过少、主题过散、或自动结果仅能给出"杂项/其他/通用"等泛化描述时，向用户只问 1 句概要并写入索引。
  - 稳定优先：无需每次写入都重写概要；仅在概要为空、明显过泛或新增内容导致主题发生明显偏移时更新。

#### 三级索引概要专用规范

三级索引的「概要」列描述的是**单个条目**的内容摘要（区别于一/二级索引描述的是分类整体），需遵循以下额外规则：

- **形态**：1 句话为主，20–50 字，从条目 frontmatter 的 `title` + `tags` + 正文前 100 字中提炼核心信息
- **必须包含的信息维度**：条目解决什么问题 / 涵盖哪些关键要点 / 适用什么场景（至少覆盖其中 2 个维度）
- **生成时机**：写入条目时自动生成；更新条目时刷新对应行；无需全量重写其他行
- **示例对照**：

  | 条目标题 | 好的概要 | 不好的概要 |
  |---------|---------|-----------|
  | Python异步编程注意事项 | 涵盖async/await协程定义、运行入口、阻塞操作包装与异常处理等5个核心要点。 | 关于Python异步编程的一些注意事项。（太泛） |
  | Git Flow工作流规范 | 记录main/develop/feature分支模型、PR review流程与合并规范。 | Git相关内容。（无信息量） |

### 影子摘要库 `memory/operations_manual_shadow_index.md`

全局语义摘要索引，供 Agent 快速检索和定位条目文件。每条记录包含完整路径，Agent 可直接据此读取文件，无需逐层查索引。

```markdown
# 工作手册影子摘要库

> 总条目数：<N>
> 最后更新：<YYYY-MM-DD HH:MM>

### [ID: entry_a1b2c3d4] Python异步编程注意事项
- 📂 **归属**: 技术规程 > Python编程
- 📄 **路径**: operations_manual/hierarchy/category_a1b2c3d4/subcategory_i9j0k1l2/entry_a1b2c3d4.md
- 🏷️ **标签**: Python, 异步编程, asyncio
- 🧠 **语义摘要**: 本文记录了Python异步编程中async/await的5个核心使用注意事项：包括协程函数定义方式、await只能在async函数内使用的限制、asyncio.run()作为运行入口、用asyncio.to_thread()包装同步阻塞操作以避免事件循环阻塞，以及try/except异常处理与同步代码一致的规则。适用于Python后端开发和异步IO场景。

### [ID: entry_e5f6g7h8] Django REST Framework配置
- 📂 **归属**: 技术规程 > Python编程
- 📄 **路径**: operations_manual/hierarchy/category_a1b2c3d4/subcategory_i9j0k1l2/entry_e5f6g7h8.md
- 🏷️ **标签**: Python, Django, API
- 🧠 **语义摘要**: 本条目系统整理了Django REST Framework项目的配置最佳实践，涵盖Serializer定义、ViewSet视图集配置、Router路由注册等核心模块的常见用法与坑位规避。适用于DRF API项目的快速搭建与维护。
```

**字段说明：**

| 字段 | 说明 | 生成时机 |
|------|------|---------|
| ID | 条目唯一标识 | 写入条目时 |
| 标题 | 条目标题（≤20字） | 写入条目时 |
| 归属 | 一级分类 > 二级分类 | 写入条目时 |
| **路径** | **相对于 workspace 根目录的文件相对路径，格式：`operations_manual/hierarchy/{category_dir}/{subcategory_dir}/{entry_id}.md`** | **写入条目时，基于已知的 category_dir / subcategory_dir / entry_id 拼接** |
| 标签 | 逗号分隔的标签列表 | 写入条目时 |
| 语义摘要 | 100~200字纯自然语言业务摘要，包含核心作用、组成逻辑、高频检索特征 | 写入条目时由大模型生成 |

> ⚠️ **路径字段是 Agent 直接操作文件的唯一依据**。写入时必须携带正确的相对路径，格式为 `operations_manual/hierarchy/<category随机ID>/<subcategory随机ID>/<entry随机ID>.md`，确保 Agent 可直接通过此路径调用 Read 工具读取条目文件。

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
