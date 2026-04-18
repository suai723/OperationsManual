## 维护操作

### 重建索引 (rebuild-index)

当索引与实际文件不一致时，由 Agent 手动重建：

1. 扫描 `{WORKSPACE}/operations_manual/hierarchy/` 下所有 `category_*/subcategory_*/entry_*.md`，解析每个条目的 YAML frontmatter
2. 按 [索引文件格式](index-formats.md) 规范，依次重写所有 `index.md`：
   - 三级索引（`subcategory_*/index.md`）：根据该目录下的 entry 文件生成条目清单
   - 二级索引（`category_*/index.md`）：根据该一级分类下的 subcategory 目录生成二级分类映射表
   - 一级索引（`hierarchy/index.md`）：根据所有 category 目录生成分类映射表
3. 可选：重建前先备份现有索引文件

> 概要字段按混合策略维护：已有概要仍可用时保留，仅对为空或明显过泛的重新生成。

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
