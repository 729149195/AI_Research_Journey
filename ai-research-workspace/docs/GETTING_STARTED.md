# 从没有任何上下文开始

## 1｜先分清两个目录

**框架仓库**存 Python 程序、通用 Skills、模板、测试和说明；**论文项目**存你的研究和稿件。一个框架可创建多个项目。框架应放在 Git clone，论文项目应放在 clone 外面。不要每次升级都重新 init，也不要把旧论文整目录覆盖进新模板。

按 README 安装 Python 3.11+、建立专用虚拟环境并 `python -m pip install -e .`。本地流程没有第三方运行时依赖，大模型和 coding agent 由你单独选择。首次建议执行 `rw doctor` 和 `rw demo ../../research-demo`。demo 用真实计算过程处理合成数据，核验与审查声明都是明确标记的模拟。

Windows 无法运行激活脚本时，不必降低全局安全策略：直接用 `.venv\Scripts\python.exe -m research_workspace ...`；安装用这个解释器的 `-m pip`。Linux/macOS 对应 `.venv/bin/python`。`rw --help` 与 `rw 子命令 --help` 是实际参数说明。

## 2｜初始化与填写

后续示例假设终端位于框架目录 `AI_Research_Journey/ai-research-workspace`，虚拟环境已激活。

```bash
rw init ../../my-paper --name "我的论文项目" --author "作者姓名"
rw --project ../../my-paper status
rw --project ../../my-paper review
```

新项目 review 返回 blocked/退出码 1 正常，因为研究问题、证据和正文还没完成。退出码 2 表示无效输入或被拒绝的操作。init 拒绝覆盖非空目录。

先填写 `workspace/research/idea-evaluation.md`，它保留用户 PPT 的十部分；没有的结果明确写尚无结果。填写 `workspace/rules/project-policy.md` 中实际核查过的导师、机构、期刊、伦理、引用、AI 和术语规则，记录来源与日期。会话交接写进 `workspace/memory.md`，但 Memory 与决策记录都不是事实证据。

不要填 `workspace/templates/` 中的空模板；那里是后续可更新的框架资产。自己的内容放在 `workspace/research/`。

## 3｜让 AI 进入项目

### 有工具的 coding agent

```bash
rw --project ../../my-paper skills install --target .agents/skills
# Claude Code 改用 --target .claude/skills
```

在 **my-paper** 根目录打开你已授权的宿主，让它先读 START_HERE.md、AGENTS.md、政策和 state.json。检查宿主确实发现了项目 Skills；不同版本的宿主可能有差异。安装 Skill 只复制文字指令，不安装模型或执行远程脚本。

初次任务可直接使用：

> 用 idea-evaluation 审查我已填写的工作表，保留十部分和可视化设计问题。分别列出已知事实、待验证假设、实际证据和验证计划；必要时比较两个或三个不同方案，由我选择。先提出可检查的改动，不替我确认研究方向、核验证据或签署审查。

### 手动使用聊天模型

```bash
rw --project ../../my-paper packet idea-evaluation --task "评估研究想法并提出验证计划"
rw --project ../../my-paper packet logic-methodology --task "检查整篇论文的论证链和方法边界"
rw --project ../../my-paper packet reviewer --task "独立检查当前研究，不替作者辩护"
```

命令打印生成的 JSON 任务包位置。任务包包含指纹、政策、相关节点、未解决问题和输出约定；**它不是模型已经完成的答案**。只把有权发送的内容交给外部模型。大项目使用一个或多个 `--focus CLM-001` 缩小范围；超 200 KB 会拒绝，不悄悄截断证据链。Reviewer 包与 Writer 包分开，排除作者的 decision 说服叙事。

可选 API 模式见 [SKILLS](SKILLS.md)：默认关闭，需项目授权、允许的 HTTPS 主机、环境密钥和每次调用许可。它只完成一次 JSON 响应调用，不会假装自动访问浏览器、工具或实验。

## 4｜第一个可执行提案

在 `my-paper/workspace/reports/idea-proposal.json` 保存以下 JSON，再把问题换成真实研究问题。它保持 draft：

```json
{
  "summary": "明确研究问题的对象和任务，保持待确认状态",
  "operations": [
    {
      "op": "upsert",
      "node": {
        "id": "RQ-001",
        "kind": "question",
        "title": "交互式图结构比较中的局部差异定位",
        "status": "draft",
        "depends_on": [],
        "data": {
          "text": "在什么图结构比较任务中，现有视觉编码难以帮助分析者定位局部差异？",
          "assumptions": "重要性与新颖性尚待真实文献和任务分析验证。"
        }
      }
    }
  ]
}
```

```bash
rw --project ../../my-paper propose ../../my-paper/workspace/reports/idea-proposal.json --actor ai-session
# 下两行中的 PROP-ID 替换为上一条实际返回的提案 ID。
rw --project ../../my-paper show PROP-ID
rw --project ../../my-paper apply PROP-ID --actor "作者姓名" --approve --note "已核对研究对象、任务边界和未验证假设，当前仍保持草稿状态。"
```

批准意味着接受这次修改，不等于论点已获证明。依赖该问题的章节会产生复核问题。`upsert` 是**完整节点替换**，先读取旧节点并保留仍有效的字段。不得把它当成只更新一个字段的 patch。

Markdown `write` 提案需要完整新文本与原文件 SHA-256；新文件的 expected_sha256 为 null。提案不能直接写 state.json、执行脚本或生成验证收据。使用任务包时应回传其 base_fingerprint；研究已变化时必须重新生成，不能强套旧提案。

## 5｜来源发现与原文证据

使用宿主可用且已授权的学术数据库，或使用内置 Crossref 元数据发现：

```bash
rw --project ../../my-paper search --query "graph comparison visualization" --limit 10 --online --public-query --actor researcher
```

这会把公开关键词发给 Crossref。结果是 unclassified、未读原文的 source 候选；不是 Evidence，也不自动标成经过同行评议。查询与原始响应保存在 `workspace/sources/searches/`。单一接口的结果不能被描述成全面系统综述。

读完合法取得的原文，将必要的逐字摘录保存为 UTF-8 .txt/.md，并保留页码/段落/表格等定位及限定条件。建立 source、claim、evidence 节点，字段见 [SCHEMA](SCHEMA.md)。Evidence 记录 source、claim、quote、locator、scope、supports/refutes/qualifies；Claim 依赖所有相关证据，包括反证。

实际核验人打开原始来源，核对身份、版本、出版状态、更正/撤稿信号、定位、语义和适用性，然后才执行：

```bash
rw --project ../../my-paper verify SRC-001 --human --actor "核验者姓名" --note "已实际打开原始来源，检查出版身份、版本状态、定位与当前研究适用范围。"
rw --project ../../my-paper verify EVD-001 --human --actor "核验者姓名" --note "已逐字对照原文并检查限定条件，确认它与当前 Claim 的支持或限制关系。"
```

命令检查本地原文/引用/Claim 哈希，不能验证操作者的真实身份或自动判断论证蕴含。AI 不应替人执行 --human。来源或 Claim 文本/强度/范围改变后重新核验。新闻/博客通常仅用于发现；研究对象确实是该文本本身时，可以用具体 `--primary-for` 说明其原始材料角色。

## 6｜方法、分析与图表

先定义已确认 method 节点，声明 reviewed script、inputs、全新 outputs、args、seed、design，把实际代码放在 `workspace/methods/`。示例字段见 SCHEMA；完整可运行实例在 `rw demo` 生成的项目里。

```bash
rw --project ../../my-paper run MTH-001 --allow-exec --actor "作者姓名"
```

它实际运行本地 Python，**没有安全沙箱**。只运行审查过的代码；不可信代码应先隔离执行。新分析使用新的输出路径，避免旧文件冒充本轮结果；失败/超时后检查部分输出，不把它们记成成功。

成功会记录 code/input/output/method 哈希和实际执行事件。后来数据、代码、参数、方法或结果发生变化，旧结果不再满足质量门。定量图需要真实数据和代码；机制示意图区分证据关系与假设。Figure 节点记录目的、路径、哈希、Claim、result/evidence、caption 和 alt_text。创建图节点并不意味着机器已经完成视觉或统计审查。

## 7｜写作与双向同步

```bash
rw --project ../../my-paper packet writing-language --task "根据已确认的逻辑和证据起草结果段落，不扩大推断范围"
rw --project ../../my-paper sync status
rw --project ../../my-paper sync propose --actor sync-agent
```

对返回的提案 ID 继续 show/apply。仅一侧改变时提出向另一侧同步；两侧都改时暂停。例如确认采用导师改动后：

```bash
rw --project ../../my-paper sync propose --actor sync-agent --resolve SEC-ABSTRACT=manuscript
```

也可明确选择 `=workspace`，或先手动合并再检查。不要删掉 `<!-- rw:section SEC-ID -->` 标记。新增/删除章节时，要让节点与标记同时一致；当前适配器不会猜测结构。标记外的修改需 `--acknowledge-outside` 并触发复核。

导师把“导致”改成“相关”后，Sync 保存差异并创建语义复核问题；再由 Logic/Evidence 调整 Claim 强度、方法解释、摘要、讨论、结论和图注。不能只因为文本一致就关闭科学问题。

已有 Word/LaTeX 稿件暂不支持无损自动导入。先保留原件，在新项目中逐节建立对应节点和带 ID 的 Markdown 工作稿，核对后再使用原生同步；不要直接覆盖导致 ID 丢失。

## 8｜独立审查与投稿工作包

```bash
rw --project ../../my-paper review
rw --project ../../my-paper cycle --actor coordinator
rw --project ../../my-paper packet reviewer --task "独立审查完整论证、证据、方法及稿件一致性"
```

Review 输出 JSON/Markdown 报告；cycle 生成并去重下一轮 Skill 任务，不在后台自动执行。新增问题用 `rw issue add`；真实修复并复核后用 `rw issue resolve ISS-ID --actor NAME --note "具体修复依据与复核结果，至少二十个字符"`。不要为了“变绿”而关闭问题。

机器无重大阻塞后，实际独立审核者逐项审核并声明：research_logic、evidence_citations、method_statistics、figures_tables、writing_language、rules_compliance、ethics_ai、sync_consistency。例如：

```bash
rw --project ../../my-paper attest research_logic --human --actor "独立审核者姓名" --note "已独立检查当前问题、整体论证、关键推断与修复后的证据缺口，并记录审查范围。"
# 其他领域完成真实检查后分别声明，不能批量制造签字。
rw --project ../../my-paper attest author_release --human --actor "作者姓名" --note "本人确认实际审查、证据和稿件对应当前版本，并承担这份提交工作包的作者责任。"
rw --project ../../my-paper gate
rw --project ../../my-paper export ../../submission-package
```

导出目录须是新的，包含 Markdown、图表、补充材料、CSL JSON 引用、Review、当前声明和文件哈希。还需按真实期刊要求转换格式。内容变化使旧声明过期；写作者不能作为自己的独立审核者。本地名字不是身份认证，打包成功也不等于科研有效性认证或期刊接收。

## 9｜日常交接、多人使用与更新

会话结束保存实际决定/理由，更新非证据 Memory，然后运行 status、sync status、review。下一位使用者从 START_HERE.md 开始。团队建议给研究项目建立**独立私有 Git 仓库**，小分支/PR 审核；当前状态存储是单写者和乐观并发模型，不是多人实时数据库。不要在 state.json 冲突中直接全选 ours/theirs。

保留 `.rw/framework.json` 并另做真实数据备份；其他 .rw 运行时和增量备份默认忽略。[UPDATING](UPDATING.md) 说明 GitHub 增量更新、三方合并、冲突、恢复、回滚、多项目和分支切换。

## 10｜常见问题

| 现象 | 处理 |
|---|---|
| rw 找不到 | 激活正确虚拟环境，或用相同 Python 的 -m research_workspace |
| review 退出码 1 | 查看 blockers；这是质量门状态，不是程序崩溃 |
| stale proposal | 重新读取研究状态并生成提案 |
| sync conflict | 先比较双方研究含义，再明确方向或手动合并 |
| 证据失效 | 重开原文，检查文件、Claim 含义、定位和核验记录 |
| output already exists | 给下一轮分析使用新路径，保留上轮输出 |
| write.lock 存在 | 确认没有任何写进程后，才 `rw recover --clear-lock` |
| 研究写入中断 | `rw recover`，若有后续改动会拒绝覆盖 |
| 资产更新/回滚中断 | `rw upgrade recover`，有意外新改动时需先保留并手工处理 |
| 更新基线丢失 | 恢复 .rw/framework.json，不能猜一个新基线 |
| compatible API 不支持字段 | 不导入截断/非法结果；用手动任务包或单独适配器 |
