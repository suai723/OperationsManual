---
name: OperationsManual 技能优化
overview: 将 `workbook-hierarchy` 技能包重命名为 `operations-manual-hierarchy`（展示名 Operations Manual），按 skill-creator 流程优化触发描述；**以「工作手册」为核心中文触发词**（如「把文章存入工作手册」）；术语统一为一级分类/二级分类；新增仅标准库的 Python 索引重建脚本，生成含概述的稳定 index.md。
todos:
  - id: skill-creator-optimize
    content: 按 skill-creator 优化 description；必须显式包含「工作手册」及同义触发短语（存入/写入/归档/导入到工作手册等）
    status: completed
  - id: add-rebuild-script
    content: 新增 rebuild_hierarchy_index.py：扫描 entry、写一级/二级 index.md（含各级概述区块，规则见计划第 3.3 节）
    status: completed
  - id: rename-skill-folder
    content: 将 workbook-hierarchy/ 重命名为 operations-manual-hierarchy/，更新 SKILL.md 的 name/description/metadata/标题与内部引用
    status: completed
  - id: terminology-pass
    content: 全文将「大分类/小分类」改为「一级分类/二级分类」（保留目录名 category_/subcategory_ 不变）
    status: completed
  - id: update-references
    content: 修订 references：operation-modes、parallel-processing、maintenance、index-formats；索引由脚本生成；策略 A 子 Agent 不写索引
    status: completed
  - id: verify-consistency
    content: 全文检索旧技能名与索引手写步骤；确认与 workbook-reader 的 workbook/hierarchy 路径仍一致
    status: completed
isProject: false
---

# Operations Manual 分级索引技能优化计划

## 背景与范围

- 当前技能位于 `[workbook-hierarchy/SKILL.md](workbook-hierarchy/SKILL.md)`，流程大量依赖 Agent **手写维护** `index.md` 表格（见 `[references/parallel-processing.md](workbook-hierarchy/references/parallel-processing.md)` 中策略 A 子 Agent「立即更新二级索引」等），易产生格式漂移与统计错误。
- 数据根目录在文档与 `[workbook-reader](workbook-reader/config.yml)` 中均为 `**workbook/hierarchy/`**。本次默认 **只重命名技能包与元数据**，**不迁移**磁盘上的 `workbook/` 路径，以免破坏现有库与 reader 配置；若你后续希望目录也改为 `operations-manual/` 等，可再单开任务同步改 reader 与存量数据。

## 0. 使用 skill-creator 驱动优化（新增）

实施本计划时，应 **显式遵循** 仓库内 `[.cursor/skills/skill-creator/SKILL.md](.cursor/skills/skill-creator/SKILL.md)`（skill-creator）中的流程，而不是只凭直觉改文案：

- **描述与触发**：在重写 `description` 后，可选用 skill-creator 自带的 `[scripts/improve_description.py](.cursor/skills/skill-creator/scripts/improve_description.py)` 做触发文案迭代；对照其中「description 要略偏主动、覆盖具体场景」的规范自检。
- **范围**：至少覆盖「重命名后的技能包 + 术语 + 索引概述规范 + 脚本约束」改完后的整包一致性；若时间允许，可补充少量测试提示语做定性验收（非必须跑完整 eval 流水线）。
- **产出**：在 SKILL 或 references 中无需单独新建「eval 报告」类文档，除非你愿意保留简要的变更说明（可选）。

## 1. 重命名技能包（workbook → Operations Manual）


| 项           | 建议                                                                                                                      |
| ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| 目录          | `workbook-hierarchy/` → `operations-manual-hierarchy/`（全小写 kebab-case，与仓库内 `[workbook-reader](workbook-reader)` 命名风格一致） |
| YAML `name` | `operations-manual-hierarchy`（与目录名一致，便于 Cursor 识别）                                                                      |
| 正文标题        | 「Operations Manual 分级索引技能」；必要时括号保留「原工作手册分级索引」一句，降低老用户困惑                                                                 |
| 版本          | `metadata.version` 递增至如 `1.5.0`，`updated` 改为当前日期                                                                        |


需要全局替换的 **技能内部** 字符串：`workbook-hierarchy` → `operations-manual-hierarchy`（例如 `[references/operation-modes.md](workbook-hierarchy/references/operation-modes.md)` 中临时工作空间名 `workspace-workbook-hierarchy` → `workspace-operations-manual-hierarchy`）。

**不修改**（除非另做迁移任务）：`[workbook-reader/scripts/query_workbook.py](workbook-reader/scripts/query_workbook.py)` 等对 `workbook/hierarchy` 的路径引用。

## 2. 优化触发条件（`description`）

依据 skill-creator（见 **第 0 节**）：`**description` 是主要触发器**，应同时写清「做什么」与「何时用」，并略偏主动以防 under-trigger。

**改写策略**（保持中文、控制长度、前置触发词）：

- **核心关键词（中文）**：**「工作手册」** 应出现在 `description` 靠前位置，作为与用户自然语言对齐的主锚点；即使用户说「这篇文章」「这段内容」未提英文 Operations Manual，只要出现 **存入 / 写入 / 归档 / 导入 / 保存到 / 整理进 + 工作手册** 等组合，即应强烈倾向触发本技能。
- **典型用户句式（写入意图）**：例如「帮我把这篇文章的内容**存入工作手册**」「把下面内容**写入工作手册**」「把 PDF **导入工作手册**」「**整理进工作手册**」——`description` 中应点名此类句式，减少漏触发。
- **首句**：一句话定义能力（面向 **工作手册 / Operations Manual** 的分级存储：**一级分类 / 二级分类**、随机目录名、分级 `index.md`（含概述）、批量并行写入）。
- **触发枚举**（补充）：在含「工作手册」前提下，用户还常搭配 **文章、文档、网页、PDF、Word、聊天记录、规程** 等来源词；**批量**解析入库；**重建/修复工作手册索引**、索引与文件不一致；提及 **分级目录** `category_*` / `subcategory_*` / `entry_*` 等维护场景。
- **排除/边界**（可选一行）：仅「**查询 / 搜索** 工作手册」而无写入或索引维护意图时，更适合 `[workbook-reader](workbook-reader/SKILL.md)`，避免与本技能抢触发。
- **工具行**：`allowed-tools` 保持现有能力；若脚本通过 `Bash` 调用 `python`，无需新增工具。

## 2b. 术语统一：一级分类 / 二级分类（新增）

- 文档与技能正文中，原「**大分类**」一律改为「**一级分类**」，原「**小分类**」一律改为「**二级分类**」。
- **物理目录命名保持不变**：仍为 `category_<ID>`、`subcategory_<ID>`（避免迁移已有库与路径）；仅在中文说明、表格列名、并行分片文案、条目的 `category` / `subcategory` 字段语义说明中与「一级/二级」对应解释清楚。
- 条目的 YAML frontmatter **字段名**是否从 `category`/`subcategory` 改为 `level1_category`/`level2_category`：默认 **不改字段名**（减少与存量条目不兼容），在 `index-formats.md` 中用一句话标注「字段名仍为 category/subcategory，语义上对应一级/二级分类」。

## 3. 用脚本生成索引（稳定性）

### 3.1 新增脚本（建议路径）

在重命名后的技能包下新增：

- `[operations-manual-hierarchy/scripts/rebuild_hierarchy_index.py](workbook-hierarchy/scripts/rebuild_hierarchy_index.py)`（实施时落在最终目录）

**行为约定**（仅依赖 Python 标准库：`pathlib`、`re`、`datetime`、`json` 可选用于校验，避免 `pip install`）：

1. **参数**：`--root` 指向分级库根（默认：相对脚本定位到「技能包所在仓库」的 `workbook/hierarchy`，或通过环境变量如 `OPERATIONS_MANUAL_HIERARCHY_ROOT` 覆盖，以便 OpenClaw 绝对路径与本地开发一致）。
2. **扫描**：仅识别 `category_<8位[a-z0-9]>/subcategory_<8位>/entry_<8位>.md`（与 `[references/naming-rules.md](workbook-hierarchy/references/naming-rules.md)` 一致），跳过 `.dispatch_*`、`.result_*` 等。
3. **元数据**：从每个条目文件的 YAML frontmatter 读取 `category`、`subcategory`、`title`、`tags`、`created`、`updated`（缺失时回退文件 mtime）；若存在可选字段 `summary`（或计划中新定义的 `brief`，二选一在 index-formats 中定稿），优先作为该条目的单行概述来源。
4. **聚合**：按目录聚合条目数、`min(created)` / `max(updated)`，生成与更新后的 `[references/index-formats.md](workbook-hierarchy/references/index-formats.md)` 一致的 **根级**与**一级分类目录内**的 `index.md` 全文（固定标题、固定表格列顺序、统一时间格式），保证每次运行输出稳定。
5. **空目录**：无 `entry_*.md` 的二级分类目录仍出现在二级表（条目数 0）；一级分类下若完全无条目，仍可根据子目录生成行，显示名称优先用已有 frontmatter，否则回退为「未命名」或目录 ID（在脚本内固定一种策略并写进 `[references/maintenance.md](workbook-hierarchy/references/maintenance.md)`）。
6. **退出码**：成功 0；根目录不存在或不可写时非 0，便于 Agent/Bash 判断。

### 3.2 修改技能流程（与脚本对齐）

在 **SKILL 主文件「注意事项」或「关键机制」** 增加硬规则：

- **禁止**用模型直接编辑一级/二级 `index.md` 中的映射表或概述章节来「凑统计」；**写入/删除/批量导入/重建索引** 后，必须执行一次重建脚本（可接受「仅当次任务相关根目录」与 OpenClaw 绝对路径一致）。

需改动的参考文档要点：


| 文件                                                                                          | 变更要点                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `[references/operation-modes.md](workbook-hierarchy/references/operation-modes.md)`         | 模式一单条：步骤 3「创建空索引」可保留占位；步骤 8「手写更新索引」→ **改为运行脚本**；初始化目录后若尚无条目，可生成最小合法 `index.md` 或由脚本生成空表                                                                                        |
| `[references/parallel-processing.md](workbook-hierarchy/references/parallel-processing.md)` | **策略 A**：子 Agent 步骤中删除「更新 `category_dir/index.md`」；统一为「只写 `entry_*.md`」；主 Agent 汇总后 **一次** 调脚本刷新全部索引（或 `--root` 指向库根，全量重建最简单）。**策略 B** 已与「子 Agent 不写索引」一致，主 Agent 收尾改为调脚本而非手写表 |
| `[references/maintenance.md](workbook-hierarchy/references/maintenance.md)`                 | 「重建索引」步骤 1–3 改为：**运行 `python .../rebuild_hierarchy_index.py --root ...`**，再人工/Agent 核对输出摘要                                                                                     |
| `[references/index-formats.md](workbook-hierarchy/references/index-formats.md)`             | 更新表格列名为一级/二级分类语义；约定 **映射表 + 概述章节** 全文均由脚本生成；可选 frontmatter `summary`/`brief`；说明 category/subcategory 字段与一级/二级分类的对应关系                                                           |


**影子摘要** `memory/workbook_shadow_index.md` 仍可由 Agent 追加（与索引表解耦）；若希望也完全脚本化，可列为后续增强，本次不强制。

### 3.3 各级 `index.md` 增加「概述」区块（新增）

目标：Agent **只读索引**即可判断「每个目录大致做什么、每个条目文件讲什么」，再决定深入读哪个 `entry_*.md`。

**设计原则**：概述正文仍由脚本 **确定性生成**（不调用 LLM），避免索引文件内容随模型波动。

建议结构（写入 `index-formats.md` 并由脚本实现）：

1. **根目录 `workbook/hierarchy/index.md`**
  - 保留现有统计头与「一级分类映射表」。
  - 在表下增加章节 `## 一级分类目录概述`：对每个 `category_<ID>/` 用固定模板生成一段，例如：一级分类显示名、目录 ID、二级分类个数与条目总数、各二级分类名称列表（可截断长度）、**代表性条目标题**（按 `updated` 取最近 3～5 条，不足则全列）、可选标签并集 Top N。无条目时写明「尚无条目，仅预留目录」。
2. **一级分类目录内 `category_<ID>/index.md`**
  - 保留「二级分类映射表」。
  - 增加章节 `## 二级分类目录概述`：每个 `subcategory_<ID>/` 一段：显示名、目录 ID、条目数、**各 `entry_*.md` 一行**（`entry_id`、title、单行概述）。单行概述优先级：`summary` / `brief` frontmatter → 否则从正文「## 内容」下取纯文本首行或首段并 **硬截断** 到固定字符数（如 120），去除 Markdown 语法痕迹（脚本内简单规则即可）。
3. **与写入流程的衔接**：批量写入时子 Agent 仍只写 `entry_*.md`；若希望概述质量更高，可在条目的 frontmatter 中 **推荐** 写入简短 `summary`（一句 50～120 字），由脚本原样纳入索引；未写则由脚本按正文截断补齐。
4. **体积控制**：对概述列表设上限（每级最多条目数、每段最大字符），超出时追加「…共 N 条，其余见子目录」类说明，避免单文件过大。

## 4. 实施顺序建议

```mermaid
flowchart LR
  S[skill-creator 自检 description] --> A[新增 rebuild 脚本含概述]
  A --> B[本地用样例或空库跑通]
  B --> C[重命名目录与 SKILL 元数据]
  C --> T[术语一级二级分类全文替换]
  T --> D[批量更新 references 与 index 格式]
  D --> E[通读全文路径与策略 A/B 一致]
```



## 5. 验收标准

- 技能目录与 `name:` 已为 `operations-manual-hierarchy`，`description` 经 skill-creator 规范自检（及可选 improve_description 迭代）；**显式包含「工作手册」** 及「存入/写入/导入工作手册」等典型句式，与「仅查询」场景边界清晰。
- 全文术语已为「一级分类 / 二级分类」，且与 `category`_* / `subcategory_`* 目录名的对应关系在 `index-formats.md` 中有说明。
- 运行重建脚本后，根 `index.md` 与各 `category_*/index.md` 均包含计划第 **3.3** 节规定的 **概述章节**；仅改条目正文不重跑脚本时，概述可在下次重建时更新（行为在 maintenance 中写明）。
- 在含若干 `entry_*.md` 的测试目录上运行脚本两次，**输出字节级一致**（除「最后更新」若脚本每次写当前时间则允许该字段变化——可选：**索引头时间**用「本次扫描完成时间」或「全库 max(updated)」二选一并在文档中固定，避免无意义 diff）。
- 文档中不再要求子 Agent / 主 Agent **手改**映射表统计列或概述列表；重建索引维护项明确指向脚本命令。

