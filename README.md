# Operations Manual Skills

**Languages:** [场景介绍](#场景介绍) · [演示视频](#演示视频) · [简体中文](#简体中文) · [English](#english)

---

## 演示视频

演示文件位于 **`assets/demo.mp4`**。将仓库推送到 GitHub 后，在仓库首页 README 中即可用下方播放器直接观看（无需外链托管）。

**Demo video:** the recording is at [`assets/demo.mp4`](assets/demo.mp4). After you push to GitHub, the player below works on the repository README page.

<video src="./assets/demo.mp4" controls width="100%" playsinline>
  您的浏览器不支持 HTML5 视频，请<a href="./assets/demo.mp4">点击下载</a>。
</video>

---

## 场景介绍

### 中文

**Operations Manual** 为 Agent 提供一套可长期沉淀的**记忆与知识库**：把约定、流程、结论与参考资料整理成**结构化工作手册**。你可以把它想象成一座**记忆宫殿**，或一本常在手边的**工作手册**——Agent 在需要时随时翻阅，核对事实、对齐规范、检索历史结论，而不必仅依赖当次会话的有限上下文。

### English

**Operations Manual** is a **long-term memory and knowledge base** for agents. It turns norms, workflows, conclusions, and references into a **structured operations manual**—a **memory palace** you can navigate, or a **handbook** agents can **open and browse anytime** to recall facts, align on standards, and look up past decisions, instead of relying only on the current session’s context.

---

## 简体中文

### Operations Manual 技能集

本仓库包含两个面向 Cursor Agent 的 **Operations Manual（智能工作手册）** 技能：**只读检索** 与 **分级写入/维护**。二者共用同一数据根目录，按用户意图二选一使用。

| 技能 | 目录 | 主文档 |
|------|------|--------|
| 工作手册读取（Reader） | [`operations-manual-reader/`](operations-manual-reader/) | [`operations-manual-reader/SKILL.md`](operations-manual-reader/SKILL.md) |
| 工作手册分级索引（Hierarchy） | [`operations-manual-hierarchy/`](operations-manual-hierarchy/) | [`operations-manual-hierarchy/SKILL.md`](operations-manual-hierarchy/SKILL.md) |

**分工简述**：仅查询、浏览、搜索手册内容 → Reader；存入、导入、重建索引、维护 `category_*` / `subcategory_*` / `entry_*` → Hierarchy。

**数据根目录**：`{WORKSPACE}/operations_manual/hierarchy/`（Reader 只读；Hierarchy 负责写入与索引重建，根下目录结构须符合 Hierarchy 规范）。

#### 1. Operations Manual Reader（工作手册读取技能）

##### 能力概览

- **只读检索**：从结构化工作手册库中查询、浏览、搜索、定位知识条目；**不写入、不维护目录**。
- **适用场景**：「查工作手册」「在手册里找」「手册有没有 XX」「读 entry_xxx」「列出分类」「按关键词找条目」、按标签筛选、总结条目、浏览分类结构、搜索操作规程等。

##### 技术要点

| 能力 | 说明 |
|------|------|
| 精准直读 | 已知 entry ID 或完整相对路径时，直接定位并读取 |
| 结构浏览 | 从根 `index.md` 渐进读取各级索引，浏览一/二级分类 |
| 多路并行检索 | 通过 `operations-manual-reader/scripts/parallel_retrieve.py` 发起索引 / 元数据 / 全文三路并行检索（JSON 输出） |
| 可选向量路 | 宿主提供 `memory_search` 时，可与脚本同轮并行做语义检索 |
| 合并与降级 | 结果去重排序；可放宽词面、全局渐进兜底、澄清分类、如实反馈未命中 |
| 已读台账 | 单次查询内避免重复读取同一文件 |

**版本与变更**：以 [`operations-manual-reader/SKILL.md`](operations-manual-reader/SKILL.md) 元数据为准；[`operations-manual-reader/log.md`](operations-manual-reader/log.md)。

#### 2. Operations Manual Hierarchy（工作手册分级索引技能）

##### 能力概览

- **写入与维护**：将信息以「一级分类 / 二级分类」两级结构持久化到工作手册；随机目录名防冲突；各级 `index.md` 由脚本统一生成，便于 Agent 快速定位。
- **适用场景**：「存入/写入/归档/导入/整理到工作手册」、批量导入文档、**重建或修复索引**、维护 `category_*` / `subcategory_*` / `entry_*` 等目录。

##### 技术要点

| 能力 | 说明 |
|------|------|
| 单条存储 | 按规范创建条目与分类目录，填写 frontmatter（含 `summary` 等） |
| 批量存储 | 文档解析后按分类分片写入；支持子 Agent 时并行，否则主 Agent 顺序分片 |
| 分片策略 | 多一级分类 → 按一级分片；仅一个一级分类 → 按二级分片（详见技能内引用文档） |
| 索引重建 | 写入/删除/批量导入后运行 `operations-manual-hierarchy/scripts/rebuild_hierarchy_index.py`；**禁止手改** `index.md` 映射表与概述区块 |
| 去重与版本 | 更新内容时保留原文件并新版本，可用 `replaces` 指向旧条目 |
| 维护操作 | 重建索引、统计、备份等见 [`operations-manual-hierarchy/references/maintenance.md`](operations-manual-hierarchy/references/maintenance.md) |

**版本与变更**：以 [`operations-manual-hierarchy/SKILL.md`](operations-manual-hierarchy/SKILL.md) 元数据为准；[`operations-manual-hierarchy/log.md`](operations-manual-hierarchy/log.md)。

### 示例

以下话术可在启用 **Operations Manual Hierarchy** 与 **Operations Manual Reader** 技能后，直接作为用户提示词使用（具体写入与检索由 Agent 按技能规范执行）。

#### 创建工作手册

帮我创建一个工作手册，我想先构建一级目录：

1. **时事新闻**：用于存储不同类型的新闻消息，让 Agent 可以根据场景随时调取。
2. **网站收藏**：用于收藏不同类型的网站，方便 Agent 随时查阅，并根据用户需求调取。
3. **工作文档**：用于记录个人的工作文档摘要和链接；当用户想查阅时，Agent 可以快速调取。
4. **我的偏好**：用于记录个人使用偏好，以及 Agent 执行错误的记录，让 Agent 在执行同类任务时能根据偏好与历史错误及时修正。

#### 创建「时事新闻」的二级分类

1. 国际政治军事新闻  
2. 国内政治军事新闻  
3. 国内外科技新闻  
4. 国内外娱乐新闻  

#### 存入工作手册

帮我把 [伊朗正在审议美方新提议 尚未回应（央视新闻）](https://news.cctv.com/2026/04/18/ARTIeyzCqBIqppYDlZMcuW1q260418.shtml?spm=C94212.PBi4fu284lJm.EqrnPf7WDfbU.13) 存入工作手册。

#### 查询工作手册

帮我从工作手册中看看，最近的美伊关系。

---

## English

### Operations Manual skill set

The scenario above applies here as well: this repo implements that **long-term memory / handbook** idea as two concrete skills for Cursor Agent—**read-only retrieval** and **hierarchical write / maintenance**. They share the same data root; use one or the other depending on user intent.

| Skill | Folder | Main doc |
|-------|--------|----------|
| Operations Manual Reader | [`operations-manual-reader/`](operations-manual-reader/) | [`operations-manual-reader/SKILL.md`](operations-manual-reader/SKILL.md) |
| Operations Manual Hierarchy | [`operations-manual-hierarchy/`](operations-manual-hierarchy/) | [`operations-manual-hierarchy/SKILL.md`](operations-manual-hierarchy/SKILL.md) |

**How they split work**: Query, browse, or search the manual only → Reader. Save, import, rebuild indexes, or maintain `category_*` / `subcategory_*` / `entry_*` → Hierarchy.

**Data root**: `{WORKSPACE}/operations_manual/hierarchy/` (Reader is read-only; Hierarchy owns writes and index rebuilds; the tree must follow Hierarchy rules.)

#### 1. Operations Manual Reader

##### Capabilities

- **Read-only retrieval**: Query, browse, search, and locate entries in the structured manual; **no writes or directory maintenance**.
- **When to use**: Phrases like “look up the manual”, “find in the manual”, “does the manual mention X”, read `entry_xxx`, list categories, keyword search, filter by tags, summarize entries, browse structure, search procedures, etc.

##### Technical notes

| Area | Description |
|------|----------------|
| Direct read | When entry ID or full relative path is known, resolve and read the file |
| Structure browse | Walk from root `index.md` through index files for L1/L2 categories |
| Parallel retrieval | Run index / metadata / full-text in parallel via `operations-manual-reader/scripts/parallel_retrieve.py` (JSON output) |
| Optional vectors | If the host exposes `memory_search`, run semantic search in parallel with the script in the same turn |
| Merge & fallback | Dedupe and rank; relax terms, global progressive fallback, clarify categories, or report no hit |
| Read ledger | Within one query, avoid re-reading the same file |

**Versioning**: See metadata in [`operations-manual-reader/SKILL.md`](operations-manual-reader/SKILL.md); changelog in [`operations-manual-reader/log.md`](operations-manual-reader/log.md).

#### 2. Operations Manual Hierarchy

##### Capabilities

- **Write & maintain**: Persist content under a two-level taxonomy (L1 / L2); random folder names avoid clashes; each level’s `index.md` is script-generated for fast Agent navigation.
- **When to use**: “Save to the manual”, import/archive, batch imports, **rebuild or repair indexes**, maintain `category_*` / `subcategory_*` / `entry_*` trees.

##### Technical notes

| Area | Description |
|------|----------------|
| Single entry | Create entries and categories per spec; fill frontmatter (including `summary`) |
| Batch | After parsing, write by shard; parallel sub-agents when available, else sequential shards on the main agent |
| Sharding | Multiple L1 → shard by L1; single L1 → shard by L2 (see skill references) |
| Index rebuild | After writes/deletes/batch import, run `operations-manual-hierarchy/scripts/rebuild_hierarchy_index.py`; **do not hand-edit** mapping tables or summary blocks in `index.md` |
| Dedup & versions | Keep old files on updates; new files may use `replaces` for the previous entry |
| Maintenance | Rebuild, stats, backups: [`operations-manual-hierarchy/references/maintenance.md`](operations-manual-hierarchy/references/maintenance.md) |

**Versioning**: See metadata in [`operations-manual-hierarchy/SKILL.md`](operations-manual-hierarchy/SKILL.md); changelog in [`operations-manual-hierarchy/log.md`](operations-manual-hierarchy/log.md).
