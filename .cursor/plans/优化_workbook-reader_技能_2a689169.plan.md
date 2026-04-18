---
name: 优化 workbook-reader 技能
overview: 依据 skill-creator 的写法与描述优化规范，重写 workbook-reader 的触发描述与正文流程，并与 operations-manual-hierarchy 的路径、三级索引与读写分工对齐；可选执行描述触发评测与迭代。
todos:
  - id: align-skill-md
    content: 重写 workbook-reader/SKILL.md：YAML description、三级索引路径、模式 C 双路径、与 hierarchy 分工、修正 SOUL/影子索引表述
    status: completed
  - id: add-ref-paths
    content: 新增 workbook-reader/references/hierarchy-paths.md（最短路径与命名规范 + 指向 hierarchy 详述）
    status: completed
  - id: sync-config-examples
    content: 同步 config.yml、query_workbook.py 提示、examples/sample_queries.md 中的库根路径为 operations_manual/hierarchy
    status: completed
  - id: optional-eval-desc
    content: （可选）按 skill-creator 准备 trigger 评测集并运行 description 优化脚本或人工校对
    status: completed
isProject: false
---

# 优化 workbook-reader 技能计划

## 现状与差距


| 维度    | [operations-manual-hierarchy/SKILL.md](e:\Myproject\OperationsManual\operations-manual-hierarchy\SKILL.md) | [workbook-reader/SKILL.md](e:\Myproject\OperationsManual\workbook-reader\SKILL.md)                                                                                                                                                                                                                                     |
| ----- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 库根路径  | `{WORKSPACE}/operations_manual/hierarchy/`                                                                 | 正文未写死路径；依赖 `memory_search` 与泛称 `index.md`                                                                                                                                                                                                                                                                              |
| 索引层级  | 根 / `category_*` / `subcategory_*` 三级 `index.md` + `entry_*.md`                                            | 模式 B 仅写「全局与子分类索引」，未与三级脚本生成索引对齐                                                                                                                                                                                                                                                                                         |
| 技能分工  | 已在 description 中写明：仅查询时用 **workbook-reader**                                                               | 未反向写明「禁止写入、写入请用 hierarchy」                                                                                                                                                                                                                                                                                             |
| 其它    | `entry` 含 `summary` 等 frontmatter                                                                          | 未指导用 `summary` 做无向量时的检索补充                                                                                                                                                                                                                                                                                              |
| 示例/配置 | —                                                                                                          | [examples/sample_queries.md](e:\Myproject\OperationsManual\workbook-reader\examples\sample_queries.md) 与 [config.yml](e:\Myproject\OperationsManual\workbook-reader\config.yml) 仍为 `workbook/hierarchy/`；[scripts/query_workbook.py](e:\Myproject\OperationsManual\workbook-reader\scripts\query_workbook.py) 报错文案同旧路径 |


仓库内**不存在** `SOUL.md` 与 `memory/workbook_shadow_index.md`；技能正文仍引用前者为硬性模板、后者为语义检索唯一来源，需在计划中修正为「有则用 / 无则降级」，避免 Agent 困惑。

## 设计原则（对齐 skill-creator）

遵循 [.cursor/skills/skill-creator/SKILL.md](e:\Myproject\OperationsManual.cursor\skills\skill-creator\SKILL.md)：

1. **description 承担触发职责**：在 YAML `description` 中合并「做什么 + 何时必须用」，略偏「主动触发」以减少漏触发；并与 hierarchy 技能**互斥说明**（查询/浏览/总结/定位条目 → 本技能；存入/导入/索引重建 → hierarchy）。
2. **正文解释 why、控制篇幅**：保留 A/B/C 瀑布流思想，但收紧为 imperative；单文件建议仍 <500 行；若层级说明变长，可抽 [operations-manual-hierarchy/references/directory-structure.md](e:\Myproject\OperationsManual\operations-manual-hierarchy\references\directory-structure.md) 的**最短摘要**到 `workbook-reader/references/`（新建一小段 `hierarchy-paths.md`），SKILL 内只保留指针，避免与 hierarchy 大文档重复维护。
3. **可选评测闭环**：技能稳定后，按 skill-creator「Description Optimization」生成 ~20 条 trigger eval（含 near-miss 负例），在用户有 Claude Code + `skill-creator` 的 `scripts.run_loop` 环境时再跑 `best_description`；本仓库若未接该脚本，则**手工迭代 description** 即可满足「用 skill-creator 优化」的核心（结构 + 文案规范）。

## 拟修改内容（按文件）

### 1. [workbook-reader/SKILL.md](e:\Myproject\OperationsManual\workbook-reader\SKILL.md)（核心）

- **YAML**：重写 `description`（中文）：覆盖场景示例——「查工作手册里有没有…」「某流程在手册哪条」「列出某分类条目」「按关键词找 entry」「读 entry_xxx」「根据问题总结手册内容」等；明确 **不触发** 场景：写入、批量导入、重建索引、`category_`*/`subcategory_`* 目录维护（指向 hierarchy）。可保留 `metadata.version` 递增、`updated: 2026-04-18`。
- **路径与模式 B**：固定库根 `{WORKSPACE}/operations_manual/hierarchy/`；模式 B 依次说明可读的三处 `index.md` 及何时读到 `subcategory_*/index.md` 再引导到 `entry_*.md`（与 [directory-structure.md](e:\Myproject\OperationsManual\operations-manual-hierarchy\references\directory-structure.md) 一致）。
- **模式 A**：说明条目文件位于 `category_<id>/subcategory_<id>/entry_<id>.md`；若用户只给短 ID，可用 glob / `grep` 定位唯一路径后再 `Read`。
- **模式 C**：  
  - 若宿主提供 `memory_search`：仍可用于影子索引（路径可写为约定文件名，并注明「以实际工作区为准」）。  
  - **若无**：降级为结合三级 `index.md` 中的概述 + `entry_*.md` 的 frontmatter（尤其 `summary`）与标题全文搜索，再模式 A 直读。
- **删除或弱化**对不存在文件的硬依赖：`SOUL.md` 改为「若仓库/项目另有输出模板则遵守，否则按用户要求的结构输出」。
- **与 hierarchy 协作**：简短互链说明——读取前若发现库未初始化或索引明显过期，**只读场景下**可提示用户运行 hierarchy 中的重建脚本，本技能不代为执行写入类操作（与「只读」一致）。
- **风格**：可与 hierarchy 对齐，减少标题中的装饰性符号，便于严肃场景使用（可选）。

### 2. 新建（可选但推荐）`workbook-reader/references/hierarchy-paths.md`

- 约半页：库根、`category_`* / `subcategory_`* / `entry_`* 命名、三级索引职责；末尾一行指向 hierarchy 的 `directory-structure.md` 作为权威详述。

### 3. 配置与脚本、示例（与 hierarchy 路径一致，避免技能外行为与文档矛盾）

- [workbook-reader/config.yml](e:\Myproject\OperationsManual\workbook-reader\config.yml)：`root_dir` 改为与 hierarchy 一致的相对说明或占位（例如文档注释说明应设为 `$WORKSPACE/operations_manual/hierarchy/`，Windows 下为工作区绝对路径）；默认示例避免写死仅适用于 OpenClaw 的 `/home/node/...`。
- [workbook-reader/scripts/query_workbook.py](e:\Myproject\OperationsManual\workbook-reader\scripts\query_workbook.py)：更新未初始化时的提示路径文案。
- [workbook-reader/examples/sample_queries.md](e:\Myproject\OperationsManual\workbook-reader\examples\sample_queries.md)：统计示例中的「存储路径」改为 `operations_manual/hierarchy/`。

### 4. skill-creator 的「描述优化」后置步骤（可选执行）

- 在 `workbook-reader/evals/` 下准备 `trigger_queries.json`（或按 skill-creator 的 JSON 数组格式）供后续 `run_loop` 使用。  
- 若环境具备：运行 `python -m scripts.run_loop ...`（路径指向 `.cursor/skills/skill-creator`），用输出的 `best_description` 替换 frontmatter。  
- 若不具备：用 5～10 条手写「应触发 / 不应触发」在对话中做一次人工校对即可。

## 实施顺序建议

```mermaid
flowchart LR
  intent[对齐 hierarchy 路径与索引模型]
  draft[重写 description 与 SKILL 正文]
  bundle[references + config + 示例 + 脚本提示]
  optional[可选 trigger eval 与 run_loop]
  intent --> draft --> bundle --> optional
```



## 风险与注意

- `**memory_search` 与影子索引**：不同宿主能力不一致；计划中必须写清「有则优先、无则索引+全文」，否则模式 C 在 Cursor 等环境易失效。  
- **技能安装为独立包时**：`references/hierarchy-paths.md` 应自洽，勿仅依赖仓库内相对链到另一技能文件夹。

