# 交付与实际验收记录

版本 0.1.0；Schema 1；验证日期 2026-09-23。本次提供可运行的本地框架与通用研究 Skill 契约。GitHub 项目入口为 aiworkspace/、根目录 update_aiworkspace.py 和 README.md；原 Vue 应用保留。

## 实际执行的本地验证

Linux / Python 3.13.5。原有引擎和两份单元测试从已提交源码恢复，逐文件核对 Git blob SHA 后测试；新增公共更新入口与文档在本次完善。

| 验证 | 结果 | 记录 |
|---|---|---|
| 完整单元/回归测试 | 65 项，0 失败、0 错误、0 跳过 | [unit-tests.json](verification/unit-tests.json) |
| 已用项目实际 Git 更新 | 当前目录与旧目录迁移两种场景均通过；包含实际 fetch/fast-forward/venv 安装 | [root-update.json](verification/root-update.json) |
| 干净 wheel 安装 | 全新 venv，在源码目录外 doctor 成功，9 个 Skill 契约通过 | [installed-doctor.json](verification/installed-doctor.json) |
| 完整合成研究演示 | 实际分析、证据链、双向同步、质量门、更新/回滚、演示导出通过 | [installed-demo.json](verification/installed-demo.json) |
| 文档与分发契约 | 本地相对链接、受管资产、14 个场景覆盖、无 PPT 二进制 | [docs.json](verification/docs.json) |

更新演练验证：研究状态、稿件、已填写 Idea Evaluation、用户规则哈希保持不变；本地非重叠 Skill 修改与上游合并；重叠冲突显式解决；脏引擎和预览 SHA 变化阻断；回滚保护更新后新编辑；未知 schema 阻断；旧目录真实笔记仍可见。

演示实际计算12组人工配对数据，baseline mean 22.5、candidate mean 18.0、candidate-minus-baseline -4.5。图表为生成的 SVG，已渲染检查；只读 dashboard HTML 已在 Chromium 中渲染检查。所有示例来源、数据和人工审核声明明确属于模拟，不能用于真实投稿。

## GitHub CI 的独立状态

已配置 Python 3.11/3.13 工作流、wheel 安装演示、更新测试和报告工件。观察到的先前 run [35859490131](https://github.com/729149195/AI_Research_Journey/actions/runs/35859490131) 在任何 job step 执行前失败；可用日志未给出可确认原因。**该次 CI 没有运行测试，不记为通过。** 后续提交的实际工作流状态请查看仓库 Actions。本地验收与 GitHub CI 分开报告。

## 尚未验证/实现的范围

没有真实付费模型 API 或完整 coding-agent-host 效果基准；API 测试使用 mock，Skills 的14个行为场景标记 not_run。没有声称全网最佳 Skill、专家科研评审、统计有效性、期刊语言认证或投稿接收保证。

原生稿件同步是带稳定章节标记的 Markdown。Word/LaTeX/Overleaf 无损往返、身份认证、多人实时数据库和无界后台自主研究未实现。Crossref 适配器发现元数据候选，不自动获得全文或完成多数据库系统综述。

## 复测命令

从仓库根目录的专用 venv 执行：

```bash
python aiworkspace/scripts/run_tests.py
python aiworkspace/scripts/smoke_root_update.py
python aiworkspace/scripts/check_docs.py
rw demo ../a-new-synthetic-demo
```

研究选择、原文核验、代码执行授权与最终独立审核均由实际责任人完成。更新备份只保护受管默认资产，另行备份研究原文、数据、代码及稿件。
