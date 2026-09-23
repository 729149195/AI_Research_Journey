"""New study scaffolding. Refuses to overwrite existing user work."""
from __future__ import annotations
from pathlib import Path
from .model import SCHEMA_VERSION, digest, make_node, now, pretty, require
from .store import Store, atomic_write, read_text
from .sync import block, parse
from .upgrade import initialize_baseline

SECTION_NAMES = {'SEC-ABSTRACT': 'Abstract', 'SEC-INTRO': 'Introduction', 'SEC-METHODS': 'Methods',
                 'SEC-RESULTS': 'Results', 'SEC-DISCUSSION': 'Discussion', 'SEC-CONCLUSION': 'Conclusion'}


def initialize(destination: str | Path, name: str, author: str, *, mode: str = 'research') -> Store:
    path = Path(destination).expanduser()
    require(not path.is_symlink(), 'Study root cannot be a symlink.')
    root = path.resolve()
    require(not root.exists() or (root.is_dir() and not any(root.iterdir())), 'Refusing to overwrite a nonempty directory.')
    require(bool(name.strip()) and bool(author.strip()) and mode in ('research', 'demo'), 'Project name, author and valid mode required.')
    root.mkdir(parents=True, exist_ok=True)
    for folder in ('research', 'sources/snapshots', 'sources/searches', 'evidence', 'methods', 'data', 'results', 'rules', 'figures', 'history', 'sync', 'reports'):
        (root / 'workspace' / folder).mkdir(parents=True, exist_ok=True)
    for folder in ('figures', 'supplementary'):
        (root / 'manuscript' / folder).mkdir(parents=True, exist_ok=True)
    (root / '.rw').mkdir()
    initialize_baseline(root)
    atomic_write(root / 'workspace/research/idea-evaluation.md', read_text(root / 'workspace/templates/idea-evaluation.md'))
    atomic_write(root / 'workspace/rules/project-policy.md', '# Project-specific policy\n\nRecord the actual venue, supervisor, institution, ethics, external-AI authorization, retention, citation, language and terminology rules. Include original source, access date and applicability. Unknown requirements remain unknown.\n\nThis file is user-owned and never replaced by framework upgrades.\n')
    atomic_write(root / 'workspace/memory.md', '# Non-evidentiary project memory\n\nSave session handover, unresolved questions and next steps here. Decisions and AI memory do not establish facts.\n')
    atomic_write(root / 'manuscript/supplementary/README.md', '# Supplementary materials\n\nRegister actual data/code/material availability and permissions before release. Do not invent declarations.\n')
    nodes = {}
    for node in (
        make_node('RQ-001', 'question', 'Research question', {'text': 'TODO: formulate a bounded research question.'}),
        make_node('HYP-001', 'hypothesis', 'Hypothesis / core idea', {'text': 'TODO: state what is proposed and what would test it.'}, ['RQ-001']),
        make_node('ARG-001', 'argument', 'Overall argument', {'text': 'TODO: explain why the evidence and methods can answer the question.'}, ['HYP-001'])
    ):
        nodes[node['id']] = node
    for key, title in SECTION_NAMES.items():
        nodes[key] = make_node(key, 'section', title, {'text': '## ' + title + '\n\nTODO: draft only from confirmed logic and evidence.'}, ['ARG-001'])
    text = '# ' + name + '\n\n' + '\n\n'.join(block(key, nodes[key]['data']['text']) for key in SECTION_NAMES) + '\n'
    atomic_write(root / 'manuscript/main.md', text)
    sections, outside = parse(text)
    state = {'schema_version': SCHEMA_VERSION, 'revision': 0,
             'project': {'name': name, 'author': author, 'mode': mode, 'created_at': now(), 'external_ai': {'enabled': False, 'allowed_hosts': []}},
             'nodes': nodes, 'proposals': {}, 'issues': {}, 'events': [], 'approvals': [], 'writers': [], 'tasks': [],
             'sync': {'sections': sections, 'outside_hash': digest(outside)}}
    atomic_write(root / 'workspace/state.json', pretty(state))
    atomic_write(root / '.gitignore', '.rw/*\n!.rw/framework.json\ndist/\n.env\n.env.*\n__pycache__/\n*.pyc\nworkspace/reports/\n')
    store = Store(root)
    store.event('project.initialized', author, {'mode': mode, 'boundary': 'No sources, results or human approvals have been invented.'})
    store.commit()
    return store
