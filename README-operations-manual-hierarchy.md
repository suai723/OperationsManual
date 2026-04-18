# Operations Manual Hierarchy（工作手册分级索引技能）

面向 Cursor Agent 的技能包，路径：`operations-manual-hierarchy/`。主说明见 [`operations-manual-hierarchy/SKILL.md`](operations-manual-hierarchy/SKILL.md)。

## 能力概览

- **写入与维护**：将信息以「一级分类 / 二级分类」两级结构持久化到工作手册；随机目录名防冲突；各级 `index.md` 由脚本统一生成，便于 Agent 快速定位。
- **适用场景**：用户要「存入/写入/归档/导入/整理到工作手册」、批量导入文档、**重建或修复索引**、维护 `category_*` / `subcategory_*` / `entry_*` 等目录时。
- **与 Reader 技能的分工**：仅「查询/搜索」而无写入或索引维护意图时，应使用 **operations-manual-reader**；本技能负责写入侧与索引维护。

## 技术要点

| 能力 | 说明 |
|------|------|
| 单条存储 | 按规范创建条目与分类目录，填写 frontmatter（含 `summary` 等） |
| 批量存储 | 文档解析后按分类分片写入；支持子 Agent 时并行，否则主 Agent 顺序分片 |
| 分片策略 | 多一级分类 → 按一级分片；仅一个一级分类 → 按二级分片（详见技能内引用文档） |
| 索引重建 | 写入/删除/批量导入后运行 `scripts/rebuild_hierarchy_index.py`；**禁止手改** `index.md` 映射表与概述区块 |
| 去重与版本 | 更新内容时保留原文件并新版本，可用 `replaces` 指向旧条目 |
| 维护操作 | 重建索引、统计、备份等见技能内 [maintenance](operations-manual-hierarchy/references/maintenance.md) |

## 数据位置

库根：`{WORKSPACE}/operations_manual/hierarchy/`（根下仅允许规范内的 `category_*` 与脚本生成的 `index.md`）。

## 版本

技能元数据中的版本以 `operations-manual-hierarchy/SKILL.md` 为准；变更记录见 [`operations-manual-hierarchy/log.md`](operations-manual-hierarchy/log.md)。
