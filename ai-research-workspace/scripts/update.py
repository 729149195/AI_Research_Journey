#!/usr/bin/env python3
"""Incrementally fetch a reviewed Git commit, fast-forward engine, and merge study defaults.

No reset --hard, automatic stash, clean, force-push or execution of fetched code in --check.
Activate a dedicated virtual environment and close active study writers before --apply.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
from research_workspace.model import WorkspaceError, now, pretty, require
from research_workspace.store import atomic_write
from research_workspace.upgrade import plan_upgrade


def git(root: Path, *args: str, binary: bool = False) -> str | bytes:
    hooks = 'core.hooksPath=NUL' if sys.platform == 'win32' else 'core.hooksPath=/dev/null'
    process = subprocess.run(['git', '-c', hooks, '-C', str(root), *args], capture_output=True, timeout=180, check=False)
    require(process.returncode == 0, 'Git failed: ' + process.stderr.decode('utf-8', 'replace')[-2000:])
    return process.stdout if binary else process.stdout.decode('utf-8').strip()


def stage_commit(root: Path, commit: str, relative: str, destination: Path) -> Path:
    archive = git(root, 'archive', '--format=zip', commit, '--', relative, binary=True)
    require(len(archive) <= 64 * 1024 * 1024, 'Framework archive exceeds 64 MiB; review distribution contents.')
    with zipfile.ZipFile(BytesIO(archive)) as data:
        require(len(data.infolist()) <= 4000 and sum(i.file_size for i in data.infolist()) <= 128 * 1024 * 1024, 'Oversized framework archive.')
        for info in data.infolist():
            path = Path(info.filename)
            require(not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename, 'Unsafe archive path.')
            require((info.external_attr >> 16) & 0o170000 != 0o120000, 'Symlinks are not accepted in a release.')
            target = destination / path
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data.read(info))
    return destination / relative


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, help='Used study, outside the framework checkout')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--apply', action='store_true')
    parser.add_argument('--actor', default='local-user')
    parser.add_argument('--remote', default='origin')
    parser.add_argument('--ref', default='origin/main', help='Existing/fetched branch, tag or commit; pinned to SHA before applying')
    parser.add_argument('--offline', action='store_true', help='Use already-fetched Git objects')
    parser.add_argument('--keep-local', action='append', default=[])
    parser.add_argument('--take-upstream', action='append', default=[])
    a = parser.parse_args()
    try:
        for value in (a.remote, a.ref):
            require(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9/._-]*', value) is not None, 'Invalid remote/ref.')
        root = Path(git(PACKAGE, 'rev-parse', '--show-toplevel'))
        study = Path(a.project).expanduser().resolve()
        require(not study.is_relative_to(root), 'Move studies outside the framework checkout before updating.')
        relative = PACKAGE.relative_to(root).as_posix()
        old = git(root, 'rev-parse', 'HEAD')
        if not a.offline:
            git(root, 'fetch', '--no-tags', a.remote)
        target = git(root, 'rev-parse', '--verify', a.ref + '^{commit}')
        require(re.fullmatch(r'[a-f0-9]{40,64}', target) is not None, 'Invalid commit.')
        dirty = git(root, 'status', '--porcelain')
        ancestry = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', old, target], capture_output=True).returncode == 0
        with tempfile.TemporaryDirectory(prefix='rw-update-') as temporary:
            staged = stage_commit(root, target, relative, Path(temporary))
            assets = plan_upgrade(study, staged, a.keep_local, a.take_upstream)
            report = {'current_commit': old, 'target_commit': target, 'dirty_checkout': bool(dirty), 'fast_forward': ancestry,
                      'repository_diff': git(root, 'diff', '--stat', old, target),
                      'project_asset_changes': [entry for entry in assets['entries'] if entry['path'] in assets['changes']],
                      'preserved_local_customizations': [e['path'] for e in assets['entries'] if e['action'] in ('local-only', 'keep-local')],
                      'conflicts': assets['conflicts'], 'project_untouched': True,
                      'note': 'Check only reads new release data. Apply explicitly trusts and installs its code. Asset backups are not full research backups.'}
            print(pretty(report), end='')
            if a.check:
                return 1 if dirty or not ancestry or assets['conflicts'] else 0
            require(sys.prefix != sys.base_prefix, 'Activate a dedicated virtual environment before --apply.')
            require(not dirty, 'Commit or preserve local/untracked engine edits yourself; updater never stashes or overwrites them.')
            require(ancestry, 'Branches diverged. Review and merge in Git yourself; no force reset is allowed.')
            require(not assets['conflicts'], 'Resolve asset conflicts before applying. No engine or study files changed.')
            backup_ref = 'refs/rw-backups/' + old[:12]
            git(root, 'update-ref', backup_ref, old)
            git(root, 'merge', '--ff-only', target)
            installed = subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-deps', '--no-build-isolation', '-e', str(PACKAGE)], check=False)
            require(installed.returncode == 0, 'Engine install failed; study assets NOT updated. Old code is at ' + backup_ref + '. See docs/UPDATING.md.')
            command = [sys.executable, '-m', 'research_workspace', '--project', str(study), 'upgrade', 'apply', '--source', str(staged), '--actor', a.actor, '--approve']
            for path in a.keep_local:
                command += ['--keep-local', path]
            for path in a.take_upstream:
                command += ['--take-upstream', path]
            changed = subprocess.run(command, cwd=temporary, capture_output=True, text=True, encoding='utf-8', check=False)
            require(changed.returncode == 0, 'Engine updated but study assets paused. ' + changed.stderr + '\nRetry asset check/apply after resolving the issue; no destructive automatic rollback.')
            receipt = {'at': now(), 'actor': a.actor, 'from_commit': old, 'to_commit': target, 'backup_ref': backup_ref,
                       'asset_update': json.loads(changed.stdout), 'engine_install': 'editable-dedicated-venv'}
            atomic_write(study / '.rw/last-engine-update.json', pretty(receipt))
            print(pretty(receipt), end='')
            return 0
    except (WorkspaceError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(pretty({'error': str(exc), 'recovery': 'No hard reset used. See docs/UPDATING.md. Asset backups live in the study .rw/backups directory.'}), file=sys.stderr, end='')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
