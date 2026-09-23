#!/usr/bin/env python3
"""Actual Git/pip/update integration in disposable local repositories and a fresh venv.

Requires setuptools in the development interpreter. Uses no user remote, private study,
model API or credentials. The version 0.1.1+fixture is a synthetic test release only.
"""
from __future__ import annotations
import hashlib
import importlib.metadata
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    package = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix='rw-install-test-') as directory:
        base = Path(directory)
        remote, client, study, venv = (base / name for name in ('upstream', 'client', 'used-study', 'venv'))
        def call(args, cwd=base):
            process = subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True, text=True, encoding='utf-8')
            if process.returncode:
                raise RuntimeError('Failed: ' + ' '.join(map(str, args)) + '\n' + process.stdout + process.stderr)
            return process.stdout
        def git(cwd, *args): return call(['git', '-C', cwd, *args])
        remote.mkdir(); git(remote, 'init', '-b', 'main')
        for key, value in (('user.name', 'Synthetic Integration Test'), ('user.email', 'fixture@example.invalid'), ('commit.gpgsign', 'false')):
            git(remote, 'config', key, value)
        shutil.copytree(package, remote / 'ai-research-workspace', ignore=shutil.ignore_patterns('__pycache__', '*.egg-info', '.git', '.venv', 'build', 'dist'))
        git(remote, 'add', '.'); git(remote, 'commit', '-m', 'Initial fixture release')
        call(['git', 'clone', remote, client])
        call([sys.executable, '-m', 'venv', venv])
        py = venv / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        # A nested venv cannot inherit an outer venv's build tools reliably. Copy only
        # installed build-tool distributions into this disposable environment.
        purelib = Path(call([py, '-c', "import sysconfig; print(sysconfig.get_path('purelib'))"]).strip())
        for name in ('setuptools', 'wheel'):
            try:
                distribution = importlib.metadata.distribution(name)
            except importlib.metadata.PackageNotFoundError:
                if name == 'setuptools': raise RuntimeError('Install setuptools in the development environment first.')
                continue
            for entry in distribution.files or []:
                if '..' in Path(str(entry)).parts: continue
                source = Path(distribution.locate_file(entry))
                if source.is_file():
                    target = purelib / str(entry); target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
        local = client / 'ai-research-workspace'
        call([py, '-m', 'pip', 'install', '--no-deps', '--no-build-isolation', '-e', local])
        call([py, '-m', 'research_workspace', 'init', study, '--name', 'Previously used study', '--author', 'Fixture Author'])
        filled = study / 'workspace/research/idea-evaluation.md'
        filled.write_text(filled.read_text(encoding='utf-8') + '\nAlready-filled personal research idea.\n', encoding='utf-8')
        custom = study / 'workspace/skills/researcher/SKILL.md'
        custom.write_text(custom.read_text(encoding='utf-8').replace('# researcher', '# Local researcher customization'), encoding='utf-8')
        protected = [study / 'workspace/state.json', study / 'manuscript/main.md', filled, study / 'workspace/rules/project-policy.md']
        def hashes(): return {p.relative_to(study).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
        before = hashes()
        upstream = remote / 'ai-research-workspace'
        for path in ('pyproject.toml', 'research_workspace/__init__.py', 'research_workspace/assets/release.json'):
            target = upstream / path
            target.write_text(target.read_text(encoding='utf-8').replace('0.1.0', '0.1.1+fixture'), encoding='utf-8')
        skill = upstream / 'research_workspace/assets/skills/researcher/SKILL.md'
        skill.write_text(skill.read_text(encoding='utf-8') + '\nUpstream fixture clarification.\n', encoding='utf-8')
        git(remote, 'add', '.'); git(remote, 'commit', '-m', 'New fixture release')
        command = [py, local / 'scripts/update.py', '--project', study, '--ref', 'origin/main']
        check = json.loads(call(command + ['--check']))
        assert check['current_commit'] != check['target_commit']
        assert not check['conflicts'] and check['project_untouched'] and hashes() == before
        call(command + ['--apply', '--actor', 'Fixture Author'])
        receipt = json.loads((study / '.rw/last-engine-update.json').read_text(encoding='utf-8'))
        assert receipt['from_commit'] != receipt['to_commit']
        assert git(client, 'rev-parse', 'HEAD').strip() == receipt['to_commit']
        assert call([py, '-m', 'research_workspace', '--version']).strip() == '0.1.1+fixture'
        assert hashes() == before
        assert 'Local researcher customization' in custom.read_text(encoding='utf-8')
        assert 'Upstream fixture clarification' in custom.read_text(encoding='utf-8')
        repeated = json.loads(call(command + ['--check']))
        assert not repeated['project_asset_changes'] and not repeated['conflicts']
        call([py, '-m', 'research_workspace', '--project', study, 'upgrade', 'rollback', receipt['asset_update']['backup_id']])
        assert hashes() == before
        assert 'Local researcher customization' in custom.read_text(encoding='utf-8')
        assert 'Upstream fixture clarification' not in custom.read_text(encoding='utf-8')
        print(json.dumps({'status': 'passed', 'actual_git_fetch': True, 'actual_fast_forward': True,
            'actual_editable_install': True, 'installed_version': '0.1.1+fixture', 'nonoverlapping_local_skill_preserved': True,
            'research_hashes_unchanged': True, 'repeat_check_idempotent': True, 'asset_rollback_passed': True,
            'protected_files': list(before), 'source': 'Temporary local Git repositories; not a new published release or live model test.'}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
