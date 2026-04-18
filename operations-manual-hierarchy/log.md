# operations-manual-hierarchy 版本变更记录

## v1.8.0 - 2026-04-18

- 三级索引（根 / `category_*` / `subcategory_*`）的 `index.md` 格式由「双表（映射表 + 概述）」统一为**单表**，每行一条 entry，新增「相对路径」列（相对库根），方便 Agent 与人类直接定位文件
- 根级 `index.md` 新增统计头行（一级分类数、二级分类数、条目总数），取消分散的概述段落
- `generate_subcategory_index` 签名新增 `cat_dir_name` 参数以支持完整相对路径
- `directory-structure.md` 新增「库根目录卫生」章节：明确库根仅允许 `category_*` 目录与 `index.md`
- `SKILL.md` 注意事项新增「库根目录卫生」条目
- `index-formats.md` 示例全部更新为单表 + 路径列格式
- 批量流程收尾步骤新增「必须清理 `.dispatch_*.json` 与 `.result_*` 临时文件」硬要求，覆盖正常/失败/中断路径

## v1.7.0 - 2026-04-18

- 工作手册数据根目录从 `workbook/hierarchy` 重命名为 `operations_manual/hierarchy`
- 引入 `{WORKSPACE}` 路径占位符约定：所有文档中的绝对路径统一改为以 `{WORKSPACE}/` 为根的抽象写法，不再硬编码特定平台路径
- `rebuild_hierarchy_index.py` 默认探测路径更新为 `operations_manual/hierarchy`，新增 `WORKSPACE` 环境变量支持，移除 OpenClaw 硬编码路径
- 影子摘要库路径统一为 `{WORKSPACE}/memory/operations_manual_shadow_index.md`
- `directory-structure.md`、`operation-modes.md` 增加 `{WORKSPACE}` 语义说明与 shell 用法提示

## v1.6.0 - 2026-04-18

- 跨平台子 Agent 适配：新增子 Agent 能力自检机制（`references/agent-platforms.md`），支持 OpenClaw、Cursor、Trae 等不同宿主；不支持子 Agent 的环境自动降级为主 Agent 顺序分片写入
- `allowed-tools` 默认仅声明通用工具（Read、Write、Bash），OpenClaw MCP 工具改为用户侧按需追加
- 二级分类目录索引：`subcategory_*/index.md` 由重建脚本自动生成，列出本目录下所有条目文件的 ID、文件名、标题、概述等信息，方便 Agent 快速定位
- `rebuild_hierarchy_index.py` 扩展：新增 `generate_subcategory_index` 函数，重建时同步生成三级索引（根 / `category_*` / `subcategory_*`）
- `directory-structure.md`、`index-formats.md` 更新：体现三级 index 文件结构与格式
- 作者更新为「掉渣的小桃酥」
- 版本变更记录从 SKILL.md 迁移至本文件

## v1.5.0 - 2026-04-18

- 重命名为 operations-manual-hierarchy
- 术语统一为一级/二级分类
- 索引改由 `rebuild_hierarchy_index.py` 脚本确定性生成（含概述区块），禁止手动编辑索引

## v1.4.0 - 2026-02-28

- 第四步新增「单一级分类场景」处理策略：当解析结果仅含一个一级分类时，改为按二级分类分片启动子 Agent 并行写入，主 Agent 统一汇总所有索引，保持并行优势同时确保并发安全

## v1.3.0 - 2026-02-27

- 第四步重构为子 Agent 并行写入架构，引入分发文件（`.dispatch`）与回报文件（`.result`）机制，主 Agent 负责预处理与汇总，子 Agent 按一级分类隔离并行写入，彻底解决主 Agent 串行写入丢失问题

## v1.2.0 - 2026-02-27

- 优化切块合并规则、分类自由推断机制、大批量文档的分组摘要确认交互、去重规则细化、错误处理补全

## v1.1.0 - 2026-02-27

- 新增文档批量解析存储模式（模式二），细化分类推断规则、错误处理和存储反馈格式

## v1.0.0 - 2026-02-26

- 初始版本：单条存储模式，分级索引结构（一级/二级分类 + 条目）
