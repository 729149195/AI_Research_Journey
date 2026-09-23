# 架构与扩展点

## 一、三个实体与一条受控工作流

框架包维护通用程序、Skills、空模板和更新机制；论文项目保存具体研究；Manuscript 与 Workspace 在论文项目中并列。AI 宿主可替换，研究状态不依赖某次聊天。

```text
Human / authorized coding agent / optional JSON API
                       ↓
                Bounded Research Skill
                       ↓
           Proposal + dependency impact
                       ↓
                Explicit approval
                       ↓
       Workspace ↔ Three-way Sync ↔ Manuscript
                       ↓
        Independent context + machine checks
                       ↓
             Issues / next-Skill tasks
                       ↓
       Current-snapshot human review + author release
```

这是一套可停止、可审查、可恢复的状态流程。`cycle` 只分派任务，不执行无限代理循环。工具输出、模型输出和用户决定分别记录，不把任一层直接当成科学事实。

## 二、模块职责

| 模块 | 职责 |
|---|---|
| model.py | schema、节点契约、稳定 ID、规范化哈希、可终止的依赖闭包 |
| store.py | 安全路径、流式文件哈希、UTF-8 边界、写锁、乐观并发、恢复日志 |
| workflow.py | 提案/批准/拒绝、联合前后依赖图、影响问题、核验声明 |
| sync.py | 稳定章节标记、上次同步基线、三方比较、冲突与语义复查 |
| analysis.py | 明确授权的本地 Python 运行、方法/代码/输入/输出追踪 |
| review.py | 完整性检查、独立领域声明、指纹绑定质量门与导出 |
| skills.py | Skills 读取/安装、上下文约束、任务包、问题路由与去重 |
| adapters.py | 显式联网的 Crossref 发现和一次 JSON 模型请求 |
| upgrade.py | 只更新默认资产的三方合并、备份、恢复及保守回滚 |
| scaffold.py | 新项目初始化、用户副本、研究/稿件并列布局 |
| dashboard.py | 转义后的离线只读 HTML 快照，不提供写入服务器 |
| demo.py / cli.py | 合成端到端演练和命令入口 |

## 三、八类状态的落点

Research & Logic 使用 question、hypothesis、argument、claim、section；Sources 使用 source 与实际查询日志；Evidence 使用独立 evidence；Method & Analysis 使用 method、result 与外部文件；Rules 使用项目政策与 rule；Figures & Tables 使用 figure 记录和真实生成结果；Decisions & History 使用 decision 与事件；Sync State 使用章节基线、提案、问题和待办。

`workspace/state.json` 是这些实体的权威快照，Markdown 原文、数据、代码与稿件保存在独立文件。不要再建立一份独立可编辑、却不与 state 同步的 Claim 清单。Evidence Matrix 和 Argument Map 应作为规范状态的视图或受控提案产物。

## 四、依赖图与科学推断

节点 `depends_on` 指向它依赖的上游。影响从上游传播到使用者：Source → Evidence → Claim → Section/Figure。证据对 Claim 的支持/反驳关系同时存于 evidence.data；Claim 依赖相关 Evidence，核验收据绑定 Claim 文本、推断强度和范围。

提案用修改前与修改后依赖的联合图做影响分析，删除一条旧依赖不会隐藏原来的下游影响。规则改变保守地触发广泛复核。算法用 visited 集合处理循环，避免无限遍历；它不能证明逻辑无循环论证或科学推断成立。

没有登记的自然语言关系不能由机器凭空理解。稿件回流一律产生语义复查；因果/相关、否定、范围、数值和比较对象的变化，要交给 Logic/Evidence 与作者检查全部受影响解释。

## 五、状态变更与核验

节点 draft/confirmed/retired 表示项目中的决策状态。source/evidence 的 verification 独立记录实际核验人的声明、时间、备注和相关哈希；confirmed 不自动等于来源已经核验。

提案 pending → applied/rejected。提案绑定创建时研究指纹；研究改变后旧提案失效。upsert 是完整节点替换，write 仅支持受限制 Markdown 和期望文件哈希。普通提案不能生成验证收据或实际运行证明。Result 还需匹配引擎执行事件。

文件、Claim 强度/范围或研究政策变化后旧证据/审批需要重新检查。AI 能提出变化，不能伪造核验、审批或作者决定。

## 六、并发、恢复与安全边界

Store 用原 state 文件哈希检测并发状态变化，文件写入另检查 expected_sha256。单文件使用原子替换，多文件先写恢复日志。中断后需显式 recover，恢复过程中发现新用户改动会停止。

这是本地单写者模型，不是多人实时数据库。事件哈希链用于发现意外/不一致修改，不抵抗拥有整个目录写权限的恶意操作者。actor 名字和 --human 是责任声明，不认证身份。更强审计需要服务端权限、签名和不可变存储。

研究指纹纳入引擎版本、项目配置、节点、问题、研究/稿件文件及入口政策。自动报告不进入指纹，避免生成报告本身使声明失效。未处理提案、重大问题和同步状态另外参与质量门。

代码执行并未沙箱化；上游更新 apply 表示明确授权安装该版本代码。白名单资产更新不能替代对上游代码本身的供应链审查。

## 七、如何扩展

新增 Skill：写清触发、输入、流程、输出、失败边界和评测，修改 SKILLS 注册、release manifest、版本和测试。不要把某个宿主的工具名当成全体用户都有的能力。

新增数据库：独立 adapter 保留查询/时间/过滤/原始响应/覆盖局限，默认禁网，结果先进入未核验 source。加去重、格式错误、超时、权限和隐私测试。

新增稿件格式：适配稳定段落/章节 ID 和三方冲突语义。Word Track Changes、LaTeX、Overleaf 不可用整文件覆盖冒充无损同步；当前仅 Markdown 原生支持。

新增数据 schema：先实现明确、带备份和失败恢复的迁移，准备真实旧项目 fixture，验证信息和 ID 不丢失。当前未知 schema 会拒绝，不能放宽检查后猜测数据转换。

新增可执行规则：不支持的规则类型必须明确阻塞。自动匹配到几个关键词不能被说成完成伦理/法规/期刊合规审查。

版本发布必须同时考虑新建项目与已使用项目。验收核心是旧研究继续可读、可运行、可审查、可回退，而不仅是新页面能显示。
