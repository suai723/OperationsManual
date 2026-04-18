# 工作手册目录结构与路径规范

> 本文件为 operations-manual-reader 技能的快速参考。权威详述见 [operations-manual-hierarchy/references/directory-structure.md](../../operations-manual-hierarchy/references/directory-structure.md)。

## 库根

```
{WORKSPACE}/operations_manual/hierarchy/
```

`{WORKSPACE}` 为 Agent 当前工作区根目录。Bash 中可通过 `$WORKSPACE` 环境变量引用。

## 目录命名

| 层级 | 目录名格式 | 说明 |
|------|-----------|------|
| 一级分类 | `category_<8位随机字母数字>` | 对应中文一级分类名（映射在 `index.md` 中） |
| 二级分类 | `subcategory_<8位随机字母数字>` | 对应中文二级分类名 |
| 条目文件 | `entry_<8位随机字母数字>.md` | 具体知识条目 |

## 三级索引

所有 `index.md` 由 `rebuild_hierarchy_index.py` 脚本自动生成，禁止手动编辑。

1. **根索引** `hierarchy/index.md` — 全库条目总表（一级分类、二级分类、条目 ID、标题、相对路径、概述等）
2. **一级分类索引** `category_*/index.md` — 该分类下所有条目
3. **二级分类索引** `category_*/subcategory_*/index.md` — 该目录下所有条目文件

## 条目 frontmatter 关键字段

- `title`、`tags`、`summary`（50～120 字）、`category`、`subcategory`、`importance`
- `summary` 为推荐必填；缺失时索引脚本从正文截取首段兜底
- 部分存量条目可能无 YAML frontmatter，检索时须兼容（见 retrieval-strategy.md）
