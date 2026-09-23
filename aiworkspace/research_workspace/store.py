"""Readable local state with hash-based concurrency and recoverable multi-file writes."""
from __future__ import annotations
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from .model import WorkspaceError, digest, now, pretty, require, validate_state

STATE = 'workspace/state.json'
MAX_TEXT_BYTES = 8 * 1024 * 1024


def safe_path(root: Path, relative: str, *, governed: bool = True) -> Path:
    require(isinstance(relative, str) and bool(relative), 'Relative path required.')
    require('\\' not in relative and ':' not in relative, 'Use relative POSIX paths.')
    rel = Path(relative)
    require(bool(rel.parts) and not rel.is_absolute() and '..' not in rel.parts and '.git' not in rel.parts, 'Unsafe path.')
    if governed:
        require(rel.parts[0] in ('workspace', 'manuscript'), 'Only workspace/ and manuscript/ are governed.')
    current = root
    for part in rel.parts:
        current = current / part
        require(not current.is_symlink(), 'Symlinks are not permitted: ' + relative)
    require(current.resolve().is_relative_to(root.resolve()), 'Path escapes project.')
    return current


def file_hash(path: Path) -> str | None:
    require(not path.is_symlink(), 'Cannot hash a symlink.')
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    require(path.is_file() and not path.is_symlink(), 'File missing or symlink: ' + str(path))
    require(path.stat().st_size <= MAX_TEXT_BYTES, 'Text exceeds 8 MiB; use a bounded UTF-8 extract.')
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeError as exc:
        raise WorkspaceError('Expected UTF-8 text; explicitly convert binary sources first.') from exc


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.rw-tmp')
    require(not path.is_symlink() and not temp.is_symlink(), 'Unsafe write target.')
    with temp.open('w', encoding='utf-8', newline='\n') as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


@contextmanager
def project_lock(root: Path) -> Iterator[None]:
    safe_path(root, '.rw', governed=False).mkdir(exist_ok=True)
    lock = safe_path(root, '.rw/write.lock', governed=False)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise WorkspaceError('Another writer holds .rw/write.lock. Only after confirming it stopped, use recover --clear-lock.') from exc
    try:
        with os.fdopen(fd, 'w') as handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        lock.unlink(missing_ok=True)


class Store:
    def __init__(self, root: str | Path):
        self.root = Path(root).expanduser().resolve()
        require(self.root.is_dir(), 'Project missing. Start with rw init PATH.')
        for journal, command in (('.rw/transaction.json', 'recover'), ('.rw/update-transaction.json', 'upgrade recover')):
            require(not safe_path(self.root, journal, governed=False).exists(), 'Interrupted operation: run rw --project PATH ' + command)
        self.state = json.loads(read_text(safe_path(self.root, STATE)))
        validate_state(self.state)
        self.loaded_hash = file_hash(safe_path(self.root, STATE))

    def node(self, node_id: str) -> dict:
        require(node_id in self.state['nodes'], 'Unknown ID: ' + node_id)
        return self.state['nodes'][node_id]

    def files(self) -> dict[str, str]:
        result = {}
        for folder in ('workspace', 'manuscript'):
            for path in sorted(safe_path(self.root, folder).rglob('*')):
                require(not path.is_symlink(), 'Symlink in project: ' + str(path))
                if not path.is_file():
                    continue
                name = path.relative_to(self.root).as_posix()
                if name != STATE and not name.startswith('workspace/reports/'):
                    result[name] = file_hash(path)
        for name in ('AGENTS.md', 'CLAUDE.md', 'START_HERE.md'):
            path = safe_path(self.root, name, governed=False)
            if path.exists():
                result[name] = file_hash(path)
        return result

    def fingerprint(self) -> str:
        from . import __version__
        return digest({'engine': __version__, 'project': self.state['project'], 'nodes': self.state['nodes'],
                       'issues': self.state['issues'], 'files': self.files()})

    def event(self, action: str, actor: str, detail: dict | None = None) -> None:
        require(isinstance(actor, str) and bool(actor.strip()), 'Accountable actor required.')
        previous = self.state['events'][-1]['hash'] if self.state['events'] else '0' * 64
        event = {'at': now(), 'action': action, 'actor': actor, 'detail': detail or {}, 'previous': previous}
        event['hash'] = digest(event)
        self.state['events'].append(event)

    def commit(self, changes: dict[str, str] | None = None, expected: dict[str, str | None] | None = None) -> None:
        changes, expected = changes or {}, expected or {}
        require(STATE not in changes, 'Use domain operations to change state.')
        for name, text in changes.items():
            safe_path(self.root, name)
            require(isinstance(text, str) and len(text.encode()) <= MAX_TEXT_BYTES, 'Invalid or oversized write.')
            require(name in expected, 'Missing expected hash: ' + name)
        validate_state(self.state)
        with project_lock(self.root):
            require(file_hash(safe_path(self.root, STATE)) == self.loaded_hash, 'Concurrent state change; reload and recreate proposal.')
            require(not safe_path(self.root, '.rw/update-transaction.json', governed=False).exists(), 'Recover asset update first.')
            journal = safe_path(self.root, '.rw/transaction.json', governed=False)
            require(not journal.exists(), 'Recover interrupted transaction first.')
            for name, sha in expected.items():
                require(file_hash(safe_path(self.root, name)) == sha, 'Concurrent file change: ' + name)
            self.state['revision'] += 1
            writes = {**changes, STATE: pretty(self.state)}
            before = {name: file_hash(safe_path(self.root, name)) for name in writes}
            atomic_write(journal, pretty({'version': 1, 'writes': writes, 'before': before}))
            for name, text in writes.items():
                atomic_write(safe_path(self.root, name), text)
            journal.unlink()
            self.loaded_hash = file_hash(safe_path(self.root, STATE))


def recover(root: str | Path, clear_lock: bool = False) -> dict:
    root = Path(root).expanduser().resolve()
    require(root.is_dir(), 'Project missing.')
    if clear_lock:
        safe_path(root, '.rw/write.lock', governed=False).unlink(missing_ok=True)
    with project_lock(root):
        journal = safe_path(root, '.rw/transaction.json', governed=False)
        if not journal.exists():
            return {'recovered': False, 'message': 'No interrupted research transaction.'}
        data = json.loads(read_text(journal))
        require(data.get('version') == 1 and isinstance(data.get('writes'), dict) and isinstance(data.get('before'), dict), 'Invalid recovery journal.')
        require(STATE in data['writes'] and set(data['writes']) == set(data['before']), 'Incomplete recovery journal.')
        validate_state(json.loads(data['writes'][STATE]))
        for name, text in data['writes'].items():
            require(isinstance(text, str), 'Invalid journal content.')
            current = file_hash(safe_path(root, name))
            require(current in (data['before'][name], digest(text.encode('utf-8'))), 'New local changes would be overwritten during recovery: ' + name)
        for name, text in data['writes'].items():
            atomic_write(safe_path(root, name), text)
        journal.unlink()
    return {'recovered': True, 'files': sorted(data['writes'])}
