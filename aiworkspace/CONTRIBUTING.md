# 维护与贡献

本子项目独立于父仓库的 Vue 应用。默认仅修改 ai-research-workspace/ 与明确属于本项目的 CI 文件，不借机重写其他应用。

## 开发和验证

在 Python 3.11+ 的独立虚拟环境中安装：`python -m pip install -e .`。从默认分支创建功能分支，以一个明确研究场景为单位开发。

```bash
python -m unittest discover -s tests -v
python scripts/smoke_update_install.py
python scripts/check_docs.py
python -m compileall -q research_workspace scripts
rw doctor
rw demo ../../new-synthetic-demo
```

demo 目标须是新目录；它只能生成合成项目，不能替真实作者签字。升级集成测试只操作临时 Git 仓库与虚拟环境；需要开发环境已安装 setuptools。

PR 应说明：用户场景、输入/输出、修改的契约、隐私与执行影响、已测环境、未测能力、更新/回退方式。GitHub Checks 的实际结果才是托管验收依据；写了一份 workflow 文件不代表它已经运行通过。

## 修改位置

| 内容 | 位置 |
|---|---|
| 角色工作流 | research_workspace/assets/skills/NAME/SKILL.md |
| 上游来源与选择理由 | assets/skills.lock.json |
| 空模板与项目入口 | assets/templates、AGENTS.md、START_HERE.md |
| 可更新默认资产 | assets/release.json |
| 状态契约 | model.py、docs/SCHEMA.md |
| 提案/证据/影响 | workflow.py |
| 双向同步 | sync.py |
| 检索或模型适配 | adapters.py |
| 质量门 | review.py |
| 项目默认资产更新 | upgrade.py |
| Git/引擎更新 | scripts/update.py |

## 发布纪律

当前引擎/资产版本 0.1.0、研究 schema 1。发布时同步 pyproject.toml、research_workspace/__init__.py、assets/release.json、CHANGELOG；行为变化的 Skill 也更新 metadata version。

同 schema 的 Skill、空模板和框架政策可以三方更新。严禁把 state.json、workspace/research、data、methods、results、evidence、用户 policy 或 manuscript 加入默认资产覆盖范围。更新器的路径白名单是契约，不随意放宽。

未来改变 schema 前，必须先实现明确迁移、旧项目 fixture、备份、验证、失败恢复与回滚方案。未知 schema 当前应拒绝，不能用猜测或重置取代迁移。

每个新版本至少测试 N-1→N：未改默认、本地单改、双方不重叠修改、冲突、新增/删除资产、宿主 Skill 副本、更新/回滚中断、后续用户改动保护、幂等性，以及研究文件哈希不变。引擎 Git/pip 与项目资产提交不具有跨系统原子性，错误必须明确区分。

## Skill 与模型质量

新 Skill 必须有触发、输入、输出、停止条件和失败评测。不得把付费工具、自动联网或外部脚本执行偷偷加入默认流程。新 adapter 需要最小权限、响应边界、保密、格式/失败/重试策略测试。

evals/scenarios.json 是行为评测计划。实际运行时记录模型、宿主版本、日期、输入指纹、权限、重复次数、费用、输出和人工判断。没有执行的场景保持 not_run。软件测试不能替代科研质量、语言质量或专家审查。

## 协作与权利

真实论文使用独立私有仓库，原始数据另做备份。state.json 是单写者状态，不是实时协作数据库；Git 冲突需审查节点/提案含义，不能简单全选 ours/theirs。

代码和原创 Skills 为 MIT。用户上传的 Idea Evaluation 原文及紧密改编工作表保留原权利，不属于本项目擅自授予的 MIT 范围。二次公开分发模板前由维护者确认许可。不要提交未授权论文全文、参与者数据、密钥或第三方机密审稿内容。
