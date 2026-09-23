# AI Research Workspace

**Workspace 管研究状态与整体逻辑 · Skills 管过程 · Manuscript 管正式表达 · Sync 管双向演进 · Reviewer 管最终质量。**

本地优先、证据驱动、可迭代的科研项目框架。它维护研究问题、假设、整体论证、Claim、证据、方法、图表、规则和稿件关系，通过提案与审批驱动修改，并提供专门面向“已经使用一段时间”的研究项目的增量更新与回滚。

**0.1.0 / research beta**：Python CLI、9 个可修改 Skills、独立研究状态、Markdown 双向同步、离线只读 Dashboard、可复现演练、测试及更新脚本。普通工作流和示例不需要 API Key。外部搜索、模型调用和本地方法执行都需要明确授权。现有仓库的 Vue 应用保持独立、不作修改。

## 1. 安装后先走通一次

需要 Python 3.11+ 和 Git。框架源码与自己的论文项目放在不同目录。

```bash
git clone --branch feat/ai-research-workspace https://github.com/729149195/AI_Research_Journey.git
cd AI_Research_Journey/ai-research-workspace
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell 改用：.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
rw doctor
rw demo ../../research-demo
```

功能合并到 main 后，可以直接克隆默认分支。`rw` 找不到时，用同一虚拟环境的 `python -m research_workspace` 替代。

用浏览器打开 `research-demo/workspace/reports/dashboard.html`，查看 `walkthrough.json` 和 `dist/demo-submission/`。demo 实际运行 12 对合成数据的分析、文件/引文校验、双向同步、项目升级/回滚和质量门。**其中的人工核验与审查声明全部标记为模拟，不能当成真实科学研究或专家评审。**

## 2. 开始自己的论文

```bash
rw init ../../my-paper --name "我的研究项目" --author "作者姓名"
rw --project ../../my-paper skills install --target .agents/skills
# Claude Code 使用：--target .claude/skills
rw --project ../../my-paper packet idea-evaluation --task "评估我已填写的研究想法，指出证据缺口并比较可行方案"
```

填写 `my-paper/workspace/research/idea-evaluation.md`。用你已授权的 coding agent 打开 **my-paper**，让它从 `START_HERE.md`、`AGENTS.md`、项目规则和 state.json 开始，不依赖之前聊天。建议第一条指令：

> 先阅读本项目入口和状态，运行 status、sync status 和 review。用 idea-evaluation 审查我的研究想法，保留未知项，比较可行方案。任何状态或稿件修改先出可检查的提案；原文核验、作者选择和最终审查由责任人实际完成。每次修改都检查影响范围、同步和复审。

[完整从零上手](docs/GETTING_STARTED.md) 包含第一个可用 JSON 提案、检索/证据/方法/写作/同步/审查的逐步操作和排错。[English quickstart](docs/QUICKSTART_EN.md) 面向其他使用者。

## 3. 大框架与目录边界

```text
my-paper/
├── START_HERE.md / AGENTS.md / CLAUDE.md
├── workspace/
│   ├── state.json              # 节点、依赖、提案、问题、审查声明、同步基线
│   ├── research/               # 已填写的 Idea Evaluation 与研究笔记
│   ├── sources/ evidence/      # 原始来源、检索日志、证据关系
│   ├── methods/ data/ results/ # 真实代码、输入与带哈希的运行结果
│   ├── rules/                  # 框架政策和用户拥有的项目政策
│   ├── skills/ templates/      # 可迭代 Skills 与可更新的空模板
│   ├── figures/ history/ sync/ # 图表规划、决策上下文
│   └── reports/ memory.md      # 复审、任务包、离线页面、会话交接
├── manuscript/
│   ├── main.md                 # 带稳定章节 ID 的正式 Markdown 工作稿
│   ├── figures/
│   └── supplementary/
└── .rw/
    ├── framework.json          # 必须保留的三方更新基线
    └── backups/                # 受影响框架资产的增量备份
```

研究逻辑：Question → Hypothesis/Core Idea → Overall Argument → Section/Claim → Evidence/Method/Result → Discussion/Conclusion。

依赖传播：Source → Evidence → Claim → Section/Figure。新增文献、改变方法或修改稿件后，检查全部下游，包含摘要、讨论、结论和图表。History/AI Memory 仅保存理由与上下文，不充当硬性事实来源。

[架构说明](docs/ARCHITECTURE.md) 和 [状态契约](docs/SCHEMA.md) 解释每个模块、扩展点和不能破坏的边界。

## 4. 已实现的闭环

| 环节 | 实现与边界 |
|---|---|
| Research | 明确任务、文献/工具发现、可选 Crossref 元数据搜索；新记录不自动成为 Evidence |
| Evidence | 原文定位、精确引文、支持/反驳/条件关系、来源与 Claim 断言哈希；需要实际人工核验 |
| Logic/Method | 12 类稳定 ID 节点、传递影响分析、显式方法与实际运行记录；机器不能替代领域判断 |
| Writing/Figure | 受确认状态约束的上下文、可审查修改提案、Figure–Claim–Run/Evidence 追踪 |
| Sync | 按章节基线进行三方 Markdown 同步；冲突暂停；稿件回流创建语义复核问题 |
| Review | 完整性检查、独立审查上下文、8 个领域声明及作者放行；内容变更使旧声明失效 |
| Iterate | Review 问题路由给下一项 Skill；保留状态、决策、任务和版本 |

“X 导致 Y”改成“X 与 Y 相关”会要求复核 Claim、证据要求及全篇解释。自动依赖定位加上明确的语义复核任务，不能被理解成机器已经证明所有自然语言推论正确。

## 5. Skills 选择与 PPT 转换

内置 **Researcher、Knowledge & Evidence、Logic & Methodology、Writing & Language、Figure & Visualization、Manuscript Sync、Reviewer、Rules & Compliance、Idea Evaluation**。每个 Skill 都有触发说明、输入、流程、输出、边界和评测场景，可独立修改。

本项目参考 K-Dense Scientific Agent Skills 与 Anthropic Skill Creator 的已检查部分，按证据约束、任务适配、可复现性、可维护性、依赖、隐私和成本选择，保留固定 commit、文件范围及采用/不采用理由。没有整库复制或自动安装第三方脚本，也没有宣称做过覆盖所有模型/候选的“全球最佳”排名。见 [Skill 说明](docs/SKILLS.md) 与 [来源登记](research_workspace/assets/skills.lock.json)。

用户 PPT 已转换为 [逐页原文 Markdown](research_workspace/assets/templates/idea-evaluation.original.md) 和 [可填写工作表](research_workspace/assets/templates/idea-evaluation.md)，保留 10 个部分、可视化设计问题及“问题—方法—收益”。Workspace 的新增字段单独标明，另保留 `idea_evluation.md` 拼写兼容入口。仓库不包含二进制 PPT。

## 6. 重点：本地用了很久，也能增量更新

在框架目录和已激活的专用虚拟环境中，先关闭正在写研究项目的 AI/编辑进程：

```bash
# 当前 PR 分支；只预览，不改研究文件
python scripts/update.py --project ../../my-paper --ref origin/feat/ai-research-workspace --check
# 检查差异后执行
python scripts/update.py --project ../../my-paper --ref origin/feat/ai-research-workspace --apply --actor "作者姓名"
```

合并并切换到 main 后，改用 `--ref origin/main`。如果采用 squash merge，先在干净 checkout 中正常切到 main，不能指望分叉历史被脚本强制重置。[UPDATING](docs/UPDATING.md) 有具体说明。

更新分两层：Git fetch + 只允许快进更新框架代码；项目资产更新器使用**旧默认版本 / 当前本地内容 / 新默认版本**进行三方合并。非重叠修改保留两边；冲突则整次暂停，允许明确保留本地或采用上游。

**绝不把已填写的研究、数据、代码、证据、用户项目政策或稿件当成模板更新目标。** 更新的是 `workspace/templates/` 的空模板；`workspace/research/` 的已填工作表原样保留。每次更新先备份受影响资产，支持恢复中断和受保护的回滚。

```bash
# 引擎代码已更新时，仅升级某个已有项目的默认资产
rw --project ../../my-paper upgrade check
rw --project ../../my-paper upgrade apply --actor "作者姓名" --approve
rw --project ../../my-paper upgrade history
rw --project ../../my-paper upgrade rollback UPDATE-实际备份ID
```

另有 `scripts/update.sh` 和 `scripts/update.ps1`。脚本不会自动 stash、hard reset、强推、覆盖冲突或猜测未知 schema 迁移。引擎安装和项目资产写入是两个步骤，部分失败会给出恢复说明。增量资产备份不能替代完整研究数据备份。

## 7. 验收、协作与当前边界

```bash
python -m unittest discover -s tests -v
python scripts/smoke_update_install.py
python scripts/check_docs.py
python -m compileall -q research_workspace scripts
```

[验收报告](docs/TEST_REPORT.md) 区分实际通过、未测集成和模型质量评测计划；GitHub 托管 CI 的实际状态以本分支/PR 的 Checks 为准。[维护说明](CONTRIBUTING.md)、[安全边界](SECURITY.md)、[路线图](docs/ROADMAP.md) 帮助继续迭代。

当前原生支持 Markdown，尚未实现 Word/LaTeX/Overleaf 无损同步、Zotero 连接器或多人实时协作。API 模式是一轮明确授权的 JSON 提案调用，有工具的多步过程交给已授权 coding-agent 宿主；不自带大模型或无限自动代理。Dashboard 是离线只读快照。本地 actor/--human 是责任声明，不能认证真实身份。机器检查、可重跑计算和声明均不构成科学有效性或期刊接收保证。

代码和原创 Skills 使用 MIT；用户上传模板的原文及紧密改编部分保留原权利，不擅自替原作者授权。不要向公共仓库上传未发表稿件、参与者数据或 API Key。
