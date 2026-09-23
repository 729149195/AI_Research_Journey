"""Versioned domain contracts. Structural validity does not establish scientific truth."""
from __future__ import annotations
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

SCHEMA_VERSION = 1
KINDS = {'question', 'hypothesis', 'argument', 'section', 'claim', 'source', 'evidence', 'method', 'result', 'figure', 'rule', 'decision'}
STATUSES = {'draft', 'confirmed', 'retired'}
CATEGORIES = {'peer_reviewed', 'official_data', 'standard', 'primary', 'preprint', 'institutional', 'news', 'blog', 'unclassified'}
STRENGTHS = {'descriptive', 'association', 'causal', 'hypothesis'}
DOMAINS = ('research_logic', 'evidence_citations', 'method_statistics', 'figures_tables', 'writing_language', 'rules_compliance', 'ethics_ai', 'sync_consistency')
ID_RE = re.compile(r'^[A-Z][A-Z0-9]*-[A-Z0-9][A-Z0-9_-]{0,63}$')

class WorkspaceError(Exception):
    """Recoverable user-facing error, CLI status 2."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WorkspaceError(message)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def identifier(prefix: str) -> str:
    return prefix + '-' + uuid.uuid4().hex[:12].upper()


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n'


def digest(value: Any) -> str:
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value).encode('utf-8')).hexdigest()


def node_payload(node: dict) -> str:
    return digest({k: v for k, v in node.items() if k != 'verification'})


def assertion_hash(claim: dict) -> str:
    return digest({k: claim['data'].get(k) for k in ('text', 'strength', 'scope')})


def validate_node(node: Any) -> None:
    require(isinstance(node, dict), 'Node must be an object.')
    require(set(node) <= {'id', 'kind', 'title', 'status', 'depends_on', 'data', 'verification'}, 'Put extension fields inside data.')
    for field in ('id', 'kind', 'title', 'status', 'depends_on', 'data'):
        require(field in node, 'Missing node field: ' + field)
    require(isinstance(node['id'], str) and bool(ID_RE.fullmatch(node['id'])), 'Invalid ID; use CLM-001, SRC-001, etc.')
    require(isinstance(node['kind'], str) and node['kind'] in KINDS, 'Unknown node kind.')
    require(isinstance(node['title'], str) and bool(node['title'].strip()), 'Title required.')
    require(isinstance(node['status'], str) and node['status'] in STATUSES, 'Invalid status.')
    deps = node['depends_on']
    require(isinstance(deps, list) and all(isinstance(d, str) and ID_RE.fullmatch(d) for d in deps), 'Invalid dependency IDs.')
    require(len(deps) == len(set(deps)) and node['id'] not in deps, 'Duplicate or self dependency.')
    d = node['data']
    require(isinstance(d, dict), 'data must be an object.')
    if node['kind'] == 'source':
        require(isinstance(d.get('category'), str) and d['category'] in CATEGORIES, 'Source needs a supported category.')
        require(isinstance(d.get('url'), str) and bool(d['url'].strip()), 'Source needs original URL or local provenance URI.')
    if node['kind'] == 'claim':
        require(isinstance(d.get('strength'), str) and d['strength'] in STRENGTHS, 'Claim needs inference strength.')
        require(isinstance(d.get('text'), str) and bool(d['text'].strip()), 'Claim needs text.')
    if node['kind'] == 'evidence':
        for field in ('source', 'claim', 'quote', 'locator', 'scope'):
            require(isinstance(d.get(field), str) and bool(d[field].strip()), 'Evidence needs ' + field)
        require(d.get('relation') in ('supports', 'refutes', 'qualifies'), 'Invalid evidence relation.')
        require(d['source'] in deps, 'Evidence must depend on its source.')
    if node['kind'] == 'section':
        require(isinstance(d.get('text'), str), 'Section requires data.text Markdown.')
    if 'verification' in node:
        require(isinstance(node['verification'], dict), 'Invalid verification record.')
    canonical(node)


def make_node(node_id: str, kind: str, title: str, data: dict | None = None, depends_on: list[str] | None = None, status: str = 'draft') -> dict:
    node = {'id': node_id, 'kind': kind, 'title': title, 'status': status, 'depends_on': depends_on or [], 'data': data or {}}
    validate_node(node)
    return node


def validate_state(state: Any) -> None:
    require(isinstance(state, dict) and state.get('schema_version') == SCHEMA_VERSION, 'Unknown schema; do not guess a migration. See docs/UPDATING.md.')
    require(isinstance(state.get('revision'), int) and state['revision'] >= 0, 'Invalid revision.')
    for name, kind in (('project', dict), ('nodes', dict), ('proposals', dict), ('issues', dict), ('sync', dict), ('events', list), ('approvals', list), ('writers', list), ('tasks', list)):
        require(isinstance(state.get(name), kind), 'Invalid state field: ' + name)
    require(state['project'].get('mode') in ('research', 'demo'), 'Invalid project mode.')
    for key, node in state['nodes'].items():
        validate_node(node)
        require(key == node['id'], 'Node key mismatch: ' + key)


def impact(nodes: dict[str, dict], changed: list[str]) -> dict:
    """Cycle-safe closure; propagation follows dependency -> dependent."""
    require(all(i in nodes for i in changed), 'Impact roots must exist.')
    affected = set(changed)
    reasons = {i: [] for i in changed}
    queue = list(sorted(affected))
    while queue:
        current = queue.pop(0)
        for key, node in sorted(nodes.items()):
            if current in node['depends_on']:
                reasons.setdefault(key, []).append(current)
                if key not in affected:
                    affected.add(key)
                    queue.append(key)
    return {'changed': sorted(set(changed)), 'affected': sorted(affected), 'reasons': reasons,
            'sections': sorted(i for i in affected if nodes[i]['kind'] == 'section'),
            'figures': sorted(i for i in affected if nodes[i]['kind'] == 'figure')}
