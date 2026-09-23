# 状态契约：schema_version = 1

权威状态位于 `workspace/state.json`，外部原文、数据、代码、图表和稿件保存在独立文件中。普通使用者通过 CLI 提案操作，不直接改整个 state.json。

## 节点公共结构

```json
{
  "id": "CLM-001",
  "kind": "claim",
  "title": "有范围限制的论点",
  "status": "draft",
  "depends_on": ["EVD-001", "MTH-001"],
  "data": {
    "text": "具体断言，不填入尚未发生的实验结果。",
    "strength": "descriptive",
    "scope": "明确研究对象、条件和推断范围",
    "counterevidence_search": {
      "query": "实际执行的反证检索式",
      "date": "实际检索日期",
      "result": "真实检索结果与覆盖局限"
    },
    "responses": {}
  }
}
```

以上是字段说明模板，不能原样当成实际证据。ID 使用大写前缀和连字符，例如 RQ-001、HYP-001、ARG-001、CLM-001、SRC-001、EVD-001、MTH-001、RUN-...、FIG-001、SEC-ABSTRACT、RULE-001、DEC-001。改题目不应改稳定 ID。

kind 有 12 类：question、hypothesis、argument、section、claim、source、evidence、method、result、figure、rule、decision。status 为 draft/confirmed/retired。扩展字段放在 data，不能任意增加顶层属性。depends_on 指向上游依赖；不得重复或自依赖。循环依赖遍历会终止，但科学论证仍需独立检查。

## 各类数据

| kind | 主要 data 字段 | 约束 |
|---|---|---|
| question / hypothesis / argument | text、范围、前提、贡献等 | 核心逻辑需确认，不能留占位文字 |
| section | text：完整 Markdown 章节 | 与 manuscript 同 ID 标记对应 |
| claim | text、strength、scope、counterevidence_search、responses | strength 为 descriptive/association/causal/hypothesis；因果断言需明确辨识设计 |
| source | category、url、snapshot；可带 doi、retracted 等 | snapshot 为有权限保存的 UTF-8 原始摘录/结果；元数据不等于核验 |
| evidence | source、claim、quote、locator、scope、relation | relation 为 supports/refutes/qualifies；必须依赖其 source |
| method | script、inputs、outputs、args、seed、design | 已确认方法，审阅过的本地 Python；新输出路径 |
| result | method、method_hash、code/inputs/outputs 哈希、执行信息 | 来自真实 runner，需匹配执行事件 |
| figure | path、sha256、claims、caption、purpose、alt_text | 依赖 Claim 与 result/evidence；表格也可作为受追踪资产 |
| rule | type、value、来源、版本、适用性 | required_text/forbidden_text/human；未知检查器阻塞 |
| decision | options、rationale、participants、revisit_conditions 等 | 保存选择依据，不当作事实来源 |

来源 category：peer_reviewed、official_data、standard、primary、preprint、institutional、news、blog、unclassified。默认可准入的类别仍须实际核验。以某段新闻为研究原始语料时，实际核验者可提供 primary_for 例外理由；不能用统一来源等级替代研究适用性判断。

Claim 的 depends_on 应包含所有相关支持、反驳和限定证据。Evidence 的 data.claim 指向具体断言；核验绑定该断言的 text/strength/scope。反证的处理记录在 claim.data.responses，以证据 ID 为键，值为实际回应，不应删掉不利结果。

## 方法示例

```json
{
  "id": "MTH-001",
  "kind": "method",
  "title": "经过审阅的描述性分析",
  "status": "confirmed",
  "depends_on": ["RQ-001"],
  "data": {
    "script": "workspace/methods/descriptives.py",
    "inputs": ["workspace/data/input.csv"],
    "outputs": ["workspace/results/run-001/summary.json"],
    "args": [],
    "seed": 0,
    "design": "填写实际设计和可支持的推断范围"
  }
}
```

先真实创建并检查输入和代码，再运行。runner 不会替你生成它们。已有输出会被拒绝，以免旧文件冒充本轮结果；下一轮用新目录。输出只允许 results、manuscript/figures 或 supplementary。代码执行不是沙箱。

## 提案结构

```json
{
  "summary": "目的与依据",
  "base_fingerprint": "任务包中的真实指纹，可选但推荐保留",
  "operations": [
    {"op": "upsert", "node": {"此处": "完整合法节点"}},
    {
      "op": "write",
      "path": "manuscript/main.md",
      "text": "完整新 Markdown，保留章节标记",
      "expected_sha256": "原文件真实 SHA-256；新文件为 null"
    }
  ]
}
```

此处是结构说明，不是可直接运行的合法研究提案。[上手文档](GETTING_STARTED.md) 有完整可用示例。一次最多 100 个操作。upsert 是全节点替换，必须主动保留仍然有效的数据。write 仅限受管辖 Markdown，不可写 state.json、脚本、raw data 或伪造报告。

提案状态 pending → applied/rejected，保存创建者、时间、基准指纹、操作与影响范围。应用须明确批准并提供解释；过期时重新生成。

## 核验、问题、审查与同步

verification 不由普通提案创建。实际核验操作记录责任人、时间、说明、源快照/节点/Claim 哈希。它验证本地完整性与声明，不自动证明语义、身份、科学真伪或伦理许可。

issues 记录 severity、node、message、source、status 及实际修复依据。approvals 记录领域、责任人、说明、指纹、human_declared 与 demonstration_only。领域审核不能由已记录写作者自审；全部声明都需对应当前指纹。

events 是带前序哈希的本地事件链；tasks 是按当前问题路由的 Skill 待办，旧指纹任务会 supersede；sync 保存上次一致章节及标记外文本哈希。

这些本地记录不具备真正身份认证或不可抵赖性。团队需要更强权限、签名与审计时，应开发单独服务端层。未来 schema 变化必须有明确迁移实现；当前遇到未知 schema 会停止。
