# Skills 的选择、使用与迭代

## 选择标准与实际审查范围

本项目提供 9 个项目专用 Skills：researcher、knowledge-evidence、logic-methodology、writing-language、figure-visualization、manuscript-sync、reviewer、rules-compliance、idea-evaluation。

选择看任务适配、原始来源可追踪性、输入/输出契约、证据和权限约束、可复现性、维护成本、依赖、许可证与隐私。这里没有覆盖所有候选、学科或模型的质量排名，不能据此声称“全网最佳”。

内置文本参考了下面已检查的公开工作流，并按本项目的状态、提案、同步与质量门重新组织。没有整库复制，也没有执行或自动安装第三方脚本。

| 上游参考 | 固定版本 | 已读范围 | 采用与调整 |
|---|---|---|---|
| K-Dense-AI/scientific-agent-skills | 49c6e97775eaa18ba791bebe23162a70ae601c18 | peer-review/SKILL.md 1–170 | 独立、证据优先、保密与人工负责 |
| 同上 | 同上 | scientific-writing/SKILL.md 1–150 | 有依据的写作，禁止虚构，写作与放行分离 |
| 同上 | 同上 | scientific-critical-thinking/SKILL.md 1–130 | 方法、偏差与推断；按学科选择框架 |
| 同上 | 同上 | scientific-visualization/SKILL.md 1–120 | 真实编码、数据变换可追踪、检查实际输出 |
| 同上 | 同上 | literature-review/SKILL.md 1–180 | 检索记录与原始来源；不强制 AI 图、固定数据库数或付费工具 |
| 同上 | 同上 | statistical-analysis/SKILL.md 1–140 | 设计、效应、不确定性；不把 p 值写成证明，不机械选择检验 |
| anthropics/skills | 34040c9c568585f6929bedeaad110ad08f079624 | skills/skill-creator/SKILL.md 1–110 | 明确触发、契约与迭代评测 |

完整仓库路径、blob SHA、采用理由和限制在 [skills.lock.json](../research_workspace/assets/skills.lock.json)。上述范围是部分 SKILL.md 阅读，不构成仓库安全审计、依赖审计或许可证授权。将来若真正 vendoring 代码，需要重新确认并保留相应许可证。

原始参考可直接检查：

- [K-Dense 固定版本](https://github.com/K-Dense-AI/scientific-agent-skills/tree/49c6e97775eaa18ba791bebe23162a70ae601c18/skills)
- [Anthropic Skill Creator 固定版本](https://github.com/anthropics/skills/blob/34040c9c568585f6929bedeaad110ad08f079624/skills/skill-creator/SKILL.md)
- [Agent Skills 格式](https://agentskills.io/specification)

外部 Skill 是工作流参考，不是支撑论文 Claim 的科研证据。

## Idea Evaluation

idea-evaluation 来自用户实际提供的 10 页 PPT。保留原模板的背景/问题、方法特色、贡献、比较与借鉴文献、2–4 个可视化编码/布局/交互设计、实际结果、预期结果/评价、局限、预期图表与剩余任务。

[逐页原文](../research_workspace/assets/templates/idea-evaluation.original.md) 与 [可填写模板](../research_workspace/assets/templates/idea-evaluation.md) 分开。新增 ID、证据状态、方案比较、决策和复查条件明确标注为 Workspace 补充。没有编造评分标准，也没有发布二进制 PPT。填写项目中的 workspace/research/idea-evaluation.md，空模板留在 templates 供更新。

## 安装到已有 coding agent

```bash
rw --project ../../my-paper skills list
rw --project ../../my-paper skills show logic-methodology
rw --project ../../my-paper skills lint
rw --project ../../my-paper skills install --target .agents/skills
# Claude Code 使用 --target .claude/skills
```

在 my-paper 根目录打开宿主，先读 START_HERE.md 和 AGENTS.md。目录约定参考 [Codex Skills](https://developers.openai.com/codex/skills/) 和 [Claude Code Skills](https://code.claude.com/docs/en/skills)。实际发现和执行取决于宿主版本、工作目录、权限及模型，不是复制文件后就完成了实际模型验收。

主副本是 workspace/skills；修改后重新安装到宿主需明确 `--overwrite`，先保存并比较宿主已有修改。已登记的宿主副本可随项目资产更新进行三方合并。不要在两个地方反复修改同一条规则却不说明哪一份是主版本。

## 不依赖聊天上下文的任务包

```bash
rw --project ../../my-paper packet logic-methodology --focus CLM-001 --task "检查该 Claim 的推断是否超出证据范围，并定位全部下游章节"
```

JSON 包含真实研究指纹、任务、Skill、政策、依赖闭包和输出契约。大于 200 KB 时明确拒绝，要求缩小 focus。包中记录不能代替尚未提供的完整原文、代码或实验；需要时由已授权宿主读取实际材料。

Writing 包过滤未确认/未核验证据和无有效支持的 Claim，并排除 decision；Reviewer 包附稿件、排除作者说服性决策历史和 Memory。不同上下文有助于分工，但同一个模型换会话不等于真正独立的专家。

普通模型结果必须回传 summary、base_fingerprint 和 operations，导入为 pending 提案。Reviewer 结果是待核查问题，不是人工批准。

## 可选 API 模式

默认禁用。先核查机构、期刊、数据许可与保密要求，再记录明确授权：

```bash
rw --project ../../my-paper ai configure --enable --host api.openai.com --actor "作者姓名" --note "已核查项目资料的外部处理权限、机构与目标期刊规则，并明确授权发送本次有界上下文。"
```

密钥使用进程环境变量 `RW_API_KEY`；不放在命令参数、仓库、图像、日志或研究笔记中。程序不自动读取 .env。使用自己账户实际可用、支持契约的模型：

```bash
rw --project ../../my-paper ai run logic-methodology \
  --task "审查已提供的设计与论证，不补造来源或结果" \
  --model YOUR_AVAILABLE_MODEL \
  --endpoint https://api.openai.com/v1/chat/completions \
  --allow-network
```

最小接口契约为 Chat Completions 的 messages、response_format=json_object、max_completion_tokens、store=false，以及完整 choices[0].message.content、finish_reason=stop。模型还必须回传任务指纹。参考 [官方接口](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)。其他 compatible 服务可能不支持全部字段，需要独立适配和测试。

这只执行一次无工具 JSON 请求，不自行浏览、运行实验或串行执行全部 Skills。模型结果截断、非法、过期或试图伪造收据时不接受。HTTPS 主机白名单、拒绝重定向、超时和响应大小限制不能替代数据处理合同；store=false 也不是零留存保证。POST 不自动重试，避免重复费用。

禁用外部 AI 时，执行 ai configure 并省略 --enable：

```bash
rw --project ../../my-paper ai configure --actor "作者姓名" --note "关闭此研究项目的外部模型处理，后续任何重新启用均须重新核查授权。"
```

## 迭代 Skill 的正确单位

一次修改解决一个清晰场景：触发条件、必需输入、合法输出、停止条件、失败示例与实际验收。更新 Skill metadata version、登记理由、CHANGELOG 和对应测试，使用 PR 审查。

确定性测试只能证明规则和状态操作；写作质量、科学论证和研究价值仍需模型/人工场景评测。[evals/scenarios.json](../evals/scenarios.json) 中未实际运行的条目必须保持 not_run，不能把模板 lint 或软件测试通过写成模型科学能力排名。
