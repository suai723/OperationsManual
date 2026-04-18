# operations-manual-reader 版本变更记录

## v4.0.0 - 2026-04-18

- 技能包从 `workbook-reader` 重命名为 `operations-manual-reader`，与 operations-manual-hierarchy 命名风格对齐
- 库根路径统一为 `{WORKSPACE}/operations_manual/hierarchy/`，三级索引（根 / `category_*` / `subcategory_*`）与 hierarchy 完全一致
- 检索策略从串行瀑布（A→C）升级为**脚本驱动的多路完全并行**：索引 / 元数据 / 全文三路在 `parallel_retrieve.py` 中以 `concurrent.futures` 线程池真并行，向量路由 Agent 同轮并行发起（可选）
- 元数据路兼容无 YAML frontmatter 的 entry：无 `---` 块时记为 `yaml_absent`，不中断该路，合并时由全文路等补位
- 新增**全局渐进式读取兜底**：并行合并后关键词与（若有）向量双低置信时，从根 `index.md` 起按层渐进读取
- 新增**索引命中锚点渐进钻取**：grep 命中指向某目录或条目时从锚点向下读，不盲目全扫
- 新增**已读台账**：单次查询内防重复读取同一文件
- 向量路改为可选：仅宿主提供 `memory_search` 时启用，否则跳过不阻塞
- 移除对不存在的 `SOUL.md` 的硬依赖，改为「若有则遵守」
- `description` 按 skill-creator 规范优化，覆盖查询类典型句式与排除写入场景
- 作者更新为掉渣的小桃酥
- 变更记录从 SKILL.md 迁移至本文件
- 详细检索策略拆至 `references/retrieval-strategy.md`

## v3.0.0 - 2026-03-02

- 引入语义检索与影子索引机制（memory_search + workbook_shadow_index.md）
- 建立瀑布流降级策略（A → C 串行）
- 技能设计：Moly & Judy

## v2.0.0 - 2026-02-27

- 新增 `scripts/query_workbook.py` CLI 查询工具
- 支持概览浏览、分类展开、关键词搜索、条目直读、标签过滤、统计概览
