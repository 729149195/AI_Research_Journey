"""Escaped read-only HTML snapshot. No server, third-party scripts or network calls."""
from __future__ import annotations
from html import escape
from .model import pretty
from .review import review
from .store import Store, atomic_write, safe_path


def dashboard(store: Store) -> dict:
    report = review(store)
    def e(value): return escape(str(value), quote=True)
    groups = [('question', 'Research question'), ('hypothesis', 'Hypothesis'), ('argument', 'Overall argument'),
              ('claim', 'Claims'), ('evidence', 'Evidence'), ('source', 'Sources'), ('method', 'Methods'),
              ('result', 'Results'), ('figure', 'Figures & tables'), ('section', 'Manuscript'), ('rule', 'Rules'), ('decision', 'Decisions')]
    sections = []
    for kind, title in groups:
        cards = ''.join('<article><small>' + e(n['id']) + ' · ' + e(n['status']) + '</small><h3>' + e(n['title']) + '</h3><pre>' + e(pretty(n['data'])) + '</pre><p>Depends on: ' + e(', '.join(n['depends_on'])) + '</p></article>' for n in store.state['nodes'].values() if n['kind'] == kind)
        sections.append('<section id="' + kind + '"><h2>' + title + '</h2><div class="grid">' + (cards or '<p>No records yet.</p>') + '</div></section>')
    issues = ''.join('<tr><td>' + e(i['severity']) + '</td><td>' + e(i['node']) + '</td><td>' + e(i['message']) + '</td></tr>' for i in report['issues'])
    nav = ''.join('<a href="#' + kind + '">' + title + '</a>' for kind, title in groups)
    html = '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'">
<title>Research Workspace</title><style>
:root{font:16px/1.6 system-ui,sans-serif;color:#17273c;background:#f2f5f9}*{box-sizing:border-box}body{margin:0}header{background:#17273c;color:white;padding:38px 5vw}h1{font-size:2.2rem;margin:0}nav{padding:16px 5vw;display:flex;flex-wrap:wrap;gap:14px;background:white;border-bottom:1px solid #cdd9e5}a{color:#17697d}main{max-width:1250px;margin:auto;padding:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}article,.status{padding:22px;border-radius:12px;border:1px solid #cdd9e5;background:white;min-width:0}small{color:#586b7c}pre{white-space:pre-wrap;word-break:break-word;font:13px/1.55 ui-monospace,monospace;max-height:320px;overflow:auto}h2{margin-top:36px}.badge{font-size:1.6rem;font-weight:700}table{width:100%;border-collapse:collapse;background:white}td,th{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid #cdd9e5}footer{padding:30px 0;color:#586b7c}@media(max-width:600px){main{padding:12px}h1{font-size:1.7rem}}
</style><header><p>AI RESEARCH WORKSPACE / LOCAL SNAPSHOT</p><h1>''' + e(store.state['project']['name']) + '''</h1><p>Workspace 管研究状态与整体逻辑 · Manuscript 管正式表达 · 本页面只读且不联网。</p></header><nav><a href="#review">Quality gate</a>''' + nav + '</nav><main><div class="status"><div class="badge">' + e(report['machine_status'].upper()) + ' · ' + str(report['blocker_count']) + ' blockers</div><p>Mode: ' + e(store.state['project']['mode']) + ' · Revision: ' + str(store.state['revision']) + ' · ' + e(report['generated_at']) + '</p><small>机器完整性检查不等于科学有效性，仍须独立领域审查。页面生成后的变化不会自动刷新。</small></div><section id="review"><h2>Critical issues & required fixes</h2><table><thead><tr><th>Severity</th><th>Node</th><th>Required action</th></tr></thead><tbody>' + (issues or '<tr><td colspan="3">No structural blockers. Independent human review is still required.</td></tr>') + '</tbody></table></section>' + ''.join(sections) + '<footer>重新生成：<code>rw dashboard</code><br>Fingerprint: ' + e(report['fingerprint']) + '<br>请勿把含有未发表研究的页面上传公共网站。</footer></main></html>'
    path = safe_path(store.root, 'workspace/reports/dashboard.html')
    atomic_write(path, html)
    return {'dashboard': str(path), 'mode': 'offline-read-only', 'machine_status': report['machine_status']}
