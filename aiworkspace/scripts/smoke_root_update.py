#!/usr/bin/env python3
"""Exercise the public updater using disposable Git repositories and real installations.

The tests use synthetic local files, no user study, remote service, model, or credentials.
Both the current layout and migration from ai-research-workspace/ are exercised.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def run(args, cwd: Path, expected: int = 0) -> str:
    process = subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True,
                             text=True, encoding='utf-8', errors='replace', timeout=180)
    if process.returncode != expected:
        raise RuntimeError(f'Expected {expected}, got {process.returncode}: {args}\n{process.stdout}\n{process.stderr}')
    return process.stdout


def copy_build_tools(py: Path, base: Path) -> None:
    purelib = Path(run([py, '-c', "import sysconfig; print(sysconfig.get_path('purelib'))"], base).strip())
    for name in ('setuptools', 'wheel'):
        try:
            distribution = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError:
            # Recent setuptools may vendor wheel instead of installing it globally.
            import setuptools
            vendor = Path(setuptools.__file__).parent / '_vendor'
            distribution = next((d for d in importlib.metadata.distributions(path=[str(vendor)])
                                 if d.metadata['Name'].lower() == name), None)
            if distribution is None:
                raise RuntimeError('Install the test build tools: python -m pip install setuptools wheel')
        for entry in distribution.files or []:
            if '..' in Path(str(entry)).parts:
                continue
            source = Path(distribution.locate_file(entry))
            if source.is_file():
                target = purelib / str(entry)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)


def scenario(package: Path, root_script: Path, legacy: bool) -> dict:
    with tempfile.TemporaryDirectory(prefix='aiworkspace-public-update-') as temp:
        base = Path(temp)
        remote, client, study, env = (base / x for x in ('upstream', 'client', 'used-study', 'venv'))
        def git(cwd, *args):
            return run(['git', '-C', cwd, *args], base).strip()
        remote.mkdir()
        git(remote, 'init', '-b', 'main')
        for key, value in [('user.name', 'Workspace Test'), ('user.email', 'fixture@example.invalid'), ('commit.gpgsign', 'false')]:
            git(remote, 'config', key, value)
        initial = 'ai-research-workspace' if legacy else 'aiworkspace'
        shutil.copytree(package, remote / initial, ignore=shutil.ignore_patterns(
            '.git', '.venv', '__pycache__', '*.egg-info', 'build', 'dist'))
        shutil.copy2(root_script, remote / 'update_aiworkspace.py')
        git(remote, 'add', '.')
        git(remote, 'commit', '-m', 'Initial synthetic release')
        run(['git', 'clone', remote, client], base)
        run([sys.executable, '-m', 'venv', env], base)
        py = env / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        copy_build_tools(py, base)
        run([py, '-m', 'pip', 'install', '--no-deps', '--no-build-isolation', '-e', client / initial], base)
        run([py, '-m', 'research_workspace', 'init', study, '--name', 'Used synthetic study', '--author', 'Fixture author'], base)
        filled = study / 'workspace/research/idea-evaluation.md'
        filled.write_text(filled.read_text(encoding='utf-8') + '\nMy existing research content.\n', encoding='utf-8')
        researcher = study / 'workspace/skills/researcher/SKILL.md'
        writer = study / 'workspace/skills/writing-language/SKILL.md'
        original_researcher = researcher.read_text(encoding='utf-8')
        original_writer = writer.read_text(encoding='utf-8')
        assert '# researcher' in original_researcher and '# writing-language' in original_writer
        researcher.write_text(original_researcher.replace('# researcher', '# Local researcher'), encoding='utf-8')
        local_writer = original_writer.replace('# writing-language', '# Local writer')
        writer.write_text(local_writer, encoding='utf-8')
        protected = [study / p for p in ('workspace/state.json', 'manuscript/main.md',
                      'workspace/research/idea-evaluation.md', 'workspace/rules/project-policy.md')]
        def hashes():
            return {p.relative_to(study).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
        before = hashes()
        old_head = git(client, 'rev-parse', 'HEAD')
        if legacy:
            (remote / initial).rename(remote / 'aiworkspace')
        upstream = remote / 'aiworkspace'
        rpath = upstream / 'research_workspace/assets/skills/researcher/SKILL.md'
        rpath.write_text(rpath.read_text(encoding='utf-8') + '\nUpstream nonoverlapping clarification.\n', encoding='utf-8')
        wpath = upstream / 'research_workspace/assets/skills/writing-language/SKILL.md'
        wpath.write_text(original_writer.replace('# writing-language', '# Upstream writer'), encoding='utf-8')
        # New release ignores generated remnants after a package-directory rename.
        shutil.copy2(root_script.parent / '.gitignore', remote / '.gitignore')
        git(remote, 'add', '.')
        git(remote, 'commit', '-m', 'Synthetic asset update and optional layout migration')
        command = [py, client / 'update_aiworkspace.py', '--project', study]
        conflict = json.loads(run(command + ['--check'], base, expected=1))
        assert 'workspace/skills/writing-language/SKILL.md' in conflict['conflicts']
        assert hashes() == before and git(client, 'rev-parse', 'HEAD') == old_head
        resolve = ['--keep-local', 'workspace/skills/writing-language/SKILL.md']
        check = json.loads(run(command + ['--dry-run'] + resolve, base))
        assert not check['blocked'] and check['project_untouched']
        assert check['current_commit'] != check['target_commit']
        assert check['target_package'] == 'aiworkspace'
        run(command + ['--apply', '--actor', 'Fixture author', '--expected-commit', '0' * 40] + resolve, base, expected=2)
        assert git(client, 'rev-parse', 'HEAD') == old_head and hashes() == before
        dirty = client / 'uncommitted-local-note.txt'
        dirty.write_text('Preserve this local engine edit.', encoding='utf-8')
        blocked = json.loads(run(command + ['--check'] + resolve, base, expected=1))
        assert blocked['dirty_checkout']
        run(command + ['--apply', '--actor', 'Fixture author'] + resolve, base, expected=2)
        assert dirty.read_text(encoding='utf-8') == 'Preserve this local engine edit.'
        dirty.unlink()  # Delete only the test-created disposable fixture file.
        receipt = json.loads(run(command + ['--apply', '--actor', 'Fixture author',
                                             '--expected-commit', check['target_commit']] + resolve, base))
        assert git(client, 'rev-parse', 'HEAD') == receipt['to_commit']
        assert hashes() == before
        text = researcher.read_text(encoding='utf-8')
        assert 'Local researcher' in text and 'Upstream nonoverlapping clarification' in text
        assert writer.read_text(encoding='utf-8') == local_writer
        run([py, '-m', 'research_workspace', 'doctor'], base)
        if legacy:
            legacy_note = client / initial / 'real-user-note.md'
            legacy_note.parent.mkdir(parents=True, exist_ok=True)
            legacy_note.write_text('A real local edit must stay visible.', encoding='utf-8')
            run(command + ['--check'], base, expected=1)
            assert legacy_note.read_text(encoding='utf-8') == 'A real local edit must stay visible.'
            legacy_note.unlink()  # Remove only the deliberate disposable test fixture.
        again = json.loads(run(command + ['--check'], base))
        assert not again['project_asset_changes'] and not again['conflicts']
        backup = receipt['asset_update']['backup_id']
        rollback = [py, '-m', 'research_workspace', '--project', study, 'upgrade', 'rollback', backup]
        researcher.write_text(text + '\nNew local work after upgrade.\n', encoding='utf-8')
        run(rollback, base, expected=2)
        assert 'New local work after upgrade.' in researcher.read_text(encoding='utf-8')
        researcher.write_text(text, encoding='utf-8')  # Restore only this fixture's deliberate probe.
        run(rollback, base)
        assert hashes() == before and 'Local researcher' in researcher.read_text(encoding='utf-8')
        assert 'Upstream nonoverlapping clarification' not in researcher.read_text(encoding='utf-8')
        assert writer.read_text(encoding='utf-8') == local_writer
        release = upstream / 'research_workspace/assets/release.json'
        config = json.loads(release.read_text(encoding='utf-8'))
        config['schema_version'] = 999999
        release.write_text(json.dumps(config), encoding='utf-8')
        git(remote, 'add', '.')
        git(remote, 'commit', '-m', 'Unsupported synthetic schema')
        run(command + ['--check'], base, expected=2)
        assert hashes() == before
        return {'layout': initial, 'passed': True, 'actual_fetch_and_editable_install': True,
                'nonoverlapping_merge': True, 'explicit_conflict_resolution': True,
                'dirty_checkout_protected': True, 'preview_commit_locked': True,
                'post_update_edits_protected_on_rollback': True, 'unsupported_schema_blocked': True,
                'research_hashes_unchanged': True, 'protected_files': list(before)}


def main() -> int:
    package = Path(__file__).resolve().parents[1]
    root_script = package.parent / 'update_aiworkspace.py'
    if not root_script.is_file():
        raise RuntimeError('Run this integration test from the complete repository checkout.')
    results = [scenario(package, root_script, legacy=False), scenario(package, root_script, legacy=True)]
    print(json.dumps({'status': 'passed', 'scenarios': results, 'scope': 'Synthetic local Git integration; no live model or scientific validation.'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
