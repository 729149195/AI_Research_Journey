# Skills：选型、接入与后续修改

## 已内置的 9 个工作流

| Skill | 负责什么 | 交付什么 |
|---|---|---|
| researcher | 规划、文献/工具发现、检索覆盖与 Source Policy | 查询记录、候选来源、工具比较、证据缺口 |
| knowledge-evidence | 读原文、保留定位和限定条件、反证 | Evidence Matrix 与精确 Claim 关系提案 |
| logic-methodology | 整篇论文论证、研究设计、统计、可复现分析 | 逻辑图、方法方案、边界、全局影响任务 |
| writing-language | 仅从确认逻辑/Claim/证据/规则写作 | 可审查正文和语言修改提案 |
| figure-visualization | 按任务选择工具、保留数据/代码/生成过程 | 图表规范、实际输出检查与追踪关系 |
| manuscript-sync | 双向差异、冲突、含义变化 | 三方同步提案和语义复核任务 |
| reviewer | 新上下文独立审查 | Critical Issues、Required Fixes、Final Review Report |
| rules-compliance | 核查机构/导师/期刊/伦理/AI/引用规则 | 规则注册、适用性、冲突和重新检查任务 |
| idea-evaluation | 按上传 PPT 的十部分审查研究方向 | 保留可视化设计问题的工作表与备选方案 |

源码在 `research_workspace/assets/skills/`。每个 SKILL.md 都有触发条件、Inputs、Workflow、Outputs、Boundaries 和 Evaluation。项目初始化会复制这些文件；后续按资产基线三方更新。

## 选型依据与可审计来源

查看 [锁定清单](../research_workspace/assets/skills.lock.json)，记录具体 commit、blob SHA、阅读范围、采用内容与不采用内容。选择标准为任务适配、原始证据追踪、研究完整性、输入输出清晰、可复现、可维护、许可/依赖透明、成本、隐私和失败处理。

已阅读 K-Dense 的 peer-review、scientific-writing、scientific-critical-thinking、scientific-visualization、literature-review、statistical-analysis，以及 Anthropic 的 skill-creator 部分主文件。内置的是适应该 Workspace 数据和审批契约的原创工作流，未把上游全部脚本和依赖捆绑进来。

上游固定版本：

- [K-Dense Scientific Agent Skills](https://github.com/K-Dense-AI/scientific-agent-skills/tree/49c6e97775eaa18ba791bebe23162a70ae601c18)，包含研究/写作/审核指导。
- [Anthropic skill-creator](https://github.com/anthropics/skills/tree/34040c9c568585f6929bedeaad110ad08f079624/skills/skill-creator)，参考显式契约与迭代评估。

采用证据优先、独立审核、真实执行记录和逐层写作检查。不采用强制付费工具、每篇综述必须 AI 生图、任意最低数据库数、机械统计分流或“p 值证明效应”等表述。阅读部分主文档不等于审查整个上游仓库；没有声称全网最优或运行过所有模型的对照基准。

截至 2026-09-23 核对的官方格式与宿主文档：[Agent Skills](https://agentskills.io/specification)、[OpenAI Skills 文档入口](https://developers.openai.com/codex/skills/)、[Claude Code Skills](https://code.claude.com/docs/en/skills)。实际发现路径、版本与权限以你正在使用的宿主为准；本工程未做每个宿主的实时兼容性验收。

## 三种使用方式

**有工具的宿主。** 在论文目录安装 `.agents/skills` 或 `.claude/skills` 副本，在论文根目录启动宿主并读 AGENTS.md。宿主实际完成检索/阅读/分析/写作后，把结构化修改导入提案。外部 Skills 和网页是待审查输入，不能覆盖本项目的安全/来源政策。

**任务包。** `rw packet SKILL --task "具体问题" --focus NODE-ID` 生成当前指纹、相关研究节点、适用规则和 Skill 契约。普通 AI 返回提案；Reviewer 返回问题。任务包有 200 KB 上限，超限提示收窄 focus，不会悄悄截断证据链。将未发表研究发给远程模型前必须有授权。

**可选 API 单次调用。** 以下示例中的主机/endpoint/model 都要改为你实际获准使用的服务。支持 Chat Completions 形状的 JSON 接口；供应商仍可能不支持某些参数，失败会明确报告。

```bash
rw --project ../my-paper ai configure --enable --host api.example.org --actor "作者姓名" --note "已核对本项目、数据许可和服务条款，授权向该主机发送本次所需的研究上下文。"
# 将 RW_API_KEY 设置到进程环境，不要写入仓库或任务文件。
rw --project ../my-paper ai run logic-methodology --task "审查 CLM-001 的推断范围" --focus CLM-001 --model 实际模型ID --endpoint https://api.example.org/v1/chat/completions --allow-network
```

API 模式不会自行浏览、安装 Skill 或执行工具；它传递限定上下文并接收 JSON。普通返回先成为 pending proposal；Reviewer 返回的是未核实 AI 问题，不能签署人工审核。allowlist、项目授权、环境密钥及逐次 `--allow-network` 同时成立才调用。拒绝重定向、超大/截断输出、错误指纹与过期上下文。

`store: false` 只是向服务发送的参数，不能保证第三方不留存数据。没有真实付费模型/API 验收；单元测试使用明确的 mock。

## 如何定制，哪些修改会被升级保护

仅针对某篇论文：编辑它的 `workspace/rules/project-policy.md`、`workspace/skills/NAME/SKILL.md`。宿主副本有独立路径，检查后手动同步或经批准重新安装；`--overwrite` 会覆盖相同宿主文件，请勿无检查使用。更新器会对已注册副本分别处理三方冲突。

面向所有使用者：在本框架修改 `research_workspace/assets/skills/NAME/SKILL.md`，更新版本/变更说明，添加行为场景，运行测试并提交。Skills 文档修改本身无需改变 Schema。

新增第十个自定义能力：在 assets/skills 新增符合格式的文件；注册到 `skills.py` 的 SKILLS/必要 ROUTES；在 release.json 添加受管目标；更新测试中的数量和角色覆盖。若要管理 SKILL.md 以外的资源，显式扩展打包与 owned 白名单，先写路径/删除/冲突/回滚测试，禁止用通配符开放整个研究目录。

## 评估与工具发现

[行为测试场景](../evals/scenarios.json) 覆盖九个 Skills；[评估说明](../evals/README.md) 区分格式契约、确定性软件测试和真实宿主行为评估。现有65项软件测试与实际 demo/更新演练不自动证明写作或模型推理质量。

Researcher 遇到未知任务时比较可用数据库、模型、统计/绘图工具或外部 Skill 的原始来源支持、可复现性、成本、许可证及信息流向。先记录建议并获得安装/付费/联网授权；不会不加审查拉取远程脚本或自动升级整套第三方依赖。
