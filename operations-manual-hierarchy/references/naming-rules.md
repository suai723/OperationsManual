## 命名规则

### 随机 ID 生成规则

- 组成：小写字母 (a-z) + 数字 (0-9)，共 8 位
- 生成脚本：`scripts/gen_random_id.py`（位于技能目录内）
- 生成方式：通过脚本生成并校验目标目录内不冲突，若冲突则自动重试（默认最多 5 次）
- 命名格式：
  - 一级分类目录：`category_<8位随机ID>`
  - 二级分类目录：`subcategory_<8位随机ID>`
  - 条目文件：`entry_<8位随机ID>.md`

#### 脚本用法（推荐）

脚本位于技能目录的 `scripts/gen_random_id.py`，使用 `{SKILL_DIR}` 引用技能根目录。执行时模型应将 `{SKILL_DIR}` 替换为实际的技能文件系统路径。

```bash
# 一级分类目录名（在 {WORKSPACE}/operations_manual/hierarchy/ 下生成）
python3 {SKILL_DIR}/scripts/gen_random_id.py \
  --parent "{WORKSPACE}/operations_manual/hierarchy" \
  --prefix "category_"

# 二级分类目录名（在某个一级分类目录下生成）
python3 {SKILL_DIR}/scripts/gen_random_id.py \
  --parent "{WORKSPACE}/operations_manual/hierarchy/category_<ID>" \
  --prefix "subcategory_"

# 条目文件名（在某个二级分类目录下生成）
python3 {SKILL_DIR}/scripts/gen_random_id.py \
  --parent "{WORKSPACE}/operations_manual/hierarchy/category_<ID>/subcategory_<ID>" \
  --prefix "entry_" \
  --ext ".md"
```

如只需要 8 位随机 ID（不含前缀/扩展名），加 `--id-only`。
