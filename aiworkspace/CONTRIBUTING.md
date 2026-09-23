# 迭代与贡献

所有框架代码/Skills/模板/文档保持在 aiworkspace/；根目录只保留公共更新入口和使用说明。请勿把个人论文、原始参与者数据、密钥或第三方受限全文提交进框架。

## 修改前确定层次

某篇论文的规则与研究放在该项目的 workspace/；通用 Skill 改 research_workspace/assets/skills；默认模板改 assets/templates；确定性引擎改对应 Python 模块。具体模块职责见 [架构](docs/ARCHITECTURE.md)。不要为修改个人写作偏好调整引擎数据 Schema。

在分支上开发，提交说明包含目的、影响、测试、兼容性与回滚方式。保持输入输出协议明确，错误时停止，旧用户内容完整可恢复。API/外部服务改变需核对官方文档并记录日期；固定第三方来源 commit 和许可，不自动执行外部 Skill 的安装命令。

## 本地验证

从仓库根目录、专用虚拟环境运行：

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-deps --no-build-isolation -e ./aiworkspace
python aiworkspace/scripts/run_tests.py
python aiworkspace/scripts/smoke_root_update.py
python aiworkspace/scripts/check_docs.py
rw demo ../new-demo-directory
```

单元测试离线，包含模拟网络响应；更新集成测试使用临时 Git 仓库和实际 editable 安装，复制当前环境已有的构建工具进入临时 venv。测试脚本只删除其自行创建的临时探针，不删除用户研究。

打包检查：`python -m pip wheel --no-deps --no-build-isolation ./aiworkspace -w ../workspace-wheels`，再在全新 venv、源码目录之外安装 wheel 并运行 doctor/demo。修改图表后必须打开实际输出检查。

## 必须覆盖的回归

证据/源文件/Claim 改动后旧核验失效；反证保留；未跑实验不能伪造成功；方法和输出哈希一致；双方稿件改动不会互相覆盖；过期提案拒绝；中断事务可恢复且不覆盖新编辑；重大问题/缺失人审阻断导出；demo 不得成为真实投稿。

更新相关修改还需：已填写工作表/稿件/数据/代码/用户规则哈希不变；本地 Skill 定制保留；冲突停写；新增/删除默认资产回滚；错误路径/符号链接拒绝；旧目录迁移；真实本地编辑保持可见；版本锁定；重复检查；未知 Schema 拒绝。

## 扩展与版本

新增 Skill 的注册与评估见 [Skills](docs/SKILLS.md) 和 [行为场景](evals/README.md)。文档契约检查不能替代真实模型评估。每个真实宿主试验记录 host/model/version/permission、任务、输入指纹、实际输出、观察者和失败，不从生成文本推断“已测试”。

发布时同步 pyproject.toml、__init__.py、assets/release.json 的框架版本；按实际需要更新 Skill metadata。Schema 只有结构契约变化才升级，先实现显式迁移与恢复测试。本版只支持 Schema 1。

Release PR 包含 changelog、迁移/兼容性、测试输出和已知边界。GitHub CI 未成功时不能声称绿色；区分本地验证、CI 结果和模型/科学评估。工作流失败应查看实际 job/annotations 后诊断，不推测原因。

## 模板许可

上传 PPT 的原文和紧密改编工作表保留原权利，见 [LICENSE](LICENSE)。无来源许可时不扩大再分发授权，不补入未提供的幻灯片内容，不捆绑原 PPT。
