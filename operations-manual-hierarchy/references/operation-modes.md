## 操作流程

> **路径约定**：`{WORKSPACE}` 表示 Agent 当前工作区根目录。Bash 命令中以 `$WORKSPACE` 引用（需先 `export WORKSPACE=/实际路径`）。详见 [目录结构规范](directory-structure.md)。

### 【模式一：单条存储】

适用于用户直接输入单条信息时。

1. **分析分类**：理解条目内容，确定最合适的一级分类和二级分类；若用户未指定分类，主动推断并告知用户

2. **检查工作空间**：确保在正确的工作空间中执行操作。工作手册的根目录应为 `{WORKSPACE}/operations_manual/`，所有操作都应在此路径下进行。

3. **检查一级索引**：读取 `{WORKSPACE}/operations_manual/hierarchy/index.md`；若文件不存在，先创建目录结构

4. **查找或创建一级分类目录**：在一级索引中查找一级分类是否存在；不存在则生成随机 ID，创建 `category_<ID>/` 目录

5. **查找或创建二级分类目录**：查找对应一级分类下的二级分类是否存在；不存在则生成随机 ID，创建 `subcategory_<ID>/` 目录

6. **去重检查**：读取目标二级分类目录下已有的条目文件，检查是否存在高度相似的内容（判断标准见「去重规则」）

7. **生成条目文件**：生成随机文件 ID，在二级分类目录下创建 `entry_<ID>.md`，写入标准格式内容（frontmatter 中必须包含 `summary` 字段，由模型理解内容后撰写 50～120 字概述）

8. **重建索引**：运行 `python scripts/rebuild_hierarchy_index.py --root <库根目录>`，脚本从各 entry 的 `summary` 字段组装索引概述区块，同时刷新映射表与统计数据

9. **更新影子摘要库**：为写入的条目生成一段 100~200 字的语义摘要，使用泛式影子摘要模板，追加 (append) 写入 `{WORKSPACE}/memory/operations_manual_shadow_index.md`。
   ```markdown
   ### [ID: {entry_id}] {条目主标题}
   - 📂 **归属**: {一级分类} > {二级分类}
   - 🏷️ **标签**: {tag1}, {tag2}...
   - 🧠 **语义摘要**: {100~200字核心业务描述...}
   ```

10. **向用户反馈**：
   ```
   ✅ 条目已存储
   📂 路径：operations_manual/hierarchy/category_a1b2c3d4/subcategory_i9j0k1l2/entry_q7r8s9t0.md
   🏷️ 分类：技术规程 > Python编程
   🆔 条目ID：entry_q7r8s9t0
   ```

### 【模式二：文档批量解析存储】

适用于解析外部文档（如Word、PDF、网页）并批量存储。

1. **文档解析**：使用适当的工具解析外部文档，提取可存储的条目内容

2. **内容切块**：将解析后的文档内容切分为语义完整的条目

3. **分类推断**：为每个条目确定最合适的一级分类和二级分类

4. **执行存储**：按模式一的流程批量存储每个条目

5. **分片写入**：对于大量条目，按分片策略处理——有子 Agent 能力时并行，否则主 Agent 顺序分片写入（见「并行处理策略」）

---

## 工作空间管理

### 重要原则

1. **始终在主工作空间执行**：所有 operations-manual-hierarchy 技能的操作都应在 `{WORKSPACE}/` 中进行，避免在临时工作空间创建文件

2. **明确路径规范**：
   - 工作手册根目录：`{WORKSPACE}/operations_manual/`
   - 分级索引目录：`{WORKSPACE}/operations_manual/hierarchy/`
   - 一级分类目录格式：`{WORKSPACE}/operations_manual/hierarchy/category_<8位随机ID>/`
   - 二级分类目录格式：`{WORKSPACE}/operations_manual/hierarchy/category_<ID>/subcategory_<8位随机ID>/`
   - 条目文件格式：`{WORKSPACE}/operations_manual/hierarchy/category_<ID>/subcategory_<ID>/entry_<8位随机ID>.md`

3. **避免临时工作空间**：禁止在 `{WORKSPACE}` 以外的临时目录中创建或修改工作手册文件

4. **操作前路径验证**：在执行任何操作前，检查当前工作空间是否正确，确保代码在预期路径下运行

### 调试与验证

1. **路径验证工具**：使用 Bash 命令验证路径（`$WORKSPACE` 需先 export 为实际路径）
   ```bash
   test -d "$WORKSPACE/operations_manual" || mkdir -p "$WORKSPACE/operations_manual"

   test -d "$WORKSPACE/operations_manual/hierarchy" || mkdir -p "$WORKSPACE/operations_manual/hierarchy"

   test -f "$WORKSPACE/operations_manual/hierarchy/index.md" || touch "$WORKSPACE/operations_manual/hierarchy/index.md"
   ```

2. **错误处理**：如果在操作过程中发现路径不正确，立即停止操作并向用户报告问题

---

## 操作流程改进

### 路径管理优化

为了防止工作空间路径问题，建议：

1. **使用 `{WORKSPACE}` 约定**：在所有操作中基于工作区根确定路径，而非硬编码特定平台的绝对路径
2. **操作前验证**：在每个关键步骤前验证路径正确性
3. **错误报告**：发现路径问题时，提供详细的错误信息和可能的解决方案
4. **自动化修复**：开发自动检测和修复工作空间路径问题的工具

### 分片执行体路径控制

当使用子 Agent 并行或主 Agent 顺序分片写入时：

1. **明确指定工作空间**：在创建子 Agent 时，明确指定工作空间路径；顺序分片时确保主 Agent 在正确目录下操作
2. **环境变量传递**：通过环境变量或分发文件传递工作空间信息
3. **结果验证**：检查分片执行体操作结果是否在正确的位置

---

通过以上改进，可以有效防止 operations-manual-hierarchy 技能在错误的临时工作空间执行操作，确保文件正确存储到工作手册中。
