# 已使用项目的增量更新

## 一、两个独立层次

**引擎更新**：Git fetch → 检查提交与代码差异 → fast-forward → 在专用 venv 重新安装。

**论文默认资产更新**：比较上次默认、本地实际文件、新默认 → 保留/合并/显式冲突选择 → 事务备份与写入。

根目录 `update_aiworkspace.py` 串联两个层次。`rw upgrade` 只处理第二层。后者不会回退 Python 引擎或修改研究成果。每次更新前停止活跃写入任务并备份真实研究数据。

## 二、常规更新（仓库根目录）

```bash
python update_aiworkspace.py --project ../my-paper --check
python update_aiworkspace.py --project ../my-paper --apply --actor "作者姓名"
```

建议把检查返回的完整 target_commit 加入应用命令：

```bash
python update_aiworkspace.py --project ../my-paper --apply --actor "作者姓名" --expected-commit 实际完整SHA
```

也可 `--ref 完整SHA` 锁定代码，或选明确的远程分支。默认 origin/main。已经获取了对象且无需联网时使用 `--offline`。

`--check` / `--dry-run` 不改论文文件或引擎工作区；允许 fetch 更新 Git 远程引用及临时解包。它只用当前可信引擎读取目标资产，不执行新提交中的 Python。应用操作表示你已审查并信任该版本代码；Git SHA 是版本定位，不能证明代码安全。

检查返回 current_commit、target_commit、repository_diff、project_asset_changes、preserved_local_customizations、conflicts 和 blocked。确认代码及资产差异后再应用。根脚本 stdout 是一个 JSON 对象；错误在 stderr。退出码 0 成功，1 检查被阻塞，2 执行/输入错误。

## 三、具体哪些东西保留

不作为更新目标：state.json、manuscript/、workspace/research/ 的填写内容、sources/evidence/data/methods/results、project-policy.md、memory/history，以及自定义新增研究文件。

可更新：AGENTS.md、CLAUDE.md、START_HERE.md、framework-policy.md、空模板、9 个内置 Skills、skills.lock.json、已注册的 .agents/skills 或 .claude/skills 副本。

| 旧默认、本地、新默认关系 | 行为 |
|---|---|
| 仅上游改变 | 更新默认 |
| 仅本地改变 | 保留本地 |
| 两边相同修改 | 保留并推进基线 |
| 不重叠的文本修改 | 三方合并 |
| 同一区域/删除/新增冲突 | 停止，不自动选边 |
| 上游试图覆盖研究路径或未知 schema | 拒绝 |

保留 `.rw/framework.json`，其中存储上次默认的完整内容。你的论文私有仓库应纳入该基线；`.rw` 其他运行时文件默认忽略。缺失基线时从可信备份恢复，不能以当前新模板伪造旧基线。

## 四、解决 Skill / 模板冲突

例如本地和上游都改了写作 Skill。先检查三份内容；保留本地时对检查和应用都使用相同参数：

```bash
python update_aiworkspace.py --project ../my-paper --check --keep-local workspace/skills/writing-language/SKILL.md
python update_aiworkspace.py --project ../my-paper --apply --actor "作者姓名" --keep-local workspace/skills/writing-language/SKILL.md
```

明确采用上游时使用 `--take-upstream 相同路径`，会保存被覆盖的旧内容到资产备份。同一文件不能同时 keep/take。可重复参数指定多个文件。宿主副本有自己的路径和本地修改，必要时逐个解决，不能只改 canonical Skill 后假定所有副本一致。

手工合并也可以：先保存原本地副本，审查合并后内容，再用 check/keep-local 接受结果；基线推进到新默认，后续更新仍能识别你的定制。

框架代码本身存在未提交/未跟踪编辑时，更新器停止。由你保存到分支/提交或移出 checkout；程序不自动 stash、reset、clean 或覆盖。分支分叉需在 Git 中审查合并，程序只接受 fast-forward。

## 五、回滚与中断恢复

```bash
rw --project ../my-paper upgrade history
rw --project ../my-paper upgrade rollback UPDATE-ID
```

UPDATE-ID 来自真实更新返回值或 history。`.rw/backups/` 保存变更前后受管资产；回滚恢复资产及旧基线。更新后又编辑过这些文件时回滚会停止，避免丢掉新工作。先另存并审查新修改，不强制覆盖。

中断默认资产更新/回滚后：

```bash
rw --project ../my-paper upgrade recover
```

中断研究状态事务后：

```bash
rw --project ../my-paper recover
```

存在残留写锁时，先确认原进程已经停止，才使用 `rw --project ../my-paper recover --clear-lock` 清理锁；若它提示先恢复资产，随后运行 upgrade recover。不能清理活跃进程的锁。恢复也会检查中断后是否新增本地编辑。

引擎与资产不能假装是一个完全原子事务：安装失败时引擎 Git 可能已经前进，但论文默认资产仍旧；资产应用失败时新引擎可能已安装。错误消息会明确状态。检查 `.rw/last-engine-update.json`（成功后生成）和 Git `refs/rw-backups/`；旧代码备份引用格式为 `refs/rw-backups/旧提交前12位`。

需要旧引擎时，安全做法是在新的 worktree/clone 中检出实际旧 SHA，再用新的专用 venv 安装旧包；不要对有编辑的当前仓库执行破坏性重置。资产回滚与引擎恢复分别审查。任何未知数据 schema 都需要显式迁移，本版不会猜测转换。

## 六、多篇论文、旧目录及 ZIP 用户

第一篇论文可用根脚本更新引擎及资产；后续论文在同一已更新引擎下逐个运行：

```bash
rw --project ../paper-b upgrade check
rw --project ../paper-b upgrade apply --actor "作者姓名" --approve
```

每篇论文都有独立基线/冲突/备份。不要把 A 的 `.rw/framework.json` 复制给 B。

根脚本支持旧 `ai-research-workspace/` 到新 `aiworkspace/` 的路径迁移。旧 checkout 尚无根脚本时，先审查并获取目标版本的根脚本；不要用旧目录脚本跨重命名盲目更新。较稳妥的迁移是把新版 clone 到新的框架目录、安装新引擎，再对原论文运行 upgrade check/apply。**论文目录和基线保持原样**。旧框架残留的缓存被根 .gitignore 忽略，真实旧目录笔记依然会阻断更新。

下载 ZIP 的框架没有 Git 历史，根脚本会拒绝。可先保留整个论文并另行 clone 框架，安装后运行资产更新。已有只装 wheel 的用户先自行升级到审查过的 wheel，再用 rw upgrade；无需重建论文。

框架 Schema 1 的资产更新已经测试；不同/未来 Schema 没有迁移实现时会明确阻断。

## 七、更新后的验收

```bash
rw doctor
rw --project ../my-paper sync status
rw --project ../my-paper review
```

新的引擎或受管资产可能改变指纹，旧审核声明需要重评。更新脚本的备份仅覆盖框架资产，务必另做原文、数据、代码与稿件的可靠备份。
