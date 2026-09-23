#!/usr/bin/env python3
"""Preview/apply GitHub framework updates while preserving an existing research study.

Run from a Git clone. Python 3.11+, Git, and a dedicated virtual environment are
required for --apply. --check never executes code from the fetched commit.
Research projects must be outside the framework checkout. No reset, clean, stash,
force push, or automatic conflict resolution is performed.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent
PACKAGE_NAMES = ('aiworkspace', 'ai-research-workspace')


class UpdateError(RuntimeError):
    """An update was blocked without discarding local work."""


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise UpdateError(message)


def git(root: Path, *args: str, binary: bool = False, check: bool = True):
    hooks = 'core.hooksPath=NUL' if sys.platform == 'win32' else 'core.hooksPath=/dev/null'
    result = subprocess.run(
        ['git', '-c', hooks, '-C', str(root), *args],
        capture_output=True, timeout=180, check=False,
    )
    if not check:
        return result.returncode == 0
    ensure(result.returncode == 0, 'Git failed: ' + result.stderr.decode('utf-8', 'replace')[-3000:])
    return result.stdout if binary else result.stdout.decode('utf-8').strip()


def local_package(root: Path) -> Path:
    for name in PACKAGE_NAMES:
        path = root / name
        if (path / 'research_workspace/upgrade.py').is_file():
            ensure(not path.is_symlink(), 'Framework package may not be a symlink.')
            return path
    raise UpdateError('Framework missing. Keep this script beside the aiworkspace/ folder in a Git clone.')


def target_package(root: Path, commit: str) -> str:
    for name in PACKAGE_NAMES:
        if git(root, 'cat-file', '-e', f'{commit}:{name}/research_workspace/assets/release.json', check=False):
            return name
    raise UpdateError('The selected commit has no supported workspace package. Check --ref.')


def stage_commit(root: Path, commit: str, relative: str, destination: Path) -> Path:
    ensure(relative in PACKAGE_NAMES, 'Unsupported package path.')
    archive = git(root, 'archive', '--format=zip', commit, '--', relative, binary=True)
    ensure(len(archive) <= 64 * 1024 * 1024, 'Framework archive exceeds 64 MiB.')
    with zipfile.ZipFile(BytesIO(archive)) as bundle:
        items = bundle.infolist()
        ensure(len(items) <= 4000 and sum(x.file_size for x in items) <= 128 * 1024 * 1024,
               'Framework archive exceeds extraction limits.')
        seen = set()
        for info in items:
            path = PurePosixPath(info.filename)
            ensure(not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename
                   and ':' not in info.filename and path.parts and path.parts[0] == relative,
                   'Unsafe archive path.')
            ensure(info.filename not in seen, 'Duplicate archive member.')
            seen.add(info.filename)
            ensure((info.external_attr >> 16) & 0o170000 != 0o120000, 'Release symlinks are rejected.')
            target = destination.joinpath(*path.parts)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(bundle.read(info))
    return destination / relative


def arguments(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', required=True, help='Existing study outside this Git checkout')
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', '--dry-run', action='store_true', help='Read-only study/engine preview; fetch is allowed')
    mode.add_argument('--apply', action='store_true', help='Trust and install the selected upstream code after preview')
    p.add_argument('--actor', help='Person approving --apply')
    p.add_argument('--remote', default='origin')
    p.add_argument('--ref', default='origin/main', help='Fetched ref or exact reviewed commit SHA')
    p.add_argument('--expected-commit', help='Abort if --ref no longer resolves to this previewed SHA')
    p.add_argument('--offline', action='store_true', help='Use already fetched Git objects')
    p.add_argument('--keep-local', action='append', default=[], metavar='MANAGED_PATH')
    p.add_argument('--take-upstream', action='append', default=[], metavar='MANAGED_PATH')
    return p.parse_args(argv)


def update(a) -> dict:
    for value in (a.remote, a.ref):
        ensure(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9/._-]*', value) is not None, 'Invalid remote/ref.')
    if a.expected_commit:
        ensure(re.fullmatch(r'[a-f0-9]{40,64}', a.expected_commit) is not None, 'Expected commit must be a full SHA.')
    root = Path(git(ROOT, 'rev-parse', '--show-toplevel')).resolve()
    ensure(root == ROOT, 'Place update_aiworkspace.py at the Git checkout root.')
    current_package = local_package(root)
    study = Path(a.project).expanduser().resolve()
    ensure(study.is_dir() and not study.is_relative_to(root), 'Use an existing study outside the framework checkout.')
    sys.path.insert(0, str(current_package))
    # Import only the current trusted engine. The fetched release is data during preview.
    from research_workspace.model import now, pretty
    from research_workspace.store import atomic_write, safe_path
    from research_workspace.upgrade import plan_upgrade

    old = git(root, 'rev-parse', 'HEAD')
    if not a.offline:
        git(root, 'fetch', '--no-tags', a.remote)
    target = git(root, 'rev-parse', '--verify', a.ref + '^{commit}')
    ensure(re.fullmatch(r'[a-f0-9]{40,64}', target) is not None, 'Invalid target commit.')
    ensure(not a.expected_commit or target == a.expected_commit,
           'Upstream changed since preview. Run --check again; no engine/study files were modified.')
    dirty = bool(git(root, 'status', '--porcelain'))
    fast_forward = git(root, 'merge-base', '--is-ancestor', old, target, check=False)
    relative = target_package(root, target)
    with tempfile.TemporaryDirectory(prefix='aiworkspace-update-') as temporary:
        staged = stage_commit(root, target, relative, Path(temporary))
        plan = plan_upgrade(study, staged, a.keep_local, a.take_upstream)
        report = {
            'current_commit': old, 'target_commit': target, 'target_package': relative,
            'dirty_checkout': dirty, 'fast_forward': fast_forward,
            'repository_diff': git(root, 'diff', '--stat', old, target),
            'project_asset_changes': [e for e in plan['entries'] if e['path'] in plan['changes']],
            'preserved_local_customizations': [e['path'] for e in plan['entries'] if e['action'] in ('local-only', 'keep-local', 'merged')],
            'conflicts': plan['conflicts'], 'project_untouched': True,
            'blocked': dirty or not fast_forward or bool(plan['conflicts']),
            'note': 'Preview reads fetched data only. Apply trusts fetched code. Asset backups do not replace research backups.',
        }
        if a.check:
            return report
        ensure(a.actor and a.actor.strip(), 'Supply --actor with the person approving this update.')
        ensure(sys.prefix != sys.base_prefix, 'Use a dedicated virtual environment for --apply.')
        ensure(not report['blocked'], 'Update blocked. Preserve engine edits or resolve listed asset conflicts, then preview again.')
        ensure(git(root, 'rev-parse', 'HEAD') == old and not git(root, 'status', '--porcelain'),
               'Checkout changed during preview. Retry without discarding local edits.')
        # Core asset writes recheck state, baseline and local hashes under a study lock.
        backup_ref = 'refs/rw-backups/' + old[:12]
        git(root, 'update-ref', backup_ref, old)
        git(root, 'merge', '--ff-only', target)
        installed_package = root / relative
        install = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--no-deps', '--no-build-isolation', '-e', str(installed_package)],
            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180,
        )
        ensure(install.returncode == 0,
               'Engine checkout updated but installation failed; study assets are untouched. '
               f'Old code ref: {backup_ref}. Details: ' + install.stderr[-3000:])
        cmd = [sys.executable, '-m', 'research_workspace', '--project', str(study), 'upgrade', 'apply',
               '--source', str(staged), '--actor', a.actor, '--approve']
        for key, values in (('--keep-local', a.keep_local), ('--take-upstream', a.take_upstream)):
            for path in values:
                cmd.extend([key, path])
        result = subprocess.run(cmd, cwd=temporary, capture_output=True, text=True,
                                encoding='utf-8', errors='replace', timeout=180)
        ensure(result.returncode == 0,
               'Engine updated; study asset update paused. Preserve local work and use upgrade check/recover. ' + result.stderr[-3000:])
        receipt = {'at': now(), 'actor': a.actor, 'from_commit': old, 'to_commit': target,
                   'backup_ref': backup_ref, 'package': relative, 'asset_update': json.loads(result.stdout),
                   'engine_install': 'editable-dedicated-venv', 'preview': report}
        atomic_write(safe_path(study, '.rw/last-engine-update.json', governed=False), pretty(receipt))
        return receipt


def main(argv=None) -> int:
    a = arguments(argv)
    try:
        result = update(a)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result.get('blocked') else 0
    except Exception as exc:
        # Report deterministic failures without pretending an engine rollback occurred.
        # KeyboardInterrupt and SystemExit intentionally retain their normal behavior.
        print(json.dumps({'error': str(exc), 'type': type(exc).__name__,
                          'recovery': 'See aiworkspace/docs/UPDATING.md. No reset/clean/stash was used. '
                                      'Study asset backups are in .rw/backups; engine recovery is separate.'},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
