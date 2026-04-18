## 子 Agent 能力自检与跨平台适配

批量写入的第四步（分片写入）开始前，主 Agent **必须** 先完成以下自检，判断当前宿主是否支持子 Agent 并行。

---

### 自检步骤

1. **检查当前可用工具列表**，确认是否存在以下任意一种「独立子会话 / 子代理」能力：

| 宿主平台 | 子 Agent 工具 | 说明 |
|---------|-------------|------|
| OpenClaw | `mcp__openclaw__sessions_spawn` + `mcp__openclaw__sessions_send` | 通过 MCP 创建独立会话，spawn 后可异步监听 `Subagent finished` 信号 |
| Cursor | `Task`（subagent_type = `generalPurpose`） | IDE 内置子代理，通过 prompt 参数传递指令，返回执行结果 |
| Trae / 其他 IDE | 以宿主文档为准 | 若宿主提供等价的「独立子会话」或「子任务」工具，视为可用 |

2. **判定结果**：
   - 上述工具中**任一可用** → 判定为 **支持子 Agent**，走 **并行路径**
   - **均不可用**（未出现在可用工具列表中） → 判定为 **不支持子 Agent**，走 **顺序分片路径**

---

### 并行路径 vs 顺序分片路径

| | 并行路径 | 顺序分片路径 |
|---|---------|------------|
| 分片策略 | 与策略 A/B 完全一致 | 与策略 A/B 完全一致 |
| 执行体 | 每个分片启动一个子 Agent | 主 Agent 按分片**顺序**执行（每次只处理一个分片） |
| 分发文件 | `.dispatch_*.json`（子 Agent 读取） | `.dispatch_*.json`（可选，便于核对） |
| 回报文件 | 每个子 Agent 写 `.result_*` | 主 Agent 每处理完一个分片写一份 `.result_*`（格式相同） |
| 目录隔离 | 子 Agent 间天然隔离 | 主 Agent 按分片切换工作目录，同样遵守隔离规则 |
| 索引重建 | 主 Agent 汇总后运行重建脚本 | 全部分片完成后运行重建脚本（逻辑一致） |

顺序分片路径下，主 Agent 扮演每个分片的「执行者」角色，写入逻辑与子 Agent 指令完全相同（写 entry、去重、不碰 index），唯一区别是串行而非并行。

---

### 可选工具声明指引

SKILL.md 的 `allowed-tools` 仅声明通用工具（Read、Write、Bash）。如需启用并行路径，请在**用户侧**的技能或规则配置中追加对应工具：

**OpenClaw 环境**：在 SKILL frontmatter 或 `.openclaw/config` 中追加：
```yaml
allowed-tools:
  - mcp__openclaw__sessions_spawn
  - mcp__openclaw__sessions_send
```

**Cursor 环境**：`Task` 工具为内置能力，无需额外声明，自检时确认可用即可。

**其他环境**：参照宿主文档，将等价子代理工具加入 `allowed-tools`。
