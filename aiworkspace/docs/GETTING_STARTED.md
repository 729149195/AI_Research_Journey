# 从空项目到可审查论文

先按仓库根目录 [README](../../README.md) 安装并运行 demo。以下命令均在仓库根目录、专用虚拟环境中执行，论文实例为 `../my-paper`。Windows 可用 `.venv\Scripts\python.exe -m research_workspace` 替换 `rw`。

## 1. 第一次进入与每次交接

```bash
rw --project ../my-paper status
rw --project ../my-paper sync status
rw --project ../my-paper review
```

先读项目根目录 START_HERE.md 与 AGENTS.md，再读已填写工作表、项目规则和相关节点。`state.json` 是结构化研究状态；`workspace/memory.md` 与 decision 节点保存讨论理由和未完成事项，不作为事实证据。

初始化未完成的研究显示 blocked 正常。退出码 0 表示操作完成；1 表示相应检查存在阻塞；2 表示无效输入、冲突操作或错误。`rw COMMAND --help` 查看精确参数。

## 2. 评估 Idea 与建立论证

填写 `workspace/research/idea-evaluation.md`，按上传模板保留十部分：两部分 Introduction、Contributions、Related Work、Your Methods、Initial Results、Expected Results、Discussions、Expected Figures、Remaining Tasks。可视化研究保留 2–4 个编码/布局/交互方案，以及映射、任务、操作、线索、设计理由和替代方案问题。

原文在 `workspace/templates/idea-evaluation.original.md`。填写版中“Workspace 补充”是新增字段。没有实验时如实写“尚无结果”；预期结果留在预期章节。AI 比较可行方案后由作者选方向，理由进入 decision/history。

```bash
rw --project ../my-paper packet idea-evaluation --task "检查已填写工作表，比较验证成本不同的方案"
rw --project ../my-paper packet logic-methodology --task "建立问题、核心贡献、章节、Claim、证据和结论之间的逻辑图"
```

模型输出普通提案应包含 `summary`、任务包的实际 `base_fingerprint`、`operations`。完整节点/文件写入格式见 [SCHEMA](SCHEMA.md)。导入、查看、批准是分开的：

```bash
rw --project ../my-paper propose ../my-paper/workspace/reports/changes.json --actor ai-session
rw --project ../my-paper show PROP-ID
rw --project ../my-paper apply PROP-ID --actor "作者姓名" --approve --note "已逐项检查本次改动、证据边界和所有受影响章节，保留尚未解决的研究问题。"
```

ID 使用命令实际返回值。`upsert` 完整替换节点，不能遗漏原来的有效依赖和字段。批准接受修改，不表示证明了该 Claim。提案过期时重新读取状态并生成，不跳过并发检查。

## 3. 发现文献与形成证据

研究宿主可使用已授权的数据库和浏览器；本地内置 Crossref 元数据发现：

```bash
rw --project ../my-paper search --query "graph comparison visualization" --limit 10 --online --public-query --actor researcher
```

公开关键词会发给 Crossref。候选 source 保持未分类、未读原文状态，实际查询与返回内容保存在 `workspace/sources/searches/`。单一数据库不构成全面系统综述。获取原文需合法访问；摘要可用时应明确证据仅限摘要。

建立 source、claim、evidence 节点。必要逐字摘录保存为 UTF-8 文本，记录原始来源身份/版本/出版状态、页码或段落/表格定位、适用范围、限定条件，以及 supports/refutes/qualifies 关系。证据必须依赖其来源；Claim 依赖全部相关证据，保留反证和条件性证据。

实际核验者打开原始材料并检查后，分别运行：

```bash
rw --project ../my-paper verify SRC-ID --human --actor "核验者姓名" --note "已实际打开原文，核对出版身份、版本、更正撤稿信号、原文定位及本研究的适用范围。"
rw --project ../my-paper verify EVD-ID --human --actor "核验者姓名" --note "已逐字核对引用与上下文，检查限定条件和当前论点之间的支持、反驳或条件关系。"
```

AI 不得代替核验者签署。程序核对文件哈希、摘录和 Claim 指纹；它不验证签署人的身份，也不独立判定科学推断是否成立。新闻/博客通常仅用于发现；研究对象就是该文本时可用具体 `--primary-for` 说明原始材料角色。Claim 强度、范围或源文件变化后重新核验。

## 4. 运行分析与生成图表

先审查代码并建立 confirmed method 节点，声明 script、inputs、全新 outputs、args、seed、design；代码放在 `workspace/methods/`。完整实例可直接查看 demo 的 MTH-001 与分析脚本。

```bash
rw --project ../my-paper run MTH-001 --allow-exec --actor "作者姓名"
```

命令实际执行本地 Python，**没有安全沙箱**。仅运行已审查代码；未知脚本先在隔离环境审查。每次运行用新的输出路径，避免旧文件伪装成本轮结果。失败/超时后检查部分输出，程序不会把它们记成成功。

实际运行产生 result 节点和执行事件，保留方法、代码、输入、参数和输出哈希。后续数据或代码变化会使旧结果不再通过检查。方法的科学有效性、统计前提与推断范围需要独立审查。

图表作为 figure 节点登记：目的、Claim、来源/result、文件路径与哈希、caption、alt_text。定量图来自真实数据和代码；机制示意图区分已知证据与假设。生成文件后应实际检查标签、尺度、缺失值、误差含义与正文解释。

## 5. 写作与双向同步

```bash
rw --project ../my-paper packet writing-language --task "仅根据已确认逻辑与核验证据改写结果段落，保留限定条件"
rw --project ../my-paper sync status
rw --project ../my-paper sync propose --actor sync-agent
```

查看、批准实际提案。Markdown 章节必须保留稳定标记：

```markdown
<!-- rw:section SEC-ABSTRACT -->
## Abstract
正文……
<!-- /rw:section SEC-ABSTRACT -->
```

一侧修改可提出同步。双方都改过时展示 base/workspace/manuscript 三份内容，先手工合并，或在核对后显式选择：

```bash
rw --project ../my-paper sync propose --actor sync-agent --resolve SEC-ABSTRACT=manuscript
```

也可选 `=workspace`。标记之外的文本变化需要实际检查后加 `--acknowledge-outside`；仍会留下复核任务。新增/删除章节需同时协调节点和标记。已有 Word/LaTeX 请保留原件，逐节建立可追踪 Markdown 工作稿后再同步；本版没有无损自动导入。

语义变化需要重新检查 Claim、证据要求、方法、摘要、讨论、结论与图注。`rw impact CLM-ID` 根据显式依赖提供影响范围；遗漏的依赖仍需 AI/作者识别。文本一致不代表科学含义已获确认。

## 6. 问题闭环与独立审查

```bash
rw --project ../my-paper review
rw --project ../my-paper cycle --actor coordinator
rw --project ../my-paper packet reviewer --task "独立审查完整研究与稿件，报告实际检查范围和关键缺陷"
```

`review` 输出 `workspace/reports/final-review.json` 和 `.md`。`cycle` 生成并去重下一轮 Skill 待办。Reviewer 使用新上下文，任务包不包含作者的 decision 辩护叙事与 AI Memory。真实修复后逐项关闭问题：

```bash
rw --project ../my-paper issue resolve ISS-ID --actor "审核者姓名" --note "已检查实际修复、新证据和受影响章节，记录本问题的复核依据及剩余限制。"
```

不得为了消除红色状态关闭尚未解决的问题。机器检查通过后，独立审核者实际完成相应领域审查，再逐一声明。领域包括 research_logic、evidence_citations、method_statistics、figures_tables、writing_language、rules_compliance、ethics_ai、sync_consistency：

```bash
rw --project ../my-paper attest research_logic --human --actor "独立审核者姓名" --note "已独立检查当前问题、整体论证、核心推断与修复后的证据缺口，并记录具体审查范围。"
```

其他领域完成真实检查后分别声明；不要自动批量生成签字。作者最后执行：

```bash
rw --project ../my-paper attest author_release --human --actor "作者姓名" --note "确认本版本材料、证据与实际独立审核相符，并承担此提交工作包的作者责任。"
rw --project ../my-paper gate
rw --project ../my-paper export ../submission-package
```

导出目录必须全新。工作包包含 Markdown、图表、补充材料、CSL JSON 引用、审查、当前声明和哈希清单；需要继续按真实期刊要求转换格式。缺少审核或存在重大问题会阻断导出；内容修改使旧声明过期。本地姓名是责任声明，不能替代身份认证或科学审查。

## 7. 保存、协作与迭代

每次结束更新真实 decision/history 与 memory，运行 status、sync status、review，留下清楚的下一步。建议为论文实例另建**私有** Git 仓库，使用小分支和 PR；本地状态是单写者模型，不能多人同时修改 state.json。

自己的规则写 project-policy.md；定制内置 Skill 可编辑项目的 workspace/skills 后使用 `rw packet`。宿主副本已安装时注意副本与原位置分开：重新安装前先检查副本修改，不盲目用 `--overwrite`。框架贡献改源码资产并走测试；更新规则见 [UPDATING](UPDATING.md)。
