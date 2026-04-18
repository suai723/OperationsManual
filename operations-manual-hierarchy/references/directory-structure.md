## 目录结构规范

> **路径约定**：本文档中 `{WORKSPACE}` 表示 Agent 当前工作区根目录（对应 Cursor 工作区根、OpenClaw workspace 根或其他宿主的等价根路径）。在 Bash 命令中使用时，需先设置环境变量 `export WORKSPACE=/实际/工作区/路径`，然后以 `$WORKSPACE/...` 引用。

```
{WORKSPACE}/operations_manual/hierarchy/
├── index.md                            # 【一级索引】分类映射表（Agent 维护）
├── category_<8位随机字母数字>/          # 一级分类目录（可暂无 subcategory_*）
│   ├── index.md                       # 【二级索引】二级分类映射表（Agent 维护）
│   └── subcategory_<8位随机字母数字>/   # 二级分类目录（可暂无 entry_*）
│       ├── index.md                   # 【三级索引】条目清单（Agent 维护）
│       └── entry_<8位随机字母数字>.md  # 具体条目文件
```

**根目录默认为 `{WORKSPACE}/operations_manual/hierarchy/`，不存在时自动创建。**

> 目录名中 `category_` 对应一级分类，`subcategory_` 对应二级分类。各级 `index.md` 由模型按 [索引文件格式](index-formats.md) 直接创建和增量更新，脚本仅负责生成不冲突的随机目录/文件名（`scripts/gen_random_id.py`）。
>
> **空目录支持**：初始化一级或二级分类时，只需创建目录并生成含标题与表头的 `index.md`，无需创建占位条目（entry）。后续写入条目时由模型增量更新索引。

### 库根目录卫生

`{WORKSPACE}/operations_manual/hierarchy/` 根下**仅允许**存在：
- `category_*` 目录（一级分类）
- `index.md`（由 Agent 按索引格式维护）

以下内容**均属异常**，发现后应立即删除并由 Agent 按 [维护操作](maintenance.md) 章节重建索引：
- `entries/`、`scripts/`、`data/` 等非 `category_*` 子目录
- `index.json`、`index.yaml` 等非 `index.md` 的索引文件
- 任何不符合 `category_<8位>` 命名规范的目录
