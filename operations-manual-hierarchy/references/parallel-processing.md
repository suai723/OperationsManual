### 第四步：分片写入（子 Agent 并行 或 主 Agent 顺序）⭐

用户确认后，根据解析结果中一级分类的数量，选择对应的**分片策略**；再根据宿主环境决定**并行**还是**顺序**执行。

> **策略判断（必须在预处理开始前确定）：**
> - 解析结果包含 **≥ 2 个一级分类** → 执行 **[策略 A] 按一级分类分片**
> - 解析结果只有 **1 个一级分类** → 执行 **[策略 B] 按二级分类分片**

#### 0. 子 Agent 能力自检

在执行策略 A/B 之前，主 Agent **必须** 先判断当前宿主是否支持子 Agent 并行。

详细自检步骤与判定规则见：[子 Agent 能力自检与跨平台适配](agent-platforms.md)

- **支持子 Agent** → 每个分片启动一个子 Agent **并行**写入
- **不支持子 Agent** → 主 Agent 按分片**顺序**写入（逻辑与子 Agent 指令完全一致，仅串行执行）

以下策略 A/B 的预处理、分发文件、子 Agent 指令均适用于并行路径；顺序路径下主 Agent 按相同逻辑逐分片执行，不 spawn 子 Agent。

> **串行兼容模式流程**
>
> 1. 完成与并行模式相同的**预处理步骤**（确认根目录存在、读取/创建一级索引、创建所有需要的 category 和 subcategory 目录、初始化索引）
> 2. 将条目信息写入分发文件 `.dispatch_<时间戳>.json`（格式与并行模式一致，便于调试追踪）
> 3. 主 Agent 自身遍历分发文件中的所有条目，**按二级分类分组后依次执行**：
>    - 对每个条目：去重检查 → 调用脚本生成随机 entry ID → 写入 `entry_<ID>.md`（标准 frontmatter 格式） → 立即更新三级索引（`subcategory_<ID>/index.md` 追加条目行） → 立即更新二级索引中该二级分类的条目数和时间戳
>    - 对每个 successfully written 的条目，生成 100~200 字语义摘要（semantic_summary），用于后续影子摘要库更新
>    - 若检测到重复条目，跳过并记录到 skipped 列表
> 4. 全部条目写入完成后，执行**汇总步骤**：
>    - 更新一级索引（二级分类数、条目总数、最后更新时间与概要列）
>    - 从各条目的 semantic_summary 追加写入 `{WORKSPACE}/memory/operations_manual_shadow_index.md`（每条记录必须包含 `📄 **路径**` 字段，格式：`operations_manual/hierarchy/<category_dir>/<subcategory_dir>/<entry_id>.md`）
>    - 清理临时文件（`.dispatch_*.json`）
> 5. 向用户输出最终统计反馈（格式同并行模式）

---

#### [策略 A] 按一级分类分片（多一级分类场景）

适用于解析结果涉及 **2 个及以上一级分类**的情况，每个一级分类对应一个分片。

**主 Agent 预处理（串行，写入前统一完成）：**

1. 确认根目录 `{WORKSPACE}/operations_manual/hierarchy/` 存在，不存在则创建
2. 读取一级索引 `index.md`，解析已有分类映射
3. 对所有涉及的一级分类，统一完成目录创建和二级索引初始化：
   - 已存在的一级分类：记录其目录名，供分片执行体使用；若一级索引中该分类「概要」为空或明显过泛，基于本批次该分类下的条目标题/二级分类分布先生成 1 句话概要写入一级索引
   - 新建的一级分类：生成随机 ID，创建 `category_<ID>/` 目录和空 `category_<ID>/index.md`；并基于本批次该分类下的条目标题/二级分类分布生成 1 句话「概要」写入一级索引
4. **将上述分类目录映射写入临时分发文件** `{WORKSPACE}/operations_manual/hierarchy/.dispatch_<时间戳>.json`，供分片执行体读取：
   ```json
   {
     "dispatch_id": "<时间戳>",
     "split_by": "category",
     "categories": {
       "Agent配置": {
         "dir": "category_a1b2c3d4",
         "entries": [
           { "seq": 1, "title": "Agent角色定义", "subcategory": "角色定义", "content": "...", "importance": 5 },
           { "seq": 2, "title": "目录结构规范", "subcategory": "规范约束", "content": "...", "importance": 4 }
         ]
       },
       "技术学习": {
         "dir": "category_e5f6g7h8",
         "entries": [
           { "seq": 3, "title": "Python异步编程示例", "subcategory": "Python", "content": "...", "importance": 3 }
         ]
       }
     }
   }
   ```
5. 预处理完成后，按自检结果启动分片写入：
   - **并行路径**：对每个一级分类调用宿主子 Agent 工具（见下方示例）
   - **顺序路径**：主 Agent 按分片顺序逐一执行写入逻辑

**分片写入指令（并行时为子 Agent 指令，顺序时为主 Agent 执行逻辑）：**

> **路径 P：OpenClaw 会话 spawn**

```
sessions_spawn({
  "message": "
    你是工作手册写入子Agent，负责处理「<一级分类名>」分类下的所有条目写入。

    ## 任务来源
    读取分发文件：{WORKSPACE}/operations_manual/hierarchy/.dispatch_<时间戳>.json
    处理分类键：<一级分类名>
    对应目录：{WORKSPACE}/operations_manual/hierarchy/<category_dir>/

    ## 执行步骤
    1. 读取分发文件，获取本分类的条目列表和目录名
    2. 读取 <category_dir>/index.md（二级索引）
    3. 对每个条目依次执行：
       a. 查找或创建对应二级分类目录（subcategory_<ID>）
       b. 去重检查：扫描二级分类目录下已有条目，判断是否重复（重复则跳过并记录）
       c. 生成随机 entry ID，写入 entry_<ID>.md（标准格式）
       d. 立即更新 <category_dir>/index.md 中该二级分类的条目数和最后更新时间；并按需维护该二级分类「概要」（为空/过泛时，用条目标题、tags、语义摘要聚合成 1 句话写入概要列）
       e. 立即更新三级索引：在目标 subcategory_<ID>/index.md 中追加本条目的索引行（ID / 标题 / 概要 / 重要度 / 标签 / 创建时间）；若该文件不存在则先创建标准模板再追加。概要基于 frontmatter 的 title + tags + 正文前 100 字提炼（20–50 字）
    4. 本分类全部条目处理完毕后，将写入结果写入回报文件：
       {WORKSPACE}/operations_manual/hierarchy/.result_<一级分类名>_<时间戳>.json
       格式如下：
       {
         \"category\": \"<一级分类名>\",
         \"category_dir\": \"<目录名>\",
         \"written\": [
           { \"seq\": 1, \"entry_id\": \"entry_xxxxxxxx\", \"subcategory\": \"角色定义\", \"subcategory_dir\": \"subcategory_yyyyyyyy\", \"title\": \"...\", \"semantic_summary\": \"### [ID: entry_xxxxxxxx] ...\\n- 📂 **归属**: ...\\n- 📄 **路径**: operations_manual/hierarchy/<category_dir>/<subcategory_dir>/entry_xxxxxxxx.md\\n- 🏷️ **标签**: ...\\n- 🧠 **语义摘要**: ...\" }
         ],
         \"skipped\": [
           { \"seq\": 2, \"reason\": \"重复\", \"existing_entry\": \"entry_zzzzzzzz\" }
         ],
         \"errors\": []
       }
       注意：对于每一个 successfully written 的条目，必须由大模型在写入原文后，生成一段 100~200 字的纯自然语言业务摘要（semantic_summary），包含核心作用、组成逻辑、高频检索特征。

    ## 注意事项
    - 只操作本分类目录，不得读写其他分类目录
    - 子 Agent 可更新本分类下的二级索引与三级索引
    - 写入完成后必须输出回报文件，供主Agent汇总使用
  "
})
```

> **路径 Q：Cursor Task 子代理**
>
> 对每个分片调用 `Task`（subagent_type = `generalPurpose`），`prompt` 参数内容与路径 P 的 `message` 等价，以 Cursor 实际参数格式传递。

> **路径 S：顺序分片（无子 Agent）**
>
> 主 Agent 在同一上下文中，按分片逐一执行上述「执行步骤」，每完成一个分片写入对应的 `.result_*` 文件后，再处理下一个分片。

---

#### [策略 B] 按二级分类分片（单一级分类场景）⭐

适用于解析结果所有条目仅属于 **1 个一级分类**的情况。此时按二级分类分片，每个二级分类对应一个分片。

**主 Agent 预处理（串行，写入前统一完成）：**

1. 确认根目录 `{WORKSPACE}/operations_manual/hierarchy/` 存在，不存在则创建
2. 读取一级索引 `index.md`，解析已有分类映射
3. 对该一级分类完成目录创建（若未存在）：
   - 已存在的一级分类：记录其目录名
   - 新建的一级分类：生成随机 ID，创建 `category_<ID>/` 目录，记录映射
4. 对该一级分类下所有涉及的二级分类，统一完成目录创建：
   - 已存在的二级分类：记录其目录名，供分片执行体使用
   - 新建的二级分类：生成随机 ID，创建 `subcategory_<ID>/` 目录，记录映射
5. **将分发信息写入临时分发文件** `{WORKSPACE}/operations_manual/hierarchy/.dispatch_<时间戳>.json`，供分片执行体读取：
   ```json
   {
     "dispatch_id": "<时间戳>",
     "split_by": "subcategory",
     "category": "Agent配置",
     "category_dir": "category_a1b2c3d4",
     "subcategories": {
       "角色定义": {
         "dir": "subcategory_i9j0k1l2",
         "entries": [
           { "seq": 1, "title": "Agent角色定义", "content": "...", "importance": 5 },
           { "seq": 2, "title": "Agent行为准则", "content": "...", "importance": 4 }
         ]
       },
       "规范约束": {
         "dir": "subcategory_m3n4o5p6",
         "entries": [
           { "seq": 3, "title": "目录结构规范", "content": "...", "importance": 4 },
           { "seq": 4, "title": "命名规则", "content": "...", "importance": 3 }
         ]
       },
       "操作流程": {
         "dir": "subcategory_q7r8s9t0",
         "entries": [
           { "seq": 5, "title": "批量写入流程", "content": "...", "importance": 5 }
         ]
       }
     }
   }
   ```
6. 预处理完成后，按自检结果启动分片写入：
   - **并行路径**：对每个二级分类调用宿主子 Agent 工具
   - **顺序路径**：主 Agent 按分片顺序逐一执行写入逻辑

**分片写入指令（并行时为子 Agent 指令，顺序时为主 Agent 执行逻辑）：**

> **路径 P：OpenClaw 会话 spawn**

```
sessions_spawn({
  "message": "
    你是工作手册写入子Agent，负责处理「<一级分类名> > <二级分类名>」下的所有条目写入。

    ## 任务来源
    读取分发文件：{WORKSPACE}/operations_manual/hierarchy/.dispatch_<时间戳>.json
    处理二级分类键：<二级分类名>
    一级分类目录：{WORKSPACE}/operations_manual/hierarchy/<category_dir>/
    二级分类目录：{WORKSPACE}/operations_manual/hierarchy/<category_dir>/<subcategory_dir>/

    ## 执行步骤
    1. 读取分发文件，获取本二级分类的条目列表和目录名
    2. 对每个条目依次执行：
       a. 去重检查：扫描二级分类目录下已有条目，判断是否重复（重复则跳过并记录）
       b. 生成随机 entry ID，写入 entry_<ID>.md（标准格式）
    3. 本二级分类全部条目处理完毕后，将写入结果写入回报文件：
       {WORKSPACE}/operations_manual/hierarchy/.result_<二级分类名>_<时间戳>.json
       格式如下：
       {
         \"category\": \"<一级分类名>\",
         \"subcategory\": \"<二级分类名>\",
         \"subcategory_dir\": \"<目录名>\",
         \"written\": [
           { \"seq\": 1, \"entry_id\": \"entry_xxxxxxxx\", \"title\": \"...\", \"semantic_summary\": \"### [ID: entry_xxxxxxxx] ...\\n- 📂 **归属**: ...\\n- 📄 **路径**: operations_manual/hierarchy/<category_dir>/<subcategory_dir>/entry_xxxxxxxx.md\\n- 🏷️ **标签**: ...\\n- 🧠 **语义摘要**: ...\" }
         ],
         \"skipped\": [
           { \"seq\": 2, \"reason\": \"重复\", \"existing_entry\": \"entry_zzzzzzzz\" }
         ],
         \"errors\": []
       }
       注意：对于每一个 successfully written 的条目，必须由大模型在写入原文后，生成一段 100~200 字的纯自然语言业务摘要（semantic_summary），包含核心作用、组成逻辑、高频检索特征。

    ## 注意事项
    - 只操作本二级分类目录，不得读写其他二级分类目录
    - 不得修改任何索引文件（index.md），索引由主 Agent 汇总后统一更新
    - 每写入一个条目后继续处理下一条，全部完成后再输出回报文件
    - 写入完成后必须输出回报文件，供主Agent汇总使用
  "
})
```

> **路径 Q / 路径 S**：与策略 A 中的说明一致，分别使用 Cursor Task 或主 Agent 顺序执行。

---

#### 主 Agent 接收结果与汇总（自动化闭环）⭐

**无论**走并行路径还是顺序分片路径，主 Agent 在**全部分片写入完成且回报文件齐备**后，必须在同一工作流上下文中**立刻**执行以下收尾汇总逻辑，不得中断任务等待用户指令：

> **平台提示**：在 OpenClaw 中可利用 `Subagent finished` 信号自动触发汇总；在 Cursor 中 Task 返回即表示完成；顺序路径下无需等待信号，直接进入汇总。

1. 读取全部生成的分类（或二级分类）回报文件 `.result_*_<时间戳>.json`。
2. 全部回报文件就绪后，执行索引与摘要更新：
   - **更新索引**：
     - **策略 A**：子 Agent 已更新各自的二级索引与三级索引，主 Agent 仅需更新一级索引（汇总各分类的二级分类数、条目总数、最后更新时间与概要列）
     - **策略 B**：子 Agent 仅写了 entry 文件，主 Agent 需统一更新所有三级索引、二级索引和一级索引
   - **影子摘要库更新**：从回报文件中提取 `semantic_summary`，追加写入 (append) 到 `{WORKSPACE}/memory/operations_manual_shadow_index.md` 文件中。
3. **清理临时文件（必选）**：删除本次 `dispatch_id` 对应的 `.dispatch_<时间戳>.json` 和所有 `.result_*_<时间戳>.json`。
   - **正常完成**：索引更新与影子摘要更新后立即清理。
   - **部分失败**：汇总已完成分片后仍须清理所有 dispatch/result（含失败分片的回报文件），避免下次任务误读旧文件。
   - **流程中断**（用户取消或异常退出）：下次启动批量写入前，主 Agent 应先检查库根下是否存在残余 `.dispatch_*` / `.result_*`，若发现则删除后再继续。
   - 清理范围仅限 `.dispatch_*` 和 `.result_*`，**不得**删除 `entry_*.md`、`index.md` 等持久数据。
4. 一切收尾动作完成后，向用户输出最终成功的统计反馈（见第五步）

> ⚠️ **并发安全约束**：
> - **策略 A**：每个分片执行体只写自己一级分类目录内的 entry 文件与该分类下的索引，不同分片操作完全隔离，无文件竞争
> - **策略 B**：每个分片执行体只写自己二级分类目录内的 entry 文件，不操作任何索引文件
> - **顺序路径**：无跨进程并发，仍须遵守目录隔离规则（每次只操作当前分片目录）
> - **索引更新责任**：策略 A 由子 Agent 维护二级/三级索引、主 Agent 维护一级索引；策略 B 所有索引由主 Agent 统一更新
> - 分发文件 `.dispatch_*.json` 为只读，分片执行体不得修改
