"""Incremental framework-asset upgrades. Study data and manuscripts are never targets."""
from __future__ import annotations
import difflib
import json
import re
from pathlib import Path
from .model import SCHEMA_VERSION, digest, identifier, now, pretty, require
from .store import atomic_write, file_hash, project_lock, read_text, safe_path

ASSETS = Path(__file__).parent / 'assets'
BASELINE = '.rw/framework.json'
JOURNAL = '.rw/update-transaction.json'


def owned(path: str) -> bool:
    return path in ('AGENTS.md', 'CLAUDE.md', 'START_HERE.md', 'workspace/skills.lock.json', 'workspace/rules/framework-policy.md') or bool(re.fullmatch(r'workspace/templates/[a-z0-9_.-]+\.md', path)) or bool(re.fullmatch(r'(?:workspace/skills|\.agents/skills|\.claude/skills)/[a-z0-9-]+/SKILL\.md', path))


def read_optional(root: Path, path: str) -> str | None:
    target = safe_path(root, path, governed=False)
    return read_text(target) if target.exists() else None


def release(source: str | Path | None = None, hosts: list[str] | None = None) -> dict:
    assets = Path(source).expanduser().resolve() / 'research_workspace/assets' if source else ASSETS
    config = json.loads(read_text(assets / 'release.json'))
    require(config.get('manifest_version') == 1, 'Unknown release manifest.')
    require(config.get('schema_version') == SCHEMA_VERSION, 'Unknown schema; install a reviewed migration-capable engine first. No study data changed.')
    require(isinstance(config.get('version'), str) and isinstance(config.get('files'), dict), 'Malformed release.')
    files = {}
    for target, relative in config['files'].items():
        require(owned(target), 'Release attempted to target user research: ' + target)
        files[target] = read_text(safe_path(assets, relative, governed=False))
    for host in hosts or []:
        require(host in ('.agents/skills', '.claude/skills'), 'Unknown Skill host path.')
        for path, text in list(files.items()):
            if path.startswith('workspace/skills/'):
                files[host + '/' + path.removeprefix('workspace/skills/')] = text
    return {'manifest_version': 1, 'version': config['version'], 'schema_version': config['schema_version'],
            'hosts': sorted(set(hosts or [])), 'files': files, 'release_hash': digest({'version': config['version'], 'files': files})}


def initialize_baseline(root: Path) -> None:
    require(not safe_path(root, BASELINE, governed=False).exists(), 'Installation baseline already exists.')
    baseline = release()
    for path, text in baseline['files'].items():
        atomic_write(safe_path(root, path, governed=False), text)
    atomic_write(safe_path(root, BASELINE, governed=False), pretty(baseline))


def register_host(root: Path, host: str) -> None:
    require(host in ('.agents/skills', '.claude/skills'), 'Unknown host path.')
    path = safe_path(root, BASELINE, governed=False)
    with project_lock(root):
        baseline = json.loads(read_text(path))
        baseline['hosts'] = sorted(set(baseline['hosts']) | {host})
        for key, text in list(baseline['files'].items()):
            if key.startswith('workspace/skills/'):
                baseline['files'][host + '/' + key.removeprefix('workspace/skills/')] = text
        atomic_write(path, pretty(baseline))


def merge_text(base: str | None, local: str | None, remote: str | None) -> tuple[str, str | None]:
    if local == remote:
        return 'unchanged', local
    if remote == base:
        return 'local-only', local
    if local == base:
        return ('removed' if remote is None else 'updated'), remote
    if base is None or local is None or remote is None:
        return 'conflict', None
    old = base.splitlines(keepends=True)
    def edits(text):
        lines = text.splitlines(keepends=True)
        return [(a, b, lines[c:d]) for tag, a, b, c, d in difflib.SequenceMatcher(None, old, lines, autojunk=False).get_opcodes() if tag != 'equal']
    le, re_ = edits(local), edits(remote)
    for a, b, content in le:
        for c, d, content2 in re_:
            if max(a, c) <= min(b, d) and (a, b, content) != (c, d, content2):
                return 'conflict', None
    merged = old[:]
    for a, b, content in sorted({(a, b, tuple(content)) for a, b, content in le + re_}, reverse=True):
        merged[a:b] = content
    return 'merged', ''.join(merged)


def plan_upgrade(root: str | Path, source: str | Path | None = None, keep_local: list[str] | None = None, take_upstream: list[str] | None = None) -> dict:
    root = Path(root).expanduser().resolve()
    require(root.is_dir(), 'Study directory missing.')
    require(not safe_path(root, JOURNAL, governed=False).exists(), 'Run rw upgrade recover first.')
    require(not safe_path(root, '.rw/transaction.json', governed=False).exists(), 'Recover research transaction first.')
    baseline_path = safe_path(root, BASELINE, governed=False)
    require(baseline_path.exists(), 'Restore .rw/framework.json from your backup; do not invent a used study baseline.')
    baseline = json.loads(read_text(baseline_path))
    require(baseline.get('manifest_version') == 1 and isinstance(baseline.get('files'), dict), 'Invalid installation baseline.')
    state_path = safe_path(root, 'workspace/state.json')
    state = json.loads(read_text(state_path))
    require(state.get('schema_version') == SCHEMA_VERSION, 'No reviewed migration for this study schema.')
    target = release(source, baseline.get('hosts', []))
    keep, take = set(keep_local or []), set(take_upstream or [])
    keys = set(baseline['files']) | set(target['files'])
    require(not keep & take and (keep | take) <= keys, 'Conflicting or unmanaged resolution path.')
    changes, conflicts, entries, expected = {}, [], [], {}
    for path in sorted(keys):
        require(owned(path), 'Unsafe baseline target: ' + path)
        local, remote = read_optional(root, path), target['files'].get(path)
        action, merged = merge_text(baseline['files'].get(path), local, remote)
        if path in keep:
            action, merged = 'keep-local', local
        elif path in take:
            action, merged = 'take-upstream', remote
        expected[path] = file_hash(safe_path(root, path, governed=False))
        if action == 'conflict':
            conflicts.append(path)
        elif merged != local:
            changes[path] = merged
        delta = '' if action == 'conflict' else ''.join(difflib.unified_diff((local or '').splitlines(True), (merged or '').splitlines(True), fromfile='local/' + path, tofile='updated/' + path))
        entries.append({'path': path, 'action': action, 'diff': delta})
    return {'from_version': baseline['version'], 'to_version': target['version'], 'conflicts': conflicts, 'entries': entries,
            'changes': changes, 'target': target, 'expected': expected, 'baseline_sha256': file_hash(baseline_path),
            'state_sha256': file_hash(state_path), 'update_needed': bool(changes) or baseline != target,
            'boundary': 'Only managed defaults change. Filled research, evidence, data, code, project-specific policy and manuscript are never asset targets.'}


def _write(root: Path, path: str, text: str | None) -> None:
    target = safe_path(root, path, governed=False)
    if text is None:
        target.unlink(missing_ok=True)
    else:
        atomic_write(target, text)


def apply_upgrade(root: str | Path, source: str | Path | None, actor: str, *, approve: bool = False, keep_local: list[str] | None = None, take_upstream: list[str] | None = None) -> dict:
    require(approve and bool(actor.strip()), 'Review differences, then supply --approve and --actor.')
    root = Path(root).expanduser().resolve()
    result = plan_upgrade(root, source, keep_local, take_upstream)
    require(not result['conflicts'], 'Asset conflicts; nothing changed. Review explicit --keep-local/--take-upstream choices.')
    if not result['update_needed']:
        return {'updated': False, 'message': 'Already current; local customizations preserved.'}
    writes = {**result['changes'], BASELINE: pretty(result['target'])}
    with project_lock(root):
        require(file_hash(safe_path(root, BASELINE, governed=False)) == result['baseline_sha256'], 'Baseline changed; retry.')
        require(file_hash(safe_path(root, 'workspace/state.json')) == result['state_sha256'], 'Research changed; retry.')
        for path, sha in result['expected'].items():
            require(file_hash(safe_path(root, path, governed=False)) == sha, 'Local file changed during update: ' + path)
        backup_id = identifier('UPDATE')
        backup = {'backup_id': backup_id, 'status': 'prepared', 'at': now(), 'actor': actor,
                  'from_version': result['from_version'], 'to_version': result['to_version'],
                  'before': {p: read_optional(root, p) for p in writes}, 'after': writes,
                  'boundary': 'Incremental asset backup, not a full research-data backup.'}
        backup_path = safe_path(root, '.rw/backups/' + backup_id + '.json', governed=False)
        atomic_write(backup_path, pretty(backup))
        journal = safe_path(root, JOURNAL, governed=False)
        atomic_write(journal, pretty({'backup_id': backup_id}))
        for path, text in writes.items():
            _write(root, path, text)
        backup['status'] = 'applied'
        atomic_write(backup_path, pretty(backup))
        journal.unlink()
    return {'updated': True, 'backup_id': backup_id, 'version': result['to_version'], 'changed_files': sorted(result['changes']),
            'note': 'Re-run sync and review. Changed engine or assets invalidate old snapshot approvals.'}


def rollback(root: str | Path, backup_id: str, *, recover: bool = False) -> dict:
    root = Path(root).expanduser().resolve()
    require(bool(re.fullmatch(r'UPDATE-[A-F0-9]{12}', backup_id)), 'Invalid backup ID.')
    require(not safe_path(root, '.rw/transaction.json', governed=False).exists(), 'Recover research transaction first.')
    with project_lock(root):
        backup_path = safe_path(root, '.rw/backups/' + backup_id + '.json', governed=False)
        backup = json.loads(read_text(backup_path))
        journal = safe_path(root, JOURNAL, governed=False)
        if journal.exists():
            require(json.loads(read_text(journal)).get('backup_id') == backup_id, 'Recover the other interrupted asset operation first.')
        require(backup.get('status') in ('prepared', 'applied', 'rolled_back'), 'Invalid backup status.')
        require(set(backup['before']) == set(backup['after']), 'Corrupt backup targets.')
        for path, after in backup['after'].items():
            require(path == BASELINE or owned(path), 'Unsafe backup path.')
            current = read_optional(root, path)
            if backup['status'] == 'rolled_back':
                require(current == backup['before'][path], 'Already rolled back; subsequent edits must be preserved.')
            else:
                allowed = (after, backup['before'][path]) if recover else (after,)
                require(current in allowed, 'New local edits would be overwritten by rollback: ' + path)
        if not journal.exists():
            atomic_write(journal, pretty({'backup_id': backup_id}))
        for path, before in backup['before'].items():
            _write(root, path, before)
        backup.update(status='rolled_back', rolled_back_at=now())
        atomic_write(backup_path, pretty(backup))
        journal.unlink()
    return {'rolled_back': backup_id, 'boundary': 'Restored assets only. Research and manuscript are unchanged; engine code rollback is separate.'}


def recover_upgrade(root: str | Path) -> dict:
    root = Path(root).expanduser().resolve()
    journal = safe_path(root, JOURNAL, governed=False)
    require(journal.exists(), 'No interrupted asset update/rollback.')
    return rollback(root, json.loads(read_text(journal))['backup_id'], recover=True)
