## 维护操作

### 重建索引 (rebuild-index)

当索引与实际文件不一致时，运行重建脚本：

```bash
python scripts/rebuild_hierarchy_index.py --root <工作手册分级库根目录>
```

脚本会遍历所有 `category_*/subcategory_*/entry_*.md`，重新扫描 YAML frontmatter，一次性重写所有 `index.md`（含映射表和概述区块），并在终端输出修复摘要。

> 脚本仅依赖 Python 标准库，无需 `pip install`。根目录也可通过环境变量 `OPERATIONS_MANUAL_HIERARCHY_ROOT` 指定。

### 统计信息 (stats)

读取一级索引并汇总，输出格式：

```
📊 工作手册统计
├── 一级分类数：N
├── 二级分类数：N
├── 条目总数：N
├── 最早条目：YYYY-MM-DD
└── 最近更新：YYYY-MM-DD HH:MM
```

### 备份 (backup)

```bash
tar -czf operations_manual_backup_$(date +%Y%m%d_%H%M%S).tar.gz "$WORKSPACE/operations_manual/hierarchy/"
```
