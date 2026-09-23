import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from research_workspace.model import WorkspaceError, pretty
from research_workspace.scaffold import initialize
from research_workspace.skills import install_skills
from research_workspace.store import Store, atomic_write, file_hash
from research_workspace.upgrade import ASSETS, apply_upgrade, merge_text, plan_upgrade, recover_upgrade, rollback


class UpgradeCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name); self.root = base / 'used-study'; self.source = base / 'next-framework'
        initialize(self.root, 'Used study', 'Author')
        shutil.copytree(ASSETS, self.source / 'research_workspace/assets')
        self.assets = self.source / 'research_workspace/assets'
        config = json.loads((self.assets / 'release.json').read_text()); config['version'] = '0.2.0-fixture'
        atomic_write(self.assets / 'release.json', pretty(config))
        self.path = 'workspace/skills/researcher/SKILL.md'; self.remote = self.assets / 'skills/researcher/SKILL.md'

    def update(self, **kwargs): return apply_upgrade(self.root, self.source, 'Author', approve=True, **kwargs)
    def hashes(self): return {p.relative_to(self.root).as_posix(): file_hash(p) for p in self.root.rglob('*') if p.is_file()}

    def conflict(self):
        target = self.root / self.path
        atomic_write(target, target.read_text().replace('name: researcher', 'name: local-researcher'))
        atomic_write(self.remote, self.remote.read_text().replace('name: researcher', 'name: upstream-researcher'))

    def test_preserve_all_used_research(self):
        paths = ['workspace/research/idea-evaluation.md', 'workspace/rules/project-policy.md', 'manuscript/main.md', 'workspace/memory.md', 'workspace/data/new.csv']
        for path in paths: atomic_write(self.root / path, 'Used research must survive: ' + path + '\n')
        before = {p: file_hash(self.root / p) for p in paths + ['workspace/state.json']}
        atomic_write(self.remote, self.remote.read_text() + '\nUpstream addition.\n')
        result = self.update()
        self.assertEqual(result['changed_files'], [self.path])
        self.assertEqual(before, {p: file_hash(self.root / p) for p in before})

    def test_update_is_idempotent(self):
        self.update(); self.assertFalse(self.update()['updated'])

    def test_check_does_not_write(self):
        before = self.hashes(); plan_upgrade(self.root, self.source); self.assertEqual(before, self.hashes())

    def test_local_only_edit_preserved(self):
        target = self.root / self.path; atomic_write(target, target.read_text() + '\nMy local rule.\n')
        self.update(); self.assertIn('My local rule.', target.read_text())

    def test_nonoverlapping_merge(self):
        target = self.root / self.path; atomic_write(target, target.read_text().replace('# researcher', '# My local Researcher'))
        atomic_write(self.remote, self.remote.read_text() + '\nUpstream closing note.\n')
        self.update(); self.assertIn('# My local Researcher', target.read_text()); self.assertIn('Upstream closing note.', target.read_text())

    def test_three_way_merge_and_conflict(self):
        base = 'A\nB\nC\nD\nE\n'
        self.assertEqual(merge_text(base, 'Local\nB\nC\nD\nE\n', 'A\nB\nC\nD\nRemote\n'), ('merged', 'Local\nB\nC\nD\nRemote\n'))
        self.assertEqual(merge_text(base, 'Local\nB\nC\nD\nE\n', 'Remote\nB\nC\nD\nE\n')[0], 'conflict')

    def test_conflict_stops_all_writes(self):
        self.conflict(); policy = self.assets / 'PROJECT_POLICY.md'; atomic_write(policy, policy.read_text() + '\nUpstream policy change.\n')
        before = self.hashes()
        with self.assertRaises(WorkspaceError): self.update()
        self.assertEqual(before, self.hashes()); self.assertEqual(plan_upgrade(self.root, self.source)['conflicts'], [self.path])

    def test_explicit_keep_local(self):
        self.conflict(); self.update(keep_local=[self.path])
        self.assertIn('name: local-researcher', (self.root / self.path).read_text())
        self.assertFalse(plan_upgrade(self.root, self.source)['conflicts'])

    def test_take_upstream_then_restore_local(self):
        self.conflict(); before = (self.root / self.path).read_text()
        result = self.update(take_upstream=[self.path])
        self.assertIn('name: upstream-researcher', (self.root / self.path).read_text())
        rollback(self.root, result['backup_id']); self.assertEqual((self.root / self.path).read_text(), before)

    def test_rollback_preserves_new_post_update_edits(self):
        atomic_write(self.remote, self.remote.read_text() + '\nUpstream\n')
        result = self.update(); target = self.root / self.path
        atomic_write(target, target.read_text() + '\nNew user edit after update\n')
        with self.assertRaises(WorkspaceError): rollback(self.root, result['backup_id'])
        self.assertIn('New user edit', target.read_text())

    def test_add_and_remove_managed_template(self):
        config = json.loads((self.assets / 'release.json').read_text())
        config['files']['workspace/templates/new-template.md'] = 'templates/new-template.md'
        removed = 'workspace/templates/idea_evluation.md'; config['files'].pop(removed)
        atomic_write(self.assets / 'templates/new-template.md', 'New template\n'); atomic_write(self.assets / 'release.json', pretty(config))
        result = self.update()
        self.assertTrue((self.root / 'workspace/templates/new-template.md').exists()); self.assertFalse((self.root / removed).exists())
        rollback(self.root, result['backup_id'])
        self.assertFalse((self.root / 'workspace/templates/new-template.md').exists()); self.assertTrue((self.root / removed).exists())

    def test_upstream_cannot_target_manuscript(self):
        config = json.loads((self.assets / 'release.json').read_text()); config['files']['manuscript/main.md'] = 'AGENTS.md'
        atomic_write(self.assets / 'release.json', pretty(config))
        before = self.hashes()
        with self.assertRaises(WorkspaceError): self.update()
        self.assertEqual(before, self.hashes())

    def test_unknown_schema_refused(self):
        config = json.loads((self.assets / 'release.json').read_text()); config['schema_version'] = 999
        atomic_write(self.assets / 'release.json', pretty(config))
        with self.assertRaises(WorkspaceError): self.update()

    def test_missing_baseline_refused(self):
        (self.root / '.rw/framework.json').unlink()
        with self.assertRaises(WorkspaceError): self.update()

    def test_installed_host_skills_update(self):
        install_skills(Store(self.root), '.agents/skills')
        atomic_write(self.remote, self.remote.read_text() + '\nHost upgrade too\n')
        self.update(); self.assertIn('Host upgrade too', (self.root / '.agents/skills/researcher/SKILL.md').read_text())

    def test_upgrade_interruption_recovery(self):
        import research_workspace.upgrade as module
        atomic_write(self.remote, self.remote.read_text() + '\nUpstream\n')
        original = (self.root / self.path).read_text(); write = module._write; calls = 0
        def crash(root, path, text):
            nonlocal calls
            calls += 1
            if calls == 2: raise OSError('Simulated interrupted update')
            return write(root, path, text)
        with patch.object(module, '_write', side_effect=crash):
            with self.assertRaises(OSError): self.update()
        with self.assertRaises(WorkspaceError): Store(self.root)
        recover_upgrade(self.root)
        self.assertEqual((self.root / self.path).read_text(), original)
        self.assertFalse((self.root / '.rw/update-transaction.json').exists()); Store(self.root)

    def test_rollback_interruption_recovery(self):
        import research_workspace.upgrade as module
        atomic_write(self.remote, self.remote.read_text() + '\nUpstream\n')
        original = (self.root / self.path).read_text(); result = self.update(); write = module._write; calls = 0
        def crash(root, path, text):
            nonlocal calls
            calls += 1
            if calls == 2: raise OSError('Simulated interrupted rollback')
            return write(root, path, text)
        with patch.object(module, '_write', side_effect=crash):
            with self.assertRaises(OSError): rollback(self.root, result['backup_id'])
        with self.assertRaises(WorkspaceError): Store(self.root)
        recover_upgrade(self.root)
        self.assertEqual((self.root / self.path).read_text(), original); Store(self.root)

    def test_lock_not_cleared_automatically(self):
        atomic_write(self.root / '.rw/write.lock', '12345')
        with self.assertRaises(WorkspaceError): self.update()
        self.assertTrue((self.root / '.rw/write.lock').exists())

    def test_opposite_resolutions_rejected(self):
        with self.assertRaises(WorkspaceError): self.update(keep_local=[self.path], take_upstream=[self.path])

    def test_explicit_approval_required(self):
        with self.assertRaises(WorkspaceError): apply_upgrade(self.root, self.source, 'Author')


class GitPreflightCase(unittest.TestCase):
    def test_actual_local_git_fetch_check_and_dirty_guard(self):
        package = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); remote = root / 'remote'; local = root / 'local'; study = root / 'study'
            def git(cwd, *args): subprocess.run(['git', '-C', str(cwd), *args], check=True, capture_output=True)
            remote.mkdir(); git(remote, 'init', '-b', 'main')
            for key, value in (('user.name', 'Fixture'), ('user.email', 'fixture@example.invalid'), ('commit.gpgsign', 'false')): git(remote, 'config', key, value)
            shutil.copytree(package, remote / 'ai-research-workspace', ignore=shutil.ignore_patterns('__pycache__', '*.egg-info', '.git', '.venv', 'build', 'dist'))
            git(remote, 'add', '.'); git(remote, 'commit', '-m', 'Fixture initial')
            subprocess.run(['git', 'clone', str(remote), str(local)], check=True, capture_output=True)
            path = remote / 'ai-research-workspace/research_workspace/assets/AGENTS.md'
            atomic_write(path, path.read_text() + '\nNew upstream fixture rule\n')
            git(remote, 'add', '.'); git(remote, 'commit', '-m', 'Fixture update')
            initialize(study, 'Used', 'Author'); before = file_hash(study / 'manuscript/main.md')
            command = [sys.executable, str(local / 'ai-research-workspace/scripts/update.py'), '--project', str(study), '--check']
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertNotEqual(report['current_commit'], report['target_commit']); self.assertTrue(report['project_untouched'])
            self.assertEqual(before, file_hash(study / 'manuscript/main.md'))
            self.assertNotIn('New upstream fixture rule', (local / 'ai-research-workspace/research_workspace/assets/AGENTS.md').read_text())
            atomic_write(local / 'ai-research-workspace/research_workspace/assets/AGENTS.md', 'Local uncommitted change')
            result = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1); self.assertTrue(json.loads(result.stdout)['dirty_checkout'])


if __name__ == '__main__': unittest.main()
