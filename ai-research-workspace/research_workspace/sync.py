"""Stable-section Markdown synchronization. Never choose a conflict silently."""
from __future__ import annotations
import copy
import re
from .model import digest, require
from .store import Store, file_hash, read_text, safe_path
from .workflow import propose

PATTERN = re.compile(r'<!-- rw:section ([A-Z][A-Z0-9]*-[A-Z0-9_-]+) -->\n(.*?)\n<!-- /rw:section \1 -->', re.S)


def block(node_id: str, text: str) -> str:
    return '<!-- rw:section ' + node_id + ' -->\n' + text + '\n<!-- /rw:section ' + node_id + ' -->'


def parse(text: str) -> tuple[dict[str, str], str]:
    sections = {}
    matches = list(PATTERN.finditer(text))
    for match in matches:
        key = match.group(1)
        require(key not in sections, 'Duplicate manuscript section marker: ' + key)
        sections[key] = match.group(2)
    outside = PATTERN.sub('', text)
    require('<!-- rw:section' not in outside and '<!-- /rw:section' not in outside, 'Malformed or unmatched section markers.')
    return sections, outside


def plan(store: Store) -> dict:
    text = read_text(safe_path(store.root, 'manuscript/main.md'))
    manuscript, outside = parse(text)
    active = {i: n for i, n in store.state['nodes'].items() if n['kind'] == 'section' and n['status'] != 'retired'}
    require(set(manuscript) == set(active), 'Section marker/node IDs differ; reconcile the structure explicitly first.')
    baseline = store.state['sync']
    changes, conflicts, semantic = [], [], []
    for key, node in sorted(active.items()):
        ws, ms, base = node['data']['text'], manuscript[key], baseline.get('sections', {}).get(key)
        if ws == ms:
            if base != ws:
                changes.append({'section': key, 'direction': 'acknowledge', 'before': base, 'after': ws})
                semantic.append(key)
        elif ws == base:
            changes.append({'section': key, 'direction': 'manuscript-to-workspace', 'before': ws, 'after': ms})
            semantic.append(key)
        elif ms == base:
            changes.append({'section': key, 'direction': 'workspace-to-manuscript', 'before': ms, 'after': ws})
        else:
            conflicts.append({'section': key, 'base': base, 'workspace': ws, 'manuscript': ms})
    return {'changes': changes, 'conflicts': conflicts, 'semantic_review': semantic,
            'outside_changed': digest(outside) != baseline.get('outside_hash'),
            'manuscript_text': text, 'outside': outside}


def propose_sync(store: Store, actor: str, resolutions: dict[str, str] | None = None, acknowledge_outside: bool = False) -> dict:
    result = plan(store)
    choices = resolutions or {}
    conflict_ids = {c['section'] for c in result['conflicts']}
    require(set(choices) <= conflict_ids, 'Resolution refers to a section without a current conflict.')
    require(all(v in ('workspace', 'manuscript') for v in choices.values()), 'Resolution must be workspace or manuscript.')
    require(conflict_ids <= set(choices), 'Both sides changed; inspect conflicts and choose explicit --resolve SECTION=workspace|manuscript.')
    require(not result['outside_changed'] or acknowledge_outside, 'Unmapped manuscript text changed; inspect it and use --acknowledge-outside.')
    require(result['changes'] or result['conflicts'] or result['outside_changed'], 'Already synchronized.')
    operations, semantic = [], set(result['semantic_review'])
    text = result['manuscript_text']
    manuscript, outside = parse(text)
    final = {key: node['data']['text'] for key, node in store.state['nodes'].items() if node['kind'] == 'section' and node['status'] != 'retired'}
    changes = list(result['changes'])
    for conflict in result['conflicts']:
        key = conflict['section']
        side = choices[key]
        changes.append({'section': key, 'direction': 'manuscript-to-workspace' if side == 'manuscript' else 'workspace-to-manuscript', 'after': conflict[side]})
        semantic.add(key)
    for change in changes:
        key, new = change['section'], change['after']
        final[key] = new
        if change['direction'] == 'manuscript-to-workspace':
            node = copy.deepcopy(store.node(key))
            node['data']['text'] = new
            operations.append({'op': 'upsert', 'node': node})
        elif change['direction'] == 'workspace-to-manuscript':
            text = text.replace(block(key, manuscript[key]), block(key, new), 1)
    # One no-op text write is intentional for pure baseline acknowledgments.
    operations.append({'op': 'write', 'path': 'manuscript/main.md', 'text': text,
                       'expected_sha256': file_hash(safe_path(store.root, 'manuscript/main.md'))})
    if result['outside_changed']:
        semantic.add('MANUSCRIPT')
    proposal = propose(store, operations, actor, 'Synchronize research and manuscript using an explicit three-way comparison')
    proposal['sync_commit'] = {'baseline': {'sections': final, 'outside_hash': digest(outside)}, 'semantic_review': sorted(semantic)}
    store.state['proposals'][proposal['id']] = proposal
    store.event('sync.proposed', actor, {'id': proposal['id'], 'resolutions': choices})
    store.commit()
    return proposal
