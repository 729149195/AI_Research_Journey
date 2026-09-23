# 已使用项目的增量更新、恢复与回滚

## 两层更新，分别保护

框架源码放在 Git clone；每个论文项目放在 clone 外面。框架更新获取新的程序、默认 Skills 和模板；项目更新把新默认资产与旧默认资产、本地修改做三方合并。`workspace/` 与 `manuscript/` 始终并列。

| 内容 | 处理 |
|---|---|
| 框架代码、文档、默认 Skills | Git 增量 fetch；仅允许干净 checkout 上的快进 |
| 项目 AGENTS.md、CLAUDE.md、START_HERE.md | 已登记默认资产，三方文本合并 |
| workspace/skills、已安装的宿主 Skill 副本 | 保留本地单独修改，合并非重叠修改；冲突停止 |
| workspace/templates、framework-policy.md、skills.lock.json | 更新空模板和框架政策，先检查并备份 |
| workspace/research、project-policy.md、state.json、数据、代码、证据与结果 | 当前 schema 1 资产升级不写入这些用户内容 |
| manuscript 全部内容 | 永不作为默认资产升级目标 |
| .rw/framework.json | 必须保留的旧版本文本和安装基线，不能当缓存随意删除 |

上游新增字段或空工作表不会自动重写你的已填表。需要新的研究字段时，由作者检查新版模板，再通过研究提案明确采用。

## 推荐操作：先检查，再执行

关闭正在写项目的 AI/编辑进程，在框架目录激活该框架的专用虚拟环境：

```bash
# 功能处于开发分支时使用这个 ref。
python scripts/update.py --project ../../my-paper --ref origin/feat/ai-research-workspace --check
python scripts/update.py --project ../../my-paper --ref origin/feat/ai-research-workspace --apply --actor "作者姓名"
```

代码合并且本地已正常切换到 main 后，使用 `--ref origin/main`。也可使用已获取的发布 tag 或具体 commit。脚本默认执行 `git fetch --no-tags origin`，不会获取所有新 tag；所选 ref 在检查开始时解析为固定 SHA，应用期间保持不变。

`--check` 更新远程跟踪引用，并把目标版本的资产当数据读取；不运行新版本代码、不安装包、不修改研究文件。输出当前/目标 SHA、仓库差异、项目资产差异、本地保留项和冲突。`--apply` 表示明确同意安装所选代码；必须在虚拟环境中执行。

另有 `sh scripts/update.sh ...` 和 PowerShell 的 `scripts/update.ps1 ...`。最通用的入口始终是 Python 脚本。

## 框架 checkout 有修改或分支分叉

脚本不会自动 stash、rebase、清理未跟踪文件、hard reset 或强推。先自行提交或备份改动；分支分叉后需要正常审查合并。

尤其注意：PR 若采用 squash merge，功能分支和 main 的提交历史可能不满足快进。先确认 checkout 干净，再正常切换分支：

```bash
git fetch origin
# 本地已有 main 时：
git switch main
git merge --ff-only origin/main
# 本地没有 main 时改用：git switch --track origin/main
```

之后进入框架目录，再检查/更新各个研究项目。不要用 `--ref origin/main` 强迫更新脚本解决分叉历史，也不要丢弃本地研究定制。

## 仅更新某个已有项目的默认资产

引擎已经安装或更新后，对每个项目分别执行：

```bash
rw --project ../../my-paper upgrade check
rw --project ../../my-paper upgrade apply --actor "作者姓名" --approve
```

离线或 ZIP 分发路线可指定已下载、已审查的框架包：

```bash
rw --project ../../my-paper upgrade check --source /path/to/new/ai-research-workspace
rw --project ../../my-paper upgrade apply --source /path/to/new/ai-research-workspace --actor "作者姓名" --approve
```

`--source` 是包含 pyproject.toml 与 research_workspace/ 的包目录，不是研究目录或 assets 目录。该子命令只升级项目资产；安装引擎代码需要另行完成。同版本重复执行没有新变化时不写入，不重写未变文件，也不复制大数据集。

## 三方合并与显式冲突处理

三方内容分别是：上次安装的默认版本、当前本地内容、新默认版本。只改本地时保留本地；只改上游时采用上游；双方在不重叠的位置修改时合并。重叠或边界相接等不确定情况保守地报告 conflict。

有冲突时，整个资产更新暂停，无冲突文件也不会先写入。先阅读差异，手工融合，或明确选择：

```bash
rw --project ../../my-paper upgrade check --keep-local workspace/skills/researcher/SKILL.md
rw --project ../../my-paper upgrade apply --keep-local workspace/skills/researcher/SKILL.md --actor "作者姓名" --approve
```

确实要采用上游时，把 `--keep-local` 改成 `--take-upstream`。参数可重复指定不同文件；同一文件不能同时使用两种选择。Git 更新脚本接受相同参数。不存在“强制覆盖整个论文”的开关。

日常学科/导师/写作偏好优先放在用户拥有的 project-policy.md 或项目 Skills。直接修改框架 checkout 的通用 Skill 属于源码开发，应提交到开发分支并通过 PR 维护。

## 备份、回滚和中断恢复

资产更新前会保存 `.rw/backups/UPDATE-....json`，包含受影响文件的 before/after、版本、时间和操作者。它是**增量默认资产备份**，不包含全部研究数据；仍需独立备份原始研究。

```bash
rw --project ../../my-paper upgrade history
rw --project ../../my-paper upgrade rollback UPDATE-实际备份ID
```

回滚先确认当前文件仍属于该次更新的 after 版本。更新后你又编辑了文件，回滚会拒绝覆盖；先保留新改动，再自行合并。不会撤销研究节点、最近稿件或数据变化。

更新/回滚中断会留下 `.rw/update-transaction.json`，其他写操作停止，先执行：

```bash
rw --project ../../my-paper upgrade recover
```

恢复只接受该操作的 before/after 文件版本。意外的新修改必须保留并人工处理。若进程被强杀留下 write.lock，先确认没有任何活跃写进程，再 `rw --project ../../my-paper recover --clear-lock`，随后运行资产 recover。普通研究事务中断则用 `rw recover`。不要随意删掉日志、状态或备份来绕过保护。

## 引擎安装失败或需要回退代码

Git、pip 和项目文件不构成跨系统原子事务。脚本会报告“代码安装失败，资产未更新”或“代码已更新，资产暂停”，不会把部分完成报告为成功。

更新前的源码保存在 `refs/rw-backups/<旧SHA前12位>`。成功更新的完整记录位于研究项目 `.rw/last-engine-update.json`。安装失败时先修复虚拟环境的构建工具/权限，再安装已审查版本。

需要回退引擎时，使用独立的旧版本工作树，避免破坏当前源码和未提交工作：

```bash
# 在父仓库根目录执行；ACTUAL_OLD_SHA 换成更新记录中的实际 commit。
git worktree add --detach ../rw-engine-rollback ACTUAL_OLD_SHA
python -m pip install --no-deps --no-build-isolation -e ../rw-engine-rollback/ai-research-workspace
```

然后视需要分别回滚项目默认资产。不要安装不支持当前研究 schema 的旧引擎。完成后重新执行 doctor、sync status、review。

## 多项目、版本与未来迁移

一个虚拟环境的引擎更新会影响使用该环境的所有项目，但脚本只更新指定项目的默认资产。其他项目分别执行 upgrade check/apply；需要冻结工具版本的论文使用独立虚拟环境。

当前状态 schema 为 1，支持同 schema 的资产升级。未知 schema 明确拒绝，不会猜测迁移或重置研究。未来发布破坏性数据格式变化前，维护者必须提供明确的迁移器、旧项目夹具、备份、验证、失败恢复与回滚测试。

初始化的 .gitignore 允许保留 `.rw/framework.json`，忽略其他运行时记录。跨机器复制项目要带上这份基线；丢失时从备份恢复，不能把当前定制冒充原默认版本。

每次维护版本应重新运行 `tests/test_upgrade.py` 和 `scripts/smoke_update_install.py`。测试通过只覆盖实际版本/场景，不能代替所有未来更新的回归验收。
