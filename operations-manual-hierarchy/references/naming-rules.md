## 命名规则

### 随机 ID 生成规则

- 组成：小写字母 (a-z) + 数字 (0-9)，共 8 位
- 生成命令：
  ```bash
  cat /dev/urandom | tr -dc 'a-z0-9' | head -c 8
  ```
  或使用 Python：
  ```python
  import random, string
  ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
  ```
- 命名格式：
  - 一级分类目录：`category_<8位随机ID>`
  - 二级分类目录：`subcategory_<8位随机ID>`
  - 条目文件：`entry_<8位随机ID>.md`
- **每次创建前必须通过 Bash 确认 ID 不与现有目录/文件重名，若冲突则重新生成，最多重试 5 次**
