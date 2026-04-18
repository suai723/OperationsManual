# Operations Manual Reader（工作手册读取技能）

面向 Cursor Agent 的技能包，路径：`operations-manual-reader/`。主说明见 [`operations-manual-reader/SKILL.md`](operations-manual-reader/SKILL.md)。

## 能力概览

- **只读检索**：从结构化工作手册库中查询、浏览、搜索、定位知识条目；**不写入、不维护目录**。
- **适用场景**：用户要「查工作手册」「在手册里找」「手册有没有 XX」「读 entry_xxx」「列出分类」「按关键词找条目」、按标签筛选、总结条目、浏览分类结构、搜索操作规程等。
- **与 Hierarchy 技能的分工**：涉及「存入/写入/导入」「重建索引」「维护 category_*/subcategory_*」时，应使用 **operations-manual-hierarchy**；本技能仅只读。

## 技术要点

| 能力 | 说明 |
|------|------|
| 精准直读 | 已知 entry ID 或完整相对路径时，直接定位并读取 |
| 结构浏览 | 从根 `index.md` 渐进读取各级索引，浏览一/二级分类 |
| 多路并行检索 | 通过 `scripts/parallel_retrieve.py` 发起索引 / 元数据 / 全文三路并行检索（JSON 输出） |
| 可选向量路 | 宿主提供 `memory_search` 时，可与脚本同轮并行做语义检索 |
| 合并与降级 | 结果去重排序；可放宽词面、全局渐进兜底、澄清分类、如实反馈未命中 |
| 已读台账 | 单次查询内避免重复读取同一文件 |

## 数据位置

工作手册数据根目录：`{WORKSPACE}/operations_manual/hierarchy/`（详见技能内「库根与目录结构」）。

## 版本

技能元数据中的版本以 `operations-manual-reader/SKILL.md` 为准；变更记录见 [`operations-manual-reader/log.md`](operations-manual-reader/log.md)。
