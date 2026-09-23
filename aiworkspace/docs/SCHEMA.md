# 数据契约（Schema 1）

完整可运行参考是 `rw demo NEW_PATH` 生成的 `workspace/state.json`。请通过提案/CLI 修改研究；不要手工覆盖整个状态文件。

## Node

每个节点必需 `id`、`kind`、`title`、`status`、`depends_on`、`data`。ID 如 RQ-001、CLM-001，使用大写前缀、连字符与字母数字；具体约束以 `model.py` 为准。status 是 draft / confirmed / retired。扩展字段置于 data；验证收据由 verify 生成，普通 AI 提案不能生成。

| kind | data 中关键内容 |
|---|---|
| question / hypothesis / argument | text、范围、假设、贡献与推断角色 |
| section | text：完整 Markdown 章节；depends_on 连接总体论证及 Claims |
| claim | text、strength（descriptive/association/causal/hypothesis）、scope、counterevidence_search（query/date/result）、responses（反证ID→回应） |
| source | category、url、snapshot（UTF-8 原文摘录路径）；doi、版本/出版状态、更正撤稿检查；retracted 为 true 会阻断确证支持 |
| evidence | source、claim、quote、locator、scope、relation（supports/refutes/qualifies）；depends_on 包含 source |
| method | script、inputs、outputs、args、seed、design；因果论点需 causal_identification 并接受专家核查 |
| result | 实际执行器生成 method/method_hash、code/inputs/outputs 哈希、args、seed、环境、退出码与时间 |
| figure | path、sha256、claims、purpose、caption、alt_text；依赖关联 Claim 与实际 result/evidence |
| rule | type（required_text/forbidden_text/human）、value、原始出处、适用范围/日期；未实现自动类型不会静默通过 |
| decision | 实际备选项、选择、理由、参与者、重评条件；仅供上下文参考 |

source.category 可为 peer_reviewed、official_data、standard、primary、preprint、institutional、news、blog、unclassified。分类本身不证明内容可靠或适用。新闻等作为原始研究对象时需明确原始材料角色。

## 可导入提案

```json
{
  "summary": "具体说明为什么修改",
  "base_fingerprint": "来自当前任务包的实际值",
  "operations": [
    {
      "op": "upsert",
      "node": {
        "id": "CLM-001",
        "kind": "claim",
        "title": "有范围限制的论点",
        "status": "draft",
        "depends_on": [],
        "data": {
          "text": "待验证的具体论点。",
          "strength": "hypothesis",
          "scope": "明确对象和条件，当前证据尚缺。"
        }
      }
    }
  ]
}
```

上面 fingerprint 是示意，必须替换为实际值。手工创建新提案可省略该字段，由 propose 以当前指纹建基线；模型任务包回传应保留它。每份提案包含 1–100 个 operation，不允许同一节点/路径重复修改。

`upsert` 完整替换，先读取旧节点并保留有效信息。`write` 需要完整新文本和旧文件哈希：

```json
{
  "op": "write",
  "path": "workspace/research/notes.md",
  "text": "# Research notes\n\n明确标记为待验证的想法。\n",
  "expected_sha256": null
}
```

null 仅用于尚不存在的新文件；已有文件使用实际 SHA-256。可提案写入范围是 workspace/、manuscript/ 下的 Markdown，排除报告目录；不能通过提案执行代码、直接写 state.json 或生成实验收据。研究代码在人工审查流程中单独管理。

## 引用、同步和审核

引用键使用 `[@SRC-001]` 或 `[@SRC-001; @SRC-002]`，应对应有效 source。证据用必要逐字原文、locator 和适用范围支撑精确 Claim。source.snapshot 的哈希、引用原文、Claim text/strength/scope 及核验记录均参与有效性判断。

章节使用 `<!-- rw:section SEC-ID -->` 与 `<!-- /rw:section SEC-ID -->` 成对标记。同步基线记录上一轮每节文字；请勿丢弃这些标记或用相同 ID 表示不同章节。

审核与导出使用整个当前项目指纹。审核者姓名及 `--human` 是本地声明，程序不认证身份；同一已登记写作者不能作为独立审核者。demo 模式的声明不能用于真实研究放行。

## 文件所有权

可更新目标由 `upgrade.owned()` 白名单控制：入口文档、框架政策、空模板、Skills、Skills 锁文件，以及已注册宿主副本。实际论文、已填写工作表、研究数据/代码/结果、用户规则、state.json 均不在该白名单。

`.rw/framework.json` 保存旧默认内容及宿主列表，不能随意删除或凭猜测重建。`schema_version` 未被引擎支持时拒绝更新；升级必须有显式迁移实现和测试。
