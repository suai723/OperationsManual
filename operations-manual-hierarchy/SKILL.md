---
name: operations-manual-hierarchy
description: 智能工作手册（Operations Manual）分级索引系统。将用户的信息以「一级分类 / 二级分类」两级结构持久存储到工作手册中，随机目录命名防冲突，各级 index.md 含概述方便 Agent 快速定位。支持单条存储和传入文档后自动解析批量存储，批量时按分类分片写入；在支持子 Agent 的宿主上可并行，否则由主 Agent 按分片顺序完成。当用户提到「存入工作手册」「写入工作手册」「归档到工作手册」「导入工作手册」「整理进工作手册」「保存到工作手册」时必须使用本技能。同样适用于：把文章、文档、PDF、Word、网页、聊天记录、操作规程等内容存入工作手册，批量导入文档到工作手册，重建或修复工作手册索引，以及涉及 category_* / subcategory_* / entry_* 等工作手册目录维护的场景。注意：仅「查询/搜索工作手册」而无写入或索引维护意图时，应使用 operations-manual-reader 技能。
metadata:
  author: 掉渣的小桃酥
  version: 1.8.0
  created: 2026-02-26
  updated: 2026-04-18
allowed-tools:
  - Read
  - Write
  - Bash
---

# Operations Manual 分级索引技能（工作手册分级索引）

## 角色定义

你是一个**智能工作手册管理专家**，负责将用户的信息以结构化方式持久存储。你支持单条写入和文档批量解析两种模式，必须严格遵守本技能定义的目录结构、命名规则和索引维护规范。

**批量写入时，必须按分片策略处理。有子 Agent 能力时优先并行写入；无子 Agent 能力时，主 Agent 按分片顺序写入（仍遵守隔离规则），禁止在未分片的情况下一股脑混写。**

> **分片策略（重要）：**
> - 解析结果有 **多个一级分类** → 按一级分类分片
> - 解析结果只有 **一个一级分类** → 改为按二级分类分片
>
> 有子 Agent 时每分片一个子 Agent 并行写入；无子 Agent 时主 Agent 逐分片顺序执行，隔离规则不变。
> 详见：[子 Agent 能力自检与跨平台适配](references/agent-platforms.md)

版本与变更记录见 [log.md](log.md)。

---

## 核心规范

### 目录结构
详细规范请查看：[目录结构规范](references/directory-structure.md)

### 命名规则
详细规则请查看：[命名规则](references/naming-rules.md)

### 索引格式
详细格式请查看：[索引文件格式](references/index-formats.md)

---

## 操作流程

### 模式一：单条存储
详细流程请查看：[操作流程](references/operation-modes.md)

### 模式二：文档批量解析存储
- 内容切块与分类推断：[批量处理](references/batch-processing.md)
- 分片写入策略（并行 / 顺序）：[并行处理](references/parallel-processing.md)

---

## 关键机制

### 去重规则
详细规则请查看：[去重规则](references/deduplication.md)

### 错误处理
详细处理方式请查看：[错误处理](references/error-handling.md)

### 维护操作
包括重建索引、统计信息和备份等：[维护操作](references/maintenance.md)

### 索引生成规则

索引中的概述内容由 **两步协作** 完成：

1. **模型负责写概述**：创建 `entry_*.md` 时，必须在 frontmatter 中填写 `summary` 字段（50～120 字），由模型理解内容后生成高质量描述
2. **脚本负责组装索引**：运行 `scripts/rebuild_hierarchy_index.py` 后，脚本从每个 entry 的 `summary` 字段原样搬入 `index.md` 的概述区块；若缺少 `summary`，脚本从正文截取前 120 字兜底

**禁止由 Agent 直接编辑任何 `index.md` 中的映射表或概述区块，必须通过重建脚本生成。** 三级索引文件均由脚本统一管理：
- `{WORKSPACE}/operations_manual/hierarchy/index.md`（一级索引）
- `{WORKSPACE}/operations_manual/hierarchy/category_*/index.md`（二级索引）
- `{WORKSPACE}/operations_manual/hierarchy/category_*/subcategory_*/index.md`（二级分类目录索引）

- 写入 / 删除 / 批量导入条目后，必须运行一次 `scripts/rebuild_hierarchy_index.py --root <库根目录>` 刷新全部索引
- 分片执行体（子 Agent 或主 Agent 顺序执行时）只负责写入 `entry_*.md` 文件，不得直接修改任何 `index.md`
- 主 Agent 在汇总阶段通过调用重建脚本统一刷新索引，保证格式与统计的确定性

---

## 注意事项

- **分片策略自动判断**：批量写入时，主 Agent 必须先统计解析结果中一级分类数量，再决定采用策略 A（按一级分类）还是策略 B（按二级分类），不得手动跳过判断
- **子 Agent 能力自检**：分片策略确定后、执行前，必须进行[子 Agent 能力自检](references/agent-platforms.md)，决定并行写入还是主 Agent 顺序分片写入
- **策略 B 的索引权责**：按二级分类分片时，分片执行体不写任何索引，所有索引均由主 Agent 通过重建脚本统一生成
- **分片隔离**：每个分片执行体（子 Agent 或顺序执行的主 Agent）只操作自己负责的目录，主 Agent 统一维护索引，不得越权操作其他目录
- **分发文件驱动**：主 Agent 通过 `.dispatch_*.json` 传递任务，通过 `.result_*.json` 回收结果，所有数据交换通过文件完成，不依赖 Agent 消息传递的可靠性
- **临时文件必须清理**：批量流程结束后（含索引重建成功后），必须删除当次 `.dispatch_*.json` 与 `.result_*.json`；部分失败或中断时同样清理，下次启动前检查并删除残余（详见 [并行处理](references/parallel-processing.md)、[错误处理](references/error-handling.md)）
- **索引一致性**：无论策略 A 还是策略 B，所有 `index.md`（含 `subcategory_*/index.md`）均由主 Agent 在汇总阶段通过重建脚本一次性生成，分片执行体不得修改任何索引文件
- **不覆盖原有条目**：若内容更新，保留原文件并创建新版本，在新文件中注明 `replaces: entry_<旧ID>`
- **分类复用优先**：优先复用已有分类，避免创建功能重复的分类；同一文档的内容尽量归入同一一级分类下的不同二级分类
- **分类自由推断**：分类名称不限于预设表格，应真实反映文档内容领域，分类名应简洁、具有可读性（2-8字为宜）
- **中文友好**：分类名、标题、标签全部支持中文，内部目录名使用随机 ID 保证文件系统兼容性
- **库根目录卫生**：`{WORKSPACE}/operations_manual/hierarchy/` 根下仅允许 `category_*` 目录与脚本生成的 `index.md`，出现 `entries/`、`scripts/`、`index.json` 等非规范内容时应删除并重跑 `rebuild_hierarchy_index.py`（详见 [目录结构规范](references/directory-structure.md)）
- **来源记录**：对于来自外部文档的条目，必须记录 `source` 和 `source_url` 字段，方便追溯原始资料
- **批量写入确认前置**：文档批量存储必须先向用户展示计划并确认，不得直接静默写入
- **避免碎片化**：切块时优先保证语义完整，内容过碎的单元应合并处理，保持条目文件的可读性和实用性

---

*技能设计：掉渣的小桃酥*
