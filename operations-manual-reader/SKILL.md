---
name: operations-manual-reader
description: 智能工作手册（Operations Manual）只读检索系统。当用户需要查询、浏览、搜索、定位工作手册中已存储的知识条目时必须使用本技能。支持精准 ID 直读、三级索引浏览、多路并行模糊检索（脚本驱动索引/元数据/全文三路真并行 + 可选向量语义路）和从根索引渐进式兜底。当用户提到「查工作手册」「在手册里找」「手册有没有XX」「读 entry_xxx」「列出分类」「按关键词找条目」「工作手册里关于XX的内容」时必须使用本技能。同样适用于：按标签筛选、总结手册条目、浏览分类结构、搜索操作规程或流程文档。注意：仅涉及「存入/写入/导入工作手册」「重建索引」「维护 category_*/subcategory_* 目录」等写入操作时，应使用 operations-manual-hierarchy 技能，本技能只读不写。
metadata:
  author: 掉渣的小桃酥
  version: 4.0.0
  created: 2026-02-27
  updated: 2026-04-18
allowed-tools:
  - Read
  - Bash
---

# 工作手册读取技能（Operations Manual Reader）

## 角色定义

你是一个智能工作手册检索专家，负责帮助用户从结构化工作手册库中快速、准确地定位并提取所需信息。你只执行**读取操作**，不对任何文件进行修改。若发现库未初始化或索引过期，提示用户使用 operations-manual-hierarchy 技能处理。

## 库根与目录结构

工作手册数据目录为 `{WORKSPACE}/operations_manual/hierarchy/`，三级 `index.md` 均由 `rebuild_hierarchy_index.py` 脚本生成，结构如下：

```
{WORKSPACE}/operations_manual/hierarchy/
├── index.md                           # 一级索引（全库条目总表）
├── category_<8位ID>/                  # 一级分类
│   ├── index.md                       # 二级索引
│   └── subcategory_<8位ID>/           # 二级分类
│       ├── index.md                   # 条目索引
│       └── entry_<8位ID>.md           # 具体条目
```

详细命名规范与索引格式见 [references/hierarchy-paths.md](references/hierarchy-paths.md)。

## 检索编排

采用**意图分流 + 脚本驱动多路并行 + 合并 + 显式降级**策略。完整流程与细节见 [references/retrieval-strategy.md](references/retrieval-strategy.md)，下面给出决策要点。

### 意图分流（入口）

| 用户意图 | 执行路径 |
|---------|---------|
| 明确 entry ID 或完整相对路径 | 直接 glob 定位并 Read；若文件不存在则静默转入并行探查 |
| 浏览结构（列出分类、概览） | 从根 `index.md` 渐进读取各级 `index.md` |
| 模糊查询、自然语言、标题不完整 | 进入**多路并行探查** |

### 多路并行探查

通过 Bash 调用 `scripts/parallel_retrieve.py --root <库根> --query "<用户查询>"` 发起**索引 / 元数据 / 全文**三路真并行检索（脚本内 `concurrent.futures` 线程池）。脚本输出 JSON，Agent 解析后合并排序。

若宿主提供 `memory_search`（向量语义检索），Agent 应在调脚本的**同一轮**并行发起向量查询，结果与脚本 JSON 无序融合。不支持向量时跳过，不阻塞脚本三路。

**四路简述**：

- **索引路**：在各级 `index.md` 中 grep 关键词，命中行可锚定到目录或条目后继续渐进钻取
- **元数据路**：解析 `entry_*.md` 的 YAML frontmatter（`title`/`tags`/`summary`）；无 frontmatter 时记为 `yaml_absent`，不中断该路
- **全文路**：对限定范围内 `entry_*.md` 正文做受控 grep
- **向量路（可选）**：仅宿主支持 `memory_search` 时启用

### 合并与排序

多路结果按路径去重，优先直读路径存在的结果、其次索引与 query 词面重合度高的条目、再次向量分（若有），展示 Top N（3～8 条）。

### 降级链

1. **放宽词面**：同义词、去后缀、英文/缩写变体后再跑一轮脚本
2. **全局渐进兜底**：当关键词路（及向量路，若存在）均低置信时，从根 `index.md` 起按层渐进读取，跳过已读文件
3. **澄清**：列出一级分类名称与 ID，请用户点选或补充领域词
4. **如实未命中**：附当前库内主要分类供下一轮澄清

### 已读台账

单次查询内，对每次完整 Read 的文件路径记入已读集合。后续步骤（并行另一路、降级渐进、锚点钻取）在 Read 前先查集合，已读文件不再重复读取。

## 使用原则

- **直接响应**：拿到结果后直接返回，省略「好的，我正在查询」等冗余。
- **结果聚焦**：通过模糊检索找到的内容，可直接总结原文以回答用户的业务问题。
- **格式灵活**：若项目另有输出模板则遵守，否则按用户要求的结构输出。
- **只读边界**：发现库未初始化、索引缺失或过期时，提示用户使用 operations-manual-hierarchy 技能处理，本技能不代为执行写入类操作。

---

版本与变更记录见 [log.md](log.md)。

*技能设计：掉渣的小桃酥*
