"""Deterministic integrity checks plus explicit independent human review declarations."""
from __future__ import annotations
import json
import re
import shutil
from pathlib import Path
from .model import DOMAINS, WorkspaceError, digest, node_payload, now, pretty, require
from .store import Store, atomic_write, file_hash, project_lock, read_text, safe_path
from .sync import plan
from .workflow import evidence_problems, source_problems

PLACEHOLDER = re.compile(r'\b(?:TODO|TBD|PLACEHOLDER)\b|待填写|尚未填写', re.I)


def citation_ids(text: str) -> set[str]:
    return {key.rstrip('.:') for key in re.findall(r'(?<![\w@])@([A-Za-z0-9][A-Za-z0-9_.:-]*)', text)}


def review(store: Store) -> dict:
    issues = []
    def add(code: str, node: str, message: str, severity: str = 'major', domain: str = 'research_logic'):
        issues.append({'code': code, 'node': node, 'message': message, 'severity': severity, 'domain': domain})
    active = {k: n for k, n in store.state['nodes'].items() if n['status'] != 'retired'}
    text = read_text(safe_path(store.root, 'manuscript/main.md'))
    if PLACEHOLDER.search(text):
        add('MANUSCRIPT_PLACEHOLDER', 'MANUSCRIPT', 'Resolve placeholders; do not invent missing content.', domain='writing_language')
    for kind in ('question', 'hypothesis', 'argument', 'section', 'claim'):
        if not any(n['kind'] == kind for n in active.values()):
            add('MISSING_' + kind.upper(), 'PROJECT', 'Missing active ' + kind)
    for key in citation_ids(text):
        node = active.get(key)
        if not node or node['kind'] != 'source':
            add('CITATION_MISSING', key, 'Citation has no active source record.', 'critical', 'evidence_citations')
        else:
            try:
                problems = source_problems(store, node)
            except (WorkspaceError, OSError, ValueError) as exc:
                problems = [str(exc)]
            for problem in problems:
                add('CITATION_UNVERIFIED', key, problem, 'critical', 'evidence_citations')
    previous = '0' * 64
    for event in store.state['events']:
        payload = {k: v for k, v in event.items() if k != 'hash'}
        if event.get('previous') != previous or event.get('hash') != digest(payload):
            add('AUDIT_CHAIN', 'HISTORY', 'Audit chain was changed or corrupted; investigate with external version history.', 'critical')
            break
        previous = event['hash']
    for key, node in active.items():
        data, kind = node['data'], node['kind']
        for dep in node['depends_on']:
            if dep not in active:
                add('DEPENDENCY_MISSING', key, 'Dependency missing or retired: ' + dep, 'critical')
        if kind in ('question', 'hypothesis', 'argument', 'section', 'claim'):
            if node['status'] != 'confirmed':
                add('LOGIC_UNCONFIRMED', key, 'Confirm or revise this research/section node explicitly.')
            if PLACEHOLDER.search(str(data.get('text', ''))):
                add('LOGIC_PLACEHOLDER', key, 'Research logic still contains a placeholder.')
        if kind == 'claim':
            if not data.get('scope'):
                add('CLAIM_SCOPE', key, 'Declare the population/system, conditions and inference limits.')
            search = data.get('counterevidence_search', {})
            if not isinstance(search, dict) or not all(search.get(k) for k in ('query', 'date', 'result')):
                add('COUNTERSEARCH_MISSING', key, 'Record an actual counterevidence search, coverage and limitations.', domain='evidence_citations')
            evidence = [active[d] for d in node['depends_on'] if d in active and active[d]['kind'] == 'evidence']
            valid_support = False
            for item in evidence:
                try:
                    problems = evidence_problems(store, item)
                except (WorkspaceError, OSError, ValueError) as exc:
                    problems = [str(exc)]
                if item['data']['claim'] != key:
                    problems.append('Evidence points to a different Claim.')
                if not problems and item['data']['relation'] == 'supports':
                    valid_support = True
                if item['data']['relation'] in ('refutes', 'qualifies'):
                    responses = data.get('responses', {})
                    if not isinstance(responses, dict) or not responses.get(item['id']):
                        add('COUNTEREVIDENCE_RESPONSE', key, 'Address this counter/qualifying evidence explicitly: ' + item['id'], domain='evidence_citations')
            if not valid_support:
                add('CLAIM_UNSUPPORTED', key, 'No currently verified, correctly scoped supporting evidence.', 'critical', 'evidence_citations')
            if data['strength'] == 'causal':
                methods = [active[d] for d in node['depends_on'] if d in active and active[d]['kind'] == 'method']
                if not any(m['data'].get('causal_identification') for m in methods):
                    add('CAUSAL_IDENTIFICATION', key, 'Causal strength requires a defensible identification design and expert review.', 'critical', 'method_statistics')
        elif kind == 'evidence':
            try:
                problems = evidence_problems(store, node)
            except (WorkspaceError, OSError, ValueError) as exc:
                problems = [str(exc)]
            for problem in problems:
                add('EVIDENCE_INVALID', key, problem, 'critical', 'evidence_citations')
        elif kind == 'result':
            method = active.get(data.get('method'), {})
            if not method or method.get('kind') != 'method' or data.get('method_hash') != node_payload(method):
                add('RUN_METHOD_CHANGED', key, 'Method changed or is missing; regenerate a correctly versioned result.', 'critical', 'method_statistics')
            if data.get('exit_code') != 0 or not data.get('outputs'):
                add('RUN_FAILED', key, 'No successful executed output.', 'critical', 'method_statistics')
            if not any(e.get('action') == 'method.executed' and e.get('detail', {}).get('id') == key and e['detail'].get('result_hash') == node_payload(node) for e in store.state['events']):
                add('RUN_RECEIPT', key, 'Result lacks its matching execution event; proposed JSON is not an experiment.', 'critical', 'method_statistics')
            for group in ('inputs', 'code', 'outputs'):
                records = data.get(group, {})
                if not isinstance(records, dict) or not records:
                    add('RUN_MANIFEST_MISSING', key, 'Missing ' + group + ' manifest.', 'critical', 'method_statistics')
                    continue
                for path, sha in records.items():
                    try:
                        actual = file_hash(safe_path(store.root, path))
                    except (WorkspaceError, OSError):
                        actual = None
                    if not actual or actual != sha:
                        add('RUN_ARTIFACT_CHANGED', key, group + ' changed/missing: ' + path, 'critical', 'method_statistics')
        elif kind == 'figure':
            for field in ('path', 'sha256', 'claims', 'caption', 'purpose', 'alt_text'):
                if not data.get(field):
                    add('FIGURE_METADATA', key, 'Figure requires ' + field, domain='figures_tables')
            claims = data.get('claims', [])
            if not isinstance(claims, list) or not claims or any(c not in active or active[c]['kind'] != 'claim' or c not in node['depends_on'] for c in claims):
                add('FIGURE_CLAIM', key, 'Figure must explicitly depend on the Claims it expresses.', domain='figures_tables')
            if not any(d in active and active[d]['kind'] in ('result', 'evidence') for d in node['depends_on']):
                add('FIGURE_PROVENANCE', key, 'Link to the actual evidence/run behind this figure.', domain='figures_tables')
            try:
                sha = file_hash(safe_path(store.root, data.get('path', '')))
            except (WorkspaceError, OSError):
                sha = None
            if not sha or sha != data.get('sha256'):
                add('FIGURE_CHANGED', key, 'Figure file missing/changed. Recheck data, labeling and output.', 'critical', 'figures_tables')
        elif kind == 'rule':
            rule_type = data.get('type', 'human')
            if rule_type not in ('required_text', 'forbidden_text', 'human'):
                add('RULE_UNIMPLEMENTED', key, 'No checker for this rule type; cannot silently mark it passed.', domain='rules_compliance')
                continue
            if rule_type != 'human':
                value = data.get('value')
                if not isinstance(value, str) or not value:
                    add('RULE_INVALID', key, 'Literal rule needs nonempty value.', domain='rules_compliance')
                elif (rule_type == 'required_text' and value not in text) or (rule_type == 'forbidden_text' and value in text):
                    add('RULE_VIOLATION', key, 'Manuscript violates literal rule: ' + node['title'], domain='rules_compliance')
    try:
        syncing = plan(store)
        if syncing['changes'] or syncing['conflicts'] or syncing['outside_changed']:
            add('SYNC_STALE', 'MANUSCRIPT', 'Workspace and manuscript have unreviewed changes.', domain='sync_consistency')
    except (WorkspaceError, OSError, ValueError) as exc:
        add('SYNC_INVALID', 'MANUSCRIPT', str(exc), 'critical', 'sync_consistency')
    for item in store.state['issues'].values():
        if item['status'] == 'open':
            add('OPEN_ISSUE', item['node'], item['id'] + ': ' + item['message'], item['severity'])
    if any(p['status'] == 'pending' for p in store.state['proposals'].values()):
        add('PENDING_PROPOSAL', 'PROJECT', 'Resolve pending proposals before release.')
    blockers = sum(i['severity'] in ('critical', 'major') for i in issues)
    return {'generated_at': now(), 'fingerprint': store.fingerprint(), 'machine_status': 'blocked' if blockers else 'pass',
            'blocker_count': blockers, 'issues': issues, 'required_human_domains': list(DOMAINS),
            'boundary': 'Structural and integrity checks only. Scientific validity, statistical appropriateness, citation meaning and language require independent human review.'}


def save_report(store: Store) -> dict:
    report = review(store)
    atomic_write(safe_path(store.root, 'workspace/reports/final-review.json'), pretty(report))
    text = '# Final Review — ' + report['machine_status'].upper() + '\n\n' + report['boundary'] + '\n\n'
    text += '\n'.join('## ' + i['severity'].upper() + ' / ' + i['node'] + '\n' + i['message'] + '\n' for i in report['issues'])
    text += '\nFingerprint: `' + report['fingerprint'] + '`\n'
    atomic_write(safe_path(store.root, 'workspace/reports/final-review.md'), text)
    return report


def attest(store: Store, domain: str, actor: str, note: str, *, human: bool = False) -> dict:
    require(human and len(note.strip()) >= 20, 'Attestation requires --human and specific review notes (20+ characters).')
    require(domain in (*DOMAINS, 'author_release'), 'Unknown review domain.')
    require(domain == 'author_release' or actor not in store.state['writers'], 'A recorded writer cannot independently review their own work.')
    require(review(store)['machine_status'] == 'pass', 'Fix machine blockers before recording final domain approval.')
    receipt = {'domain': domain, 'actor': actor, 'note': note, 'at': now(), 'fingerprint': store.fingerprint(),
               'human_declared': True, 'demonstration_only': store.state['project']['mode'] == 'demo'}
    store.state['approvals'].append(receipt)
    store.event('review.attested', actor, {'domain': domain, 'fingerprint': receipt['fingerprint']})
    store.commit()
    return receipt


def gate(store: Store, *, demonstration: bool = False) -> dict:
    report = review(store)
    valid = [a for a in store.state['approvals'] if a.get('human_declared') and a.get('fingerprint') == report['fingerprint']]
    required = set(DOMAINS) | {'author_release'}
    completed = {a['domain'] for a in valid if a['domain'] == 'author_release' or a['actor'] not in store.state['writers']}
    demo = store.state['project']['mode'] == 'demo'
    if not demo:
        completed = {a['domain'] for a in valid if not a.get('demonstration_only') and (a['domain'] == 'author_release' or a['actor'] not in store.state['writers'])}
    ready = report['machine_status'] == 'pass' and not (required - completed) and (not demo or demonstration)
    return {'ready_for_packaging': ready, 'machine_status': report['machine_status'], 'blocker_count': report['blocker_count'],
            'missing_domains': sorted(required - completed), 'demonstration_only': demo, 'fingerprint': report['fingerprint'],
            'boundary': 'Local declarations do not authenticate identities or certify scientific merit.'}


def export_bundle(store: Store, destination: str | Path, *, demonstration: bool = False) -> dict:
    status = gate(store, demonstration=demonstration)
    require(status['ready_for_packaging'], 'Release gate blocked. Complete actual review or use explicit demonstration only for a demo project.')
    target = Path(destination).expanduser().resolve()
    require(not target.exists(), 'Export destination must be new.')
    require(not any(target.is_relative_to(store.root / folder) for folder in ('workspace', 'manuscript', '.rw')), 'Do not export into managed research folders.')
    with project_lock(store.root):
        require(Store(store.root).fingerprint() == status['fingerprint'], 'Research changed before export.')
        target.mkdir(parents=True)
        for path in (store.root / 'manuscript').rglob('*'):
            require(not path.is_symlink(), 'Symlink in manuscript.')
            if path.is_file():
                name = path.relative_to(store.root / 'manuscript')
                (target / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target / name)
        references = []
        for key in sorted(citation_ids(read_text(store.root / 'manuscript/main.md'))):
            node = store.node(key)
            item = {'id': key, 'type': node['data'].get('csl_type', 'article'), 'title': node['title']}
            for src, dst in (('doi', 'DOI'), ('url', 'URL'), ('csl_author', 'author'), ('issued', 'issued')):
                if node['data'].get(src):
                    item[dst] = node['data'][src]
            references.append(item)
        atomic_write(target / 'references.csl.json', pretty(references))
        atomic_write(target / 'review.json', pretty(review(store)))
        atomic_write(target / 'approvals.json', pretty([a for a in store.state['approvals'] if a['fingerprint'] == status['fingerprint']]))
        atomic_write(target / 'README.md', '# ' + ('DEMONSTRATION ONLY' if status['demonstration_only'] else 'Author-approved submission working package') + '\n\nMarkdown, original figures and supplements. Convert to the verified venue format separately. Human declarations are not scientific certification.\n')
        require(Store(store.root).fingerprint() == status['fingerprint'], 'Research changed during export; discard this incomplete package and rerun.')
        files = {p.relative_to(target).as_posix(): file_hash(p) for p in target.rglob('*') if p.is_file()}
        atomic_write(target / 'manifest.json', pretty({'files': files, 'gate': status, 'created_at': now()}))
    return {'exported': str(target), 'files': len(files), 'demonstration_only': status['demonstration_only']}
