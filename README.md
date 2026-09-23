# AI Research Workspace

维护整篇论文的研究状态、论证、证据、方法和稿件，并在修改后检查全局影响。

**Workspace 管研究；Skills 管过程；Manuscript 管表达；Sync 管双向变更；Reviewer 管质量门。**

本项目提供可运行的本地 Python 引擎、9 个可修改的 Agent Skills、Markdown 模板、独立审核流程和增量更新。AI 推理通过你已授权的 coding agent、手动任务包或可选 API 完成。默认不调用模型、不联网、不上传论文。

## 1. 仓库里看这三个入口

```text
AI_Research_Journey/
├── aiworkspace/                 # 所有框架代码、Skills、模板、测试和详细文档
├── update_aiworkspace.py        # 本地已使用项目的增量更新入口
└── README.md                    # 从零开始的使用说明（本文件）
```

仓库原有 Vue 应用及其文件保持保留，与 AI Workspace 无运行依赖；隐藏的 Git/CI 配置负责版本管理和测试。AI Workspace 无需运行 npm。

**框架仓库与论文项目分开。** 初始化后的论文项目在仓库外，内部结构为：

```text
my-paper/
├── START_HERE.md                # 新作者、新 AI 会话从这里读起
├── AGENTS.md / CLAUDE.md        # 会话规则与操作边界
├── workspace/
│   ├── state.json              # 研究问题、论证图、Claims、提案、问题、同步状态
│   ├── research/               # 已填写的 Idea Evaluation
│   ├── sources/ / evidence/    # 原始来源、检索记录、证据附件
│   ├── methods/ / data/ / results/
│   ├── rules/ / figures/ / history/ / sync/
│   ├── skills/ / templates/    # 可更新的框架默认资产
│   └── memory.md / reports/    # 非证据交接记忆、审查报告和任务包
├── manuscript/                 # 正式 Markdown 稿件、图、补充材料
└── .rw/                        # 更新基线、事务和本地备份
```

一个框架安装可以维护多篇论文。不要把真实论文写进本公共仓库，不要重新初始化已有论文。

## 2. 安装并先跑一遍演示

需要 **Python 3.11 或更新版本、Git**。Python 运行时无第三方依赖；安装阶段需要 pip、setuptools、wheel。首次安装可联网下载构建工具。以下命令在终端执行。

### macOS / Linux

```bash
git clone https://github.com/729149195/AI_Research_Journey.git
cd AI_Research_Journey
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-deps --no-build-isolation -e ./aiworkspace
rw doctor
rw demo ../research-demo
```

### Windows PowerShell

```powershell
git clone https://github.com/729149195/AI_Research_Journey.git
cd AI_Research_Journey
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .\aiworkspace
.\.venv\Scripts\python.exe -m research_workspace doctor
.\.venv\Scripts\python.exe -m research_workspace demo ..\research-demo
```

Windows 其余命令中的 `rw` 可替换为 `.\.venv\Scripts\python.exe -m research_workspace`，`python` 替换为 `.\.venv\Scripts\python.exe`，无需更改系统脚本执行策略。

`doctor` 应显示 9 个 Skill 契约通过。`demo` 会实际计算 12 组人工数据、生成图表、建立证据链、进行双向同步、测试更新/回滚、执行质量门并导出演示工作包。

打开 `../research-demo/workspace/reports/dashboard.html` 查看离线看板；查看 `walkthrough.json` 了解实际步骤。示例使用合成数据，人工核验/审核声明均标记为模拟，不能作为真实研究或投稿。

目录已存在且非空时 demo/init 会拒绝覆盖；重跑请换一个新目录。

## 3. 创建自己的论文项目

以下示例继续在仓库根目录、已激活的虚拟环境中执行。

```bash
rw init ../my-paper --name "我的论文项目" --author "你的姓名"
rw --project ../my-paper status
rw --project ../my-paper review
```

新项目 `review` 返回 `blocked` 和退出码 1 属于预期：问题、证据、正文还未完成。请先填写：

- `../my-paper/workspace/research/idea-evaluation.md`：研究想法和验证计划。
- `../my-paper/workspace/rules/project-policy.md`：实际核查过的导师、机构、期刊、AI 使用、隐私、术语等规则，附来源与日期。
- `../my-paper/workspace/memory.md`：交接事项、未解决问题与下一步；它不充当证据。

Idea Evaluation 已从上传的十页 PPT 转成 Markdown，保留原文与可填写工作表，原始可视化设计问题仍在。新增 Workspace 字段有明确标记，无额外虚构评分标准。PPT 二进制文件不发布。

**填写 `research/`，保留 `templates/` 为空白框架模板。** 这样后续更新模板不会覆盖你已经填写的研究。

## 4. 让 AI 真正进入这个项目

### 推荐：使用有文件和终端能力的 coding agent

在你的论文目录安装宿主需要的 Skill 副本，二选一：

```bash
rw --project ../my-paper skills install --target .agents/skills
# 使用 Claude Code 时改为：
# rw --project ../my-paper skills install --target .claude/skills
```

在 **my-paper 根目录**打开你已授权的宿主，确认宿主能发现这些 Skills。模型账号、工具权限和联网权限由宿主管理；复制 Skills 不会自动获得这些权限。把下面这段作为新会话的第一条任务：

> 请读取 START_HERE.md、AGENTS.md、workspace/state.json、项目规则和已填写的 Idea Evaluation。先运行 status、sync status、review，说明当前研究状态。使用 idea-evaluation 与 logic-methodology 检查研究问题、贡献、方法和证据缺口，必要时比较两个或三个可行方案。所有实质修改先生成带 base_fingerprint 的 JSON 提案，展示影响范围，由我批准。不要替我核验证据、签署人工审核，或把预期结果写成已完成实验。

### 普通聊天模型：用任务包传递上下文

```bash
rw --project ../my-paper packet idea-evaluation --task "审查研究想法，指出缺失证据和下一步验证"
```

命令返回 JSON 文件路径。把有权传输的任务包交给模型，要求按包内输出契约返回提案。任务包本身不表示模型已执行研究。大项目可加 `--focus CLM-001`，保留该节点的上下游关系。

可选的单次 API 调用、模型配置和隐私边界见 [Skills 与模型接入](aiworkspace/docs/SKILLS.md)。完整 coding-agent-host / 真实模型效果基准尚未运行。

## 5. 从提案到确认，再同步稿件

仓库包含可执行的第一份草稿提案。它只提出研究问题，不声称已有证据：

```bash
rw --project ../my-paper propose aiworkspace/examples/first-proposal.json --actor ai-session
```

把返回的实际 `PROP-...` ID 替换进以下命令。先查看，再由作者批准：

```bash
rw --project ../my-paper show PROP-ID
rw --project ../my-paper apply PROP-ID --actor "你的姓名" --approve --note "已核对研究问题的对象和任务范围，当前保留草稿状态，后续验证重要性与文献依据。"
```

`upsert` 是完整节点替换，AI 必须先读旧节点并保留仍有效字段；提案过期时重新生成。原文证据核验、分析执行和最终审查是独立步骤，见 [完整使用教程](aiworkspace/docs/GETTING_STARTED.md)。

日常循环：

```bash
rw --project ../my-paper sync status
rw --project ../my-paper sync propose --actor sync-agent
# 查看并批准实际同步提案后：
rw --project ../my-paper review
rw --project ../my-paper cycle --actor coordinator
rw --project ../my-paper dashboard
```

没有待同步内容时 `sync propose` 会说明已经一致。两侧都改过时暂停并要求显式解决冲突。导师将“导致”改成“相关”会留下语义复核任务，接着由 Logic/Evidence 检查 Claim、摘要、讨论、结论与图注。`cycle` 根据问题生成下一轮 Skill 任务，不会开启隐蔽后台循环。

## 6. GitHub 更新后，增量更新已使用的项目

先结束正在写论文的 AI/编辑器任务，并做好研究数据备份。在框架仓库根目录执行：

```bash
python update_aiworkspace.py --project ../my-paper --check
```

查看 `target_commit`、代码差异、资产差异和冲突。确认后执行：

```bash
python update_aiworkspace.py --project ../my-paper --apply --actor "你的姓名"
```

需要严格锁定刚才预览的版本时，加 `--expected-commit`，值为实际返回的完整 SHA。上游在预览后变化时会停止：

```bash
python update_aiworkspace.py --project ../my-paper --apply --actor "你的姓名" --expected-commit 完整目标SHA
```

更新策略是 **旧默认 / 当前本地 / 新默认三方比较**。本地独有修改保留；不重叠修改合并；重叠冲突需指定保留本地或采用上游。稿件、证据、原始数据、方法代码、结果、研究状态、已填写工作表和项目专属规则均不作为框架资产覆盖目标。

保留 `.rw/framework.json`；它是旧默认基线。更新产生 `.rw/backups/UPDATE-....json`，可回滚受管理资产；它不替代完整研究备份，也不会回退 Python 引擎。

```bash
rw --project ../my-paper upgrade history
rw --project ../my-paper upgrade rollback UPDATE-ID
```

完整冲突处理、断电恢复、多个论文项目、旧目录迁移、离线更新及引擎恢复见 [增量更新说明](aiworkspace/docs/UPDATING.md)。不要用重新 `init` 或复制新模板覆盖旧论文来升级。

## 7. 验收、边界与后续维护

[交付与验证记录](aiworkspace/DELIVERY.md) 区分实际运行的本地测试、GitHub CI 和未执行的真实模型/科研评估。可自行复测：

```bash
python aiworkspace/scripts/run_tests.py
python aiworkspace/scripts/smoke_root_update.py
python aiworkspace/scripts/check_docs.py
```

本版原生同步格式为带稳定章节 ID 的 Markdown；Word/LaTeX/Overleaf 无损往返、多人实时数据库、自动全文获取、真实模型效果认证不在已实现范围内。论文质量门要求实际原文核验和独立审核；机器通过不代表科学有效性或期刊接收。

修改框架与扩展接口：[架构](aiworkspace/docs/ARCHITECTURE.md) · [数据契约](aiworkspace/docs/SCHEMA.md) · [Skills](aiworkspace/docs/SKILLS.md) · [贡献指南](aiworkspace/CONTRIBUTING.md) · [安全边界](aiworkspace/SECURITY.md) · [English quickstart](aiworkspace/docs/QUICKSTART_EN.md)。

代码与原创文档采用 [MIT](aiworkspace/LICENSE)，上传模板原文及紧密改编部分保留原权利，不额外授予许可。对外再分发模板前请确认原权利人的许可。

### 原有 Vue 应用

原应用文件保持保留。其原 README 的局域网启动命令为 `npm run dev -- --host`；它与上面的 Python Workspace 独立。
