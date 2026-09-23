"""Proposal approval, evidence integrity and accountable reviewable changes."""
from __future__ import annotations
import copy
from .model import assertion_hash, digest, identifier, impact, node_payload, now, require, validate_node
from .store import Store, file_hash, read_text, safe_path


def propose(store: Store, operations: list[dict], actor: str, summary: str) -> dict:
    require(isinstance(operations, list) and 0 < len(operations) <= 100, 'Provide 1–100 operations.')
    require(isinstance(summary, str) and bool(summary.strip()), 'Proposal summary required.')
    normalized, touched, paths = [], set(), set()
    graph = copy.deepcopy(store.state['nodes'])
    for op in operations:
        require(isinstance(op, dict), 'Operation must be an object.')
        if op.get('op') == 'upsert':
            require(set(op) == {'op', 'node'}, 'Unexpected upsert fields.')
            node = copy.deepcopy(op['node'])
            validate_node(node)
            old = store.state['nodes'].get(node['id'])
            require(node['id'] not in touched, 'Duplicate node operation.')
            require(old is None or old['kind'] == node['kind'], 'Node kind cannot change; use a new ID.')
            if 'verification' in node:
                require(old is not None and node['verification'] == old.get('verification'), 'Agents cannot create verification receipts.')
            node.pop('verification', None)
            if old and node_payload(old) == node_payload(node) and 'verification' in old:
                node['verification'] = copy.deepcopy(old['verification'])
            touched.add(node['id'])
            normalized.append({'op': 'upsert', 'node': node})
            combined = copy.deepcopy(node)
            combined['depends_on'] = sorted(set(node['depends_on']) | set((old or {}).get('depends_on', [])))
            graph[node['id']] = combined
        elif op.get('op') == 'write':
            require(set(op) == {'op', 'path', 'text', 'expected_sha256'}, 'write needs path, text and expected_sha256.')
            path = op['path']
            target = safe_path(store.root, path)
            require(path.endswith('.md') and not path.startswith('workspace/reports/'), 'Proposal file writes are Markdown only; reports and executable code cannot be written here.')
            require(path not in paths and isinstance(op['text'], str), 'Duplicate path or invalid text.')
            require(file_hash(target) == op['expected_sha256'], 'File changed before proposal: ' + path)
            paths.add(path)
            normalized.append(copy.deepcopy(op))
        else:
            require(False, 'Only upsert and Markdown write operations are supported.')
    roots = set(touched)
    if any(graph[i]['kind'] == 'rule' for i in touched) or any(p.startswith('workspace/rules/') for p in paths):
        roots.update(graph)
    for path in paths:
        for key, node in graph.items():
            if path in str(node['data']) or (path == 'manuscript/main.md' and node['kind'] == 'section'):
                roots.add(key)
    result = {'id': identifier('PROP'), 'status': 'pending', 'created_at': now(), 'actor': actor, 'summary': summary,
              'base_fingerprint': store.fingerprint(), 'operations': normalized, 'impact': impact(graph, sorted(roots))}
    store.state['proposals'][result['id']] = result
    store.event('proposal.created', actor, {'id': result['id'], 'summary': summary})
    store.commit()
    return result


def add_issue(store: Store, node: str, message: str, actor: str, severity: str = 'major', *, commit: bool = True) -> dict:
    require(severity in ('critical', 'major', 'minor') and isinstance(message, str) and bool(message.strip()), 'Invalid issue.')
    issue = {'id': identifier('ISS'), 'node': node, 'message': message, 'severity': severity, 'status': 'open', 'created_at': now(), 'source': actor}
    store.state['issues'][issue['id']] = issue
    if commit:
        store.event('issue.created', actor, {'id': issue['id']})
        store.commit()
    return issue


def apply(store: Store, proposal_id: str, actor: str, note: str, *, approve: bool = False) -> dict:
    require(approve and len(note.strip()) >= 12, 'Approval needs --approve and an explanatory note (12+ characters).')
    proposal = store.state['proposals'].get(proposal_id)
    require(proposal is not None and proposal['status'] == 'pending', 'Proposal missing or no longer pending.')
    require(store.fingerprint() == proposal['base_fingerprint'], 'Stale proposal; regenerate against current research.')
    changes, expected = {}, {}
    wrote = False
    for op in proposal['operations']:
        if op['op'] == 'upsert':
            node = copy.deepcopy(op['node'])
            store.state['nodes'][node['id']] = node
            wrote = wrote or node['kind'] == 'section'
        else:
            changes[op['path']], expected[op['path']] = op['text'], op['expected_sha256']
            wrote = wrote or op['path'].startswith('manuscript/')
    if wrote:
        store.state['writers'] = sorted(set(store.state['writers']) | {actor, proposal['actor']})
    sync_data = proposal.get('sync_commit')
    if sync_data:
        store.state['sync'] = sync_data['baseline']
        for key in sync_data['semantic_review']:
            add_issue(store, key, 'Manuscript meaning may have changed. Review Claim strength, evidence, abstract, discussion, conclusion and figures before closing this issue.', proposal_id, commit=False)
    else:
        for key in sorted(set(proposal['impact']['sections'] + proposal['impact']['figures'])):
            add_issue(store, key, 'Research changed upstream. Inspect this dependent section/figure and all scientific implications; document the actual global update.', proposal_id, commit=False)
    proposal.update(status='applied', applied_at=now(), approved_by=actor, approval_note=note)
    store.event('proposal.applied', actor, {'id': proposal_id, 'impact': proposal['impact']})
    store.commit(changes, expected)
    return proposal


def reject(store: Store, proposal_id: str, actor: str, note: str) -> dict:
    proposal = store.state['proposals'].get(proposal_id)
    require(proposal is not None and proposal['status'] == 'pending', 'Pending proposal not found.')
    require(bool(note.strip()), 'Rejection reason required.')
    proposal.update(status='rejected', rejected_by=actor, rejection_note=note)
    store.event('proposal.rejected', actor, {'id': proposal_id})
    store.commit()
    return proposal


def source_problems(store: Store, source: dict) -> list[str]:
    problems = []
    if source.get('kind') != 'source' or source.get('status') == 'retired':
        return ['Source is absent, retired or of the wrong kind.']
    data, receipt = source['data'], source.get('verification', {})
    if not receipt or receipt.get('node_hash') != node_payload(source):
        problems.append('Source has no current human verification receipt.')
    if data.get('retracted') is True:
        problems.append('Source is retracted; do not use it as established supporting evidence.')
    if data.get('category') not in ('peer_reviewed', 'official_data', 'standard', 'primary', 'preprint') and not receipt.get('primary_for'):
        problems.append('Discovery-only source; trace the original or justify this document as the primary object of study.')
    path = data.get('snapshot')
    if not path:
        problems.append('Original-source UTF-8 snapshot/extract is missing.')
    else:
        try:
            sha = file_hash(safe_path(store.root, path))
            if not sha or sha != receipt.get('snapshot_hash'):
                problems.append('Original source snapshot changed or is unavailable.')
        except (ValueError, OSError) as exc:
            problems.append(str(exc))
    return problems


def evidence_problems(store: Store, evidence: dict) -> list[str]:
    d, receipt = evidence['data'], evidence.get('verification', {})
    source = store.state['nodes'].get(d['source'])
    claim = store.state['nodes'].get(d['claim'])
    if not source or source['kind'] != 'source':
        return ['Evidence source is missing or not a source node.']
    problems = source_problems(store, source)
    if not receipt or receipt.get('node_hash') != node_payload(evidence):
        problems.append('Evidence has no current verification receipt.')
    if receipt.get('source_receipt_hash') != digest(source.get('verification', {})):
        problems.append('Source verification changed; reassess evidence.')
    if not claim or claim['kind'] != 'claim' or receipt.get('claim_assertion_hash') != assertion_hash(claim):
        problems.append('Claim meaning or strength changed; reassess applicability.')
    try:
        snapshot = read_text(safe_path(store.root, source['data'].get('snapshot', '')))
        if d['quote'] not in snapshot:
            problems.append('Exact quotation is not present in the source snapshot.')
    except (ValueError, OSError) as exc:
        problems.append(str(exc))
    return problems


def verify(store: Store, node_id: str, actor: str, note: str, *, human: bool = False, primary_for: str = '') -> dict:
    require(human and len(note.strip()) >= 12, 'Verification requires --human and substantive note; metadata lookup is not content verification.')
    node = store.node(node_id)
    require(node['kind'] in ('source', 'evidence'), 'Only sources and evidence receive verification receipts.')
    require(node['status'] != 'retired', 'Retired material cannot be verified as current.')
    data = node['data']
    if node['kind'] == 'source':
        require(data.get('retracted') is not True, 'Retracted source cannot be verified for established support.')
        require(data['category'] in ('peer_reviewed', 'official_data', 'standard', 'primary', 'preprint') or len(primary_for.strip()) >= 20, 'Source policy requires original material; primary-object exception needs explicit justification.')
        snapshot = safe_path(store.root, data.get('snapshot', ''))
        require(bool(read_text(snapshot).strip()), 'Source snapshot is empty.')
        receipt = {'snapshot_hash': file_hash(snapshot), 'primary_for': primary_for}
    else:
        source, claim = store.node(data['source']), store.node(data['claim'])
        require(source['kind'] == 'source' and claim['kind'] == 'claim', 'Evidence links have the wrong kinds.')
        require(not source_problems(store, source), 'Verify the original source first and fix its problems.')
        require(data['quote'] in read_text(safe_path(store.root, source['data']['snapshot'])), 'Quotation is absent from source.')
        receipt = {'source_receipt_hash': digest(source['verification']), 'claim_assertion_hash': assertion_hash(claim)}
    node['status'] = 'confirmed'
    receipt.update(actor=actor, at=now(), note=note, node_hash=node_payload(node), human_declared=True,
                   demonstration_only=store.state['project']['mode'] == 'demo')
    node['verification'] = receipt
    store.event('verification.recorded', actor, {'id': node_id, 'receipt': digest(receipt)})
    store.commit()
    return {'id': node_id, 'verification': receipt, 'boundary': 'Human declaration plus file/quote integrity; no identity authentication or scientific certification.'}


def resolve_issue(store: Store, issue_id: str, actor: str, note: str) -> dict:
    issue = store.state['issues'].get(issue_id)
    require(issue is not None and issue['status'] == 'open', 'Open issue not found.')
    require(len(note.strip()) >= 20, 'Explain actual fixes and rechecks (20+ characters).')
    issue.update(status='resolved', resolved_at=now(), resolved_by=actor, resolution=note)
    store.event('issue.resolved', actor, {'id': issue_id, 'note': note})
    store.commit()
    return issue
