# 架构与演进边界

## 分层和数据所有权

框架 checkout 存引擎、通用 Skills、模板、测试和说明。每篇论文在独立目录维护 `workspace/` 与 `manuscript/` 两个并列部分。`workspace/state.json` 是节点、提案、问题、事件、任务和同步基线的权威快照；正文、原始材料、代码和数据保留独立可检查文件。不要在不同数据库/Markdown 表格中维护互相竞争的同一研究状态。

| 用户要求的状态 | 实现位置 |
|---|---|
| Research & Logic | question/hypothesis/argument/section/claim 节点；research/idea-evaluation.md |
| Sources & Literature | source 节点；sources/searches、sources/snapshots |
| Evidence | evidence 节点及支持/反驳/条件关系；evidence/ 附件 |
| Method & Analysis | method/result 节点；methods、data、results |
| Rules | rule 节点；框架默认政策和用户专属政策 |
| Figures & Tables | figure 节点；原始数据、运行记录与 manuscript/figures |
| Decisions & History | decision 节点、事件哈希链、history/、非证据 memory.md |
| Sync State | 按章节的同步基线、提案、冲突、语义复核问题 |

## 执行闭环

```text
新问题/新文献/新数据/反馈
 → Researcher（发现）
 → Source Policy（原始来源与核验边界）
 → Knowledge & Evidence（支持/反驳/条件）
 → Logic & Methodology（问题、整体论证、设计和推断）
 → 变更提案 + 依赖影响分析 + 作者批准
 → Writing / Figure（可追踪输出）
 → Manuscript Sync（三方同步与语义复核）
 → Reviewer / Rules（机器检查 + 独立领域审查）
 → cycle 生成下一轮 Skill 任务
```

CLI 管确定性状态和边界；Skills 指导授权 AI 完成语义工作；人负责研究选择、原文核验、执行授权和最终责任。不会启动无界后台代理。`rw ai run` 是一次受限 JSON 调用；浏览器/实验/多步编排应由有工具的宿主实际执行并保留记录。

## 依赖方向与影响传播

`depends_on` 表示“本节点依赖哪些节点”。传播从变化节点向所有依赖它的节点闭包扩展；遍历具有环保护。例如：

```text
source → evidence → claim → section / figure
question → hypothesis → argument → section
method → result → source/evidence → claim
```

Evidence 中的 `data.claim` 表示其评价对象，同时 Claim 的依赖包含 evidence；不要为该语义关联额外制造依赖环。显示/导出 Evidence Matrix 应从状态生成视图。

规则更新按全局影响处理。删除或改变依赖时，提案对新旧依赖做保守影响评估。未声明的关系不会被图自动发现；Logic/Sync 必须检查摘要、讨论、结论与图注的语义联系。循环依赖虽然不会卡死算法，仍可能是论证缺陷。

## 写入、审批与恢复

提案保存 base_fingerprint；Markdown 写入另外带 expected_sha256。批准前发现资料已变化即拒绝过期提案。写入有单写者锁、状态哈希并发检查及事务日志；中断后显式 recover，遇到中断后新增的本地编辑则停止。不会自动清理被其他活跃进程持有的锁。

事件包含 previous/hash，可发现普通篡改；用户有文件系统权限时能重写整个历史，因此它不构成防篡改认证系统。权限、签名与审计需要未来的独立安全基础设施。

## 同步与质量门

Markdown 章节有稳定 ID，保留 base/workspace/manuscript 三份内容。一侧变化生成同步提案，两侧冲突需要明确选择。Manuscript 回流或标记外编辑产生语义复核问题；不靠简单词替换自动判断所有因果关系。

机器检查覆盖结构、引用键、原文摘录/哈希、证据适用指纹、执行收据、图表来源、占位内容、待办和同步完整性。最终还需八个领域的独立人审及作者发布声明。任何关键内容/框架资产变化使旧快照声明失效。

## 扩展接口

`model.py` 定义节点和版本；`store.py` 管事务；`workflow.py` 管提案/证据；`sync.py` 管格式适配；`analysis.py` 管执行收据；`adapters.py` 管网络；`review.py` 管问题与导出；`skills.py` 管任务包/路由；`upgrade.py` 管资产；`dashboard.py` 管只读视图。

新增数据库适配器先只产生带来源的候选记录。新增稿件适配器必须保留稳定 ID、外部编辑、三方冲突和恢复测试。新增 Schema 版本需先提供已用项目迁移/回滚测试；当前对未知版本直接拒绝，绝不重建用户数据。新 Skills 注册方式见 [SKILLS](SKILLS.md)。

本版存储刻意保持 JSON/Markdown 可读与可迁移。未来可在相同领域契约外增加 Web UI、签名审批、数据库、多文档适配和有边界的任务执行器，保持用户数据所有权与原文证据边界不变。
