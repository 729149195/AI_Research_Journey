# AI Research Workspace

一个本地优先、可审查、可增量更新的论文研究框架。`workspace/` 保存研究状态与整体论证，`manuscript/` 保存正式表达，两者在每个论文项目中并列。

**第一次使用请读仓库根目录 [使用说明](../README.md)**；完整研究操作见 [入门教程](docs/GETTING_STARTED.md)。本目录是框架源码，可创建多个独立论文项目。请把真实论文放在框架 Git checkout 外面。

## 最小入口

需要 Python 3.11+ 和 Git。从仓库根目录建立专用虚拟环境后：

```bash
python -m pip install -e ./aiworkspace
rw doctor
rw demo ../research-demo
rw init ../my-paper --name "我的论文" --author "作者姓名"
rw --project ../my-paper skills install --target .agents/skills
```

`rw` 找不到时，使用同一虚拟环境的 `python -m research_workspace` 替代。演示目录须是新的，数据和审核声明都明确标为合成演示。初始化项目显示质量门 blocked 属正常情况。

## 框架模块

| 层 | 文件/目录 | 职责 |
|---|---|---|
| 研究模型 | `research_workspace/model.py` | 稳定 ID、节点、依赖与影响传播 |
| 事务与历史 | `store.py`、`workflow.py` | 提案、批准、哈希、并发保护与恢复 |
| 稿件同步 | `sync.py` | Markdown 章节三方比较与语义复核任务 |
| 来源与执行 | `adapters.py`、`analysis.py` | 显式授权的检索、模型调用、本地分析 |
| 质量门 | `review.py` | 完整性检查、独立审查声明与导出 |
| 可更新能力 | `assets/skills/`、`assets/templates/` | 8 个科研 Skills + Idea Evaluation |
| 增量更新 | `upgrade.py`、根目录 `update_aiworkspace.py` | 已用项目的受管资产三方更新、冲突与回滚 |
| 使用界面 | `cli.py`、`dashboard.py` | 命令行与离线只读状态页 |

所有上述相对 Python 路径位于 `research_workspace/`。核心运行时无第三方依赖；AI 模型、数据库、绘图环境由使用者按授权选择。

## 能力与边界

支持研究初始化、证据与 Claim 关系、变更提案/影响分析、实际分析执行记录、双向 Markdown 同步、审查待办、质量门、演示导出和增量更新。Skills 是可读指令与输入输出契约，需要有工具的 AI 宿主或显式配置的 API 执行语义任务。离线 CLI 不会自行理解任意论文、上网、调用模型或完成专家审查。

原生自动同步适配器面向带稳定章节标记的 Markdown。Word/LaTeX/Overleaf 无损往返适配、多人实时数据库、身份认证与持续后台研究均未实现。机器通过、语言流畅或作者声明都不构成科学有效性认证。

## 导航

[整体架构](docs/ARCHITECTURE.md) · [数据协议](docs/SCHEMA.md) · [Skills 选型与接入](docs/SKILLS.md) · [增量更新](docs/UPDATING.md) · [English quickstart](docs/QUICKSTART_EN.md) · [开发与迭代](CONTRIBUTING.md) · [安全说明](SECURITY.md) · [实际验收记录](DELIVERY.md)

PPT 已转换为 [逐页原文](research_workspace/assets/templates/idea-evaluation.original.md) 和 [可填写模板](research_workspace/assets/templates/idea-evaluation.md)，保留十部分与可视化设计要求。原附件不随仓库发布。
