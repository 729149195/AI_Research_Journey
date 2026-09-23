"""Public CLI. 0: completed; 1: quality/check blocked; 2: invalid or unsafe request."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from . import __version__
from .model import DOMAINS, KINDS, WorkspaceError, impact, pretty, require
from .store import Store, atomic_write, read_text, recover, safe_path


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='rw', description='Local-first AI Research Workspace. Start with: rw demo PATH')
    p.add_argument('--version', action='version', version=__version__)
    p.add_argument('--project', default='.', help='Study directory containing sibling workspace/ and manuscript/')
    sub = p.add_subparsers(dest='command', required=True)
    def actor(q): q.add_argument('--actor', required=True)
    def note(q): q.add_argument('--note', required=True)
    q = sub.add_parser('init'); q.add_argument('path'); q.add_argument('--name', required=True); q.add_argument('--author', required=True)
    q = sub.add_parser('demo'); q.add_argument('path')
    sub.add_parser('doctor'); sub.add_parser('status')
    q = sub.add_parser('show'); q.add_argument('id')
    q = sub.add_parser('nodes'); q.add_argument('--kind', choices=sorted(KINDS))
    q = sub.add_parser('propose'); q.add_argument('file'); actor(q); q.add_argument('--summary')
    q = sub.add_parser('apply'); q.add_argument('id'); actor(q); note(q); q.add_argument('--approve', action='store_true')
    q = sub.add_parser('reject'); q.add_argument('id'); actor(q); note(q)
    q = sub.add_parser('verify'); q.add_argument('id'); actor(q); note(q); q.add_argument('--human', action='store_true'); q.add_argument('--primary-for', default='')
    q = sub.add_parser('impact'); q.add_argument('ids', nargs='+')
    q = sub.add_parser('sync'); ss = q.add_subparsers(dest='action', required=True); ss.add_parser('status')
    q = ss.add_parser('propose'); actor(q); q.add_argument('--resolve', action='append', default=[], metavar='SECTION=workspace|manuscript'); q.add_argument('--acknowledge-outside', action='store_true')
    sub.add_parser('review')
    q = sub.add_parser('gate'); q.add_argument('--demonstration', action='store_true')
    q = sub.add_parser('attest'); q.add_argument('domain', choices=list(DOMAINS) + ['author_release']); actor(q); note(q); q.add_argument('--human', action='store_true')
    q = sub.add_parser('export'); q.add_argument('destination'); q.add_argument('--demonstration', action='store_true')
    sub.add_parser('dashboard')
    q = sub.add_parser('cycle'); actor(q)
    q = sub.add_parser('issue'); ss = q.add_subparsers(dest='action', required=True)
    q = ss.add_parser('add'); actor(q); q.add_argument('--node', default='MANUSCRIPT'); q.add_argument('--severity', choices=['critical', 'major', 'minor'], default='major'); q.add_argument('--message', required=True)
    q = ss.add_parser('resolve'); q.add_argument('id'); actor(q); note(q)
    q = sub.add_parser('packet'); q.add_argument('skill'); q.add_argument('--task', required=True); q.add_argument('--focus', action='append', default=[])
    q = sub.add_parser('skills'); ss = q.add_subparsers(dest='action', required=True)
    for name in ('list', 'lint', 'registry'): ss.add_parser(name)
    q = ss.add_parser('show'); q.add_argument('name')
    q = ss.add_parser('install'); q.add_argument('--target', choices=['.agents/skills', '.claude/skills'], required=True); q.add_argument('--overwrite', action='store_true')
    q = sub.add_parser('search'); q.add_argument('--query', required=True); q.add_argument('--limit', type=int, default=10); actor(q); q.add_argument('--online', action='store_true'); q.add_argument('--public-query', action='store_true')
    q = sub.add_parser('run'); q.add_argument('id'); actor(q); q.add_argument('--allow-exec', action='store_true'); q.add_argument('--timeout', type=int, default=60)
    q = sub.add_parser('ai'); ss = q.add_subparsers(dest='action', required=True)
    q = ss.add_parser('configure'); actor(q); note(q); q.add_argument('--enable', action='store_true'); q.add_argument('--host', action='append', default=[])
    q = ss.add_parser('run'); q.add_argument('skill'); q.add_argument('--task', required=True); q.add_argument('--model', required=True); q.add_argument('--endpoint', required=True); q.add_argument('--allow-network', action='store_true'); q.add_argument('--focus', action='append', default=[])
    q = sub.add_parser('recover'); q.add_argument('--clear-lock', action='store_true')
    q = sub.add_parser('upgrade'); ss = q.add_subparsers(dest='action', required=True)
    for action in ('check', 'apply'):
        q = ss.add_parser(action); q.add_argument('--source'); q.add_argument('--keep-local', action='append', default=[]); q.add_argument('--take-upstream', action='append', default=[])
        if action == 'apply': actor(q); q.add_argument('--approve', action='store_true')
    q = ss.add_parser('rollback'); q.add_argument('id')
    ss.add_parser('recover'); ss.add_parser('history')
    return p


def execute(a: argparse.Namespace) -> tuple[object, int]:
    from . import skills, workflow, sync, review, upgrade
    c = a.command
    if c == 'init':
        from .scaffold import initialize
        s = initialize(a.path, a.name, a.author)
        return {'created': str(s.root), 'next': 'Read START_HERE.md and fill workspace/research/idea-evaluation.md.'}, 0
    if c == 'demo':
        from .demo import demonstrate
        return demonstrate(a.path), 0
    if c == 'doctor':
        result = skills.lint_skills()
        return {'version': __version__, 'python': sys.version.split()[0], 'runtime_dependencies': [], 'skills': result}, 0 if result['passed'] else 1
    if c == 'recover': return recover(a.project, a.clear_lock), 0
    if c == 'upgrade':
        if a.action == 'check':
            result = upgrade.plan_upgrade(a.project, a.source, a.keep_local, a.take_upstream)
            return {k: v for k, v in result.items() if k not in ('changes', 'target', 'expected')}, 1 if result['conflicts'] else 0
        if a.action == 'apply': return upgrade.apply_upgrade(a.project, a.source, a.actor, approve=a.approve, keep_local=a.keep_local, take_upstream=a.take_upstream), 0
        if a.action == 'rollback': return upgrade.rollback(a.project, a.id), 0
        if a.action == 'recover': return upgrade.recover_upgrade(a.project), 0
        root = Path(a.project).expanduser().resolve()
        require((root / 'workspace/state.json').is_file(), 'Study missing.')
        folder = safe_path(root, '.rw/backups', governed=False)
        return [{k: v for k, v in json.loads(read_text(path)).items() if k not in ('before', 'after')} for path in sorted(folder.glob('UPDATE-*.json'))], 0
    if c == 'skills':
        if a.action == 'list': return list(skills.SKILLS), 0
        if a.action == 'registry': return json.loads(read_text(skills.ASSETS / 'skills.lock.json')), 0
        if a.action in ('lint', 'show') and not (Path(a.project) / 'workspace/state.json').exists():
            result = skills.lint_skills() if a.action == 'lint' else skills.skill_text(None, a.name)
            return result, 0 if isinstance(result, str) or result['passed'] else 1
    s = Store(a.project)
    if c == 'status':
        return {'project': s.state['project'], 'revision': s.state['revision'], 'node_count': len(s.state['nodes']), 'fingerprint': s.fingerprint(),
                'pending_proposals': [p['id'] for p in s.state['proposals'].values() if p['status'] == 'pending'],
                'open_issues': [i for i in s.state['issues'].values() if i['status'] == 'open']}, 0
    if c == 'show': return s.state['proposals'].get(a.id) or s.state['issues'].get(a.id) or s.node(a.id), 0
    if c == 'nodes': return [n for n in s.state['nodes'].values() if not a.kind or n['kind'] == a.kind], 0
    if c == 'propose':
        data = json.loads(read_text(Path(a.file)))
        require(isinstance(data, dict), 'Proposal file needs summary and operations.')
        if 'base_fingerprint' in data: require(data['base_fingerprint'] == s.fingerprint(), 'Task packet is stale.')
        return workflow.propose(s, data.get('operations'), a.actor, a.summary or data.get('summary', 'Imported proposal')), 0
    if c == 'apply': return workflow.apply(s, a.id, a.actor, a.note, approve=a.approve), 0
    if c == 'reject': return workflow.reject(s, a.id, a.actor, a.note), 0
    if c == 'verify': return workflow.verify(s, a.id, a.actor, a.note, human=a.human, primary_for=a.primary_for), 0
    if c == 'impact': return impact(s.state['nodes'], a.ids), 0
    if c == 'sync':
        if a.action == 'status':
            result = sync.plan(s)
            return {k: v for k, v in result.items() if k not in ('manuscript_text', 'outside')}, 1 if result['conflicts'] else 0
        choices = {}
        for choice in a.resolve:
            require('=' in choice, 'Use SECTION=workspace or SECTION=manuscript.')
            key, value = choice.split('=', 1); choices[key] = value
        return sync.propose_sync(s, a.actor, choices, a.acknowledge_outside), 0
    if c == 'review':
        result = review.save_report(s)
        return result, 1 if result['machine_status'] == 'blocked' else 0
    if c == 'gate':
        result = review.gate(s, demonstration=a.demonstration)
        return result, 0 if result['ready_for_packaging'] else 1
    if c == 'attest': return review.attest(s, a.domain, a.actor, a.note, human=a.human), 0
    if c == 'export': return review.export_bundle(s, a.destination, demonstration=a.demonstration), 0
    if c == 'dashboard':
        from .dashboard import dashboard
        return dashboard(s), 0
    if c == 'cycle': return skills.cycle(s, a.actor), 0
    if c == 'issue':
        if a.action == 'resolve': return workflow.resolve_issue(s, a.id, a.actor, a.note), 0
        return workflow.add_issue(s, a.node, a.message, a.actor, a.severity), 0
    if c == 'packet':
        packet = skills.task_packet(s, a.skill, a.task, a.focus)
        path = safe_path(s.root, 'workspace/reports/' + packet['task_id'] + '.json')
        atomic_write(path, pretty(packet))
        return {'packet': str(path), 'base_fingerprint': packet['base_fingerprint'], 'next': 'Give authorized context to your agent, then import only its proposed JSON operations.'}, 0
    if c == 'skills':
        if a.action == 'show': return skills.skill_text(s, a.name), 0
        if a.action == 'install': return skills.install_skills(s, a.target, overwrite=a.overwrite), 0
        result = skills.lint_skills(s)
        return result, 0 if result['passed'] else 1
    if c == 'search':
        from .adapters import search_crossref
        return search_crossref(s, a.query, a.limit, a.actor, online=a.online, public_query=a.public_query), 0
    if c == 'run':
        from .analysis import run_method
        return run_method(s, a.id, a.actor, allow_exec=a.allow_exec, timeout=a.timeout), 0
    if c == 'ai':
        from .adapters import configure_ai, run_agent
        if a.action == 'configure': return configure_ai(s, a.enable, a.host, a.actor, a.note), 0
        return run_agent(s, a.skill, a.task, model=a.model, endpoint=a.endpoint, allow_network=a.allow_network, focus=a.focus), 0
    raise WorkspaceError('Unknown command.')


def main(argv: list[str] | None = None) -> int:
    try:
        result, code = execute(parser().parse_args(argv))
        print(result if isinstance(result, str) else pretty(result), end='\n' if isinstance(result, str) else '')
        return code
    except (WorkspaceError, OSError, ValueError, TypeError, KeyError) as exc:
        print(pretty({'error': str(exc), 'type': type(exc).__name__}), file=sys.stderr, end='')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
