## 目录结构规范

> **路径约定**：本文档中 `{WORKSPACE}` 表示 Agent 当前工作区根目录（对应 Cursor 工作区根、OpenClaw workspace 根或其他宿主的等价根路径）。在 Bash 命令中使用时，需先设置环境变量 `export WORKSPACE=/实际/工作区/路径`，然后以 `$WORKSPACE/...` 引用。

```
{WORKSPACE}/operations_manual/hierarchy/
├── index.md                            # 【一级索引】记录所有一级分类映射与概述（脚本生成）
├── category_<8位随机字母数字>/          # 一级分类目录
│   ├── index.md                       # 【二级索引】记录该分类下所有二级分类映射与概述（脚本生成）
│   └── subcategory_<8位随机字母数字>/   # 二级分类目录
│       ├── index.md                   # 【二级分类目录索引】列出该目录下所有条目文件（脚本生成）
│       └── entry_<8位随机字母数字>.md  # 具体条目文件
```

**根目录默认为 `{WORKSPACE}/operations_manual/hierarchy/`，不存在时自动创建。**

> 目录名中 `category_` 对应一级分类，`subcategory_` 对应二级分类。三级 `index.md`（根、`category_*`、`subcategory_*`）均由 `scripts/rebuild_hierarchy_index.py` 自动生成，包含映射表和概述区块，禁止手动编辑。

### 库根目录卫生

`{WORKSPACE}/operations_manual/hierarchy/` 根下**仅允许**存在：
- `category_*` 目录（一级分类）
- `index.md`（由重建脚本生成）

以下内容**均属异常**，发现后应立即删除并重新运行 `rebuild_hierarchy_index.py`：
- `entries/`、`scripts/`、`data/` 等非 `category_*` 子目录
- `index.json`、`index.yaml` 等非 `index.md` 的索引文件
- 任何不符合 `category_<8位>` 命名规范的目录
