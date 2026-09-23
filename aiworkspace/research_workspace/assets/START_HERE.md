# 从这里开始 / Start here

这是一个论文项目实例。`workspace/` 管研究，`manuscript/` 管正式表达；框架程序位于另一个 Git checkout。第一次安装请看框架 README 与 docs/GETTING_STARTED.md，需要 Python 3.11+。

## 第一次使用

在本目录执行 `rw status`、`rw sync status`、`rw review`。新项目显示 blocked 很正常，因为问题、证据和论文尚未完成。`rw --help` 查看命令。

填写 `workspace/research/idea-evaluation.md`，阅读 `workspace/rules/project-policy.md` 并填入实际核查过的规则。空模板位于 `workspace/templates/`，后续会增量更新；不要把研究成果填进空模板目录。

使用 coding agent 时先让它读 AGENTS.md。`rw skills install --target .agents/skills` 或 `rw skills install --target .claude/skills` 安装宿主副本。生成初始任务包：`rw packet idea-evaluation --task "审查我已经填写的研究想法，指出证据缺口并比较可行方案"`。

## 日常循环

研究/读原文 → 提出证据与逻辑改动 → 作者批准 → 方法/图表/写作 → 双向同步 → 独立复审 → 下一步任务。

用 `rw propose changes.json --actor ai-session` 导入 JSON 建议，`rw show PROP-ID` 检查实际提案，作者再执行 `rw apply PROP-ID --actor NAME --approve --note "具体说明核查了哪些改动和影响"`。所有占位 ID 替换成实际返回值。

`rw sync propose --actor sync-agent` 提出同步，也要检查和批准。稿件含义变化会留下语义复核问题。`rw review` 写 JSON/Markdown 报告，`rw cycle --actor coordinator` 生成下轮待办；它不会在后台自动执行。

`rw dashboard` 生成 workspace/reports/dashboard.html，可用浏览器离线打开；页面只读，需要重新生成来刷新。

## 更新已使用项目

先结束正在写项目的编辑器/AI任务，并备份研究数据。在框架仓库根目录运行 `python update_aiworkspace.py --project 此项目路径 --check`，审查后使用 `--apply --actor 姓名`。可加 `--expected-commit 实际完整SHA` 锁定检查过的版本。脚本位于 aiworkspace/ 目录旁，默认跟踪 origin/main。

只更新项目默认资产时用 `rw upgrade check`，再 `rw upgrade apply --actor NAME --approve`。保留 `.rw/framework.json`；用 `rw upgrade history` 查看备份，`rw upgrade rollback UPDATE-ID` 回滚默认资产。更新不会覆盖稿件、数据、方法、证据或已填写工作表。完整冲突/恢复说明见框架 docs/UPDATING.md。

默认没有模型调用或外部搜索。真实论文需要实际原文核验、独立领域审查和作者责任声明；机器检查、示例数据和 AI 意见都不等于科学有效性。不要将未发表稿件、个人数据或密钥上传公共仓库。
