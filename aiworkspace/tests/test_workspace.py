import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from research_workspace import adapters, review, skills, sync, workflow
from research_workspace.analysis import run_method
from research_workspace.demo import demonstrate, AUTHOR, NOTE
from research_workspace.model import WorkspaceError, digest, impact, make_node, pretty
from research_workspace.scaffold import initialize
from research_workspace.store import Store, atomic_write, file_hash, safe_path, recover


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'study'
        initialize(self.root, 'Test', 'Author')

    def s(self): return Store(self.root)

    def add(self, nodes):
        proposal = workflow.propose(self.s(), [{'op': 'upsert', 'node': n} for n in nodes], 'test:writer', 'Fixture change')
        return workflow.apply(self.s(), proposal['id'], 'Author', NOTE, approve=True)

    def evidence_fixture(self):
        atomic_write(self.root / 'workspace/sources/snapshots/source.txt', 'A bounded observation in the fixture.\n')
        source = make_node('SRC-1', 'source', 'Original fixture', {'category': 'primary', 'url': 'local:fixture', 'snapshot': 'workspace/sources/snapshots/source.txt'})
        claim = make_node('CLM-1', 'claim', 'Bounded assertion', {'text': 'A bounded observation.', 'strength': 'descriptive', 'scope': 'Fixture only'}, ['EVD-1'], 'confirmed')
        evidence = make_node('EVD-1', 'evidence', 'Original quote', {'source': 'SRC-1', 'claim': 'CLM-1', 'quote': 'A bounded observation in the fixture.', 'locator': 'line 1', 'scope': 'Fixture only', 'relation': 'supports'}, ['SRC-1'])
        self.add([source, claim, evidence])
        workflow.verify(self.s(), 'SRC-1', 'Verifier', NOTE, human=True)
        workflow.verify(self.s(), 'EVD-1', 'Verifier', NOTE, human=True)

    def test_sibling_layout_and_markdown_template(self):
        self.assertTrue((self.root / 'workspace/research/idea-evaluation.md').exists())
        self.assertTrue((self.root / 'workspace/templates/idea-evaluation.original.md').exists())
        self.assertTrue((self.root / 'manuscript/main.md').exists())
        self.assertFalse((self.root / 'workspace/manuscript').exists())
        self.assertFalse(list(self.root.rglob('*.ppt*')))

    def test_refuse_nonempty_init(self):
        with self.assertRaises(WorkspaceError): initialize(self.root, 'Again', 'Author')

    def test_empty_project_blocked(self):
        self.assertEqual(review.review(self.s())['machine_status'], 'blocked')
        self.assertFalse(review.gate(self.s())['ready_for_packaging'])

    def test_no_accidental_network(self):
        with self.assertRaises(WorkspaceError): adapters.search_crossref(self.s(), 'query', 10, 'test')
        with self.assertRaises(WorkspaceError): adapters.run_agent(self.s(), 'researcher', 'task', model='explicit', endpoint='https://example.org/v1/chat/completions')

    def test_unsafe_paths(self):
        for value in ('../escape', '/tmp/escape', 'workspace/../../escape', 'workspace/.git/config', 'workspace/x\\y', 'workspace/C:secret', 'other/file'):
            with self.subTest(value=value), self.assertRaises(WorkspaceError): safe_path(self.root, value)

    def test_symlink_rejected(self):
        (self.root / 'workspace/sources/link').symlink_to(Path(self.tmp.name))
        with self.assertRaises(WorkspaceError): safe_path(self.root, 'workspace/sources/link/secret')
        with self.assertRaises(WorkspaceError): self.s().fingerprint()

    def test_cycle_safe_impact(self):
        a = make_node('ARG-A', 'argument', 'A', {}, ['ARG-B'])
        b = make_node('ARG-B', 'argument', 'B', {}, ['ARG-A'])
        self.assertEqual(impact({'ARG-A': a, 'ARG-B': b}, ['ARG-A'])['affected'], ['ARG-A', 'ARG-B'])
        with self.assertRaises(WorkspaceError): impact({}, ['SRC-X'])

    def test_stale_proposal_after_external_edit(self):
        node = copy.deepcopy(self.s().node('RQ-001')); node['title'] = 'Changed'
        proposal = workflow.propose(self.s(), [{'op': 'upsert', 'node': node}], 'writer', 'Change')
        atomic_write(self.root / 'manuscript/main.md', (self.root / 'manuscript/main.md').read_text() + '\nUser edit\n')
        with self.assertRaises(WorkspaceError): workflow.apply(self.s(), proposal['id'], 'Author', NOTE, approve=True)

    def test_explicit_proposal_approval_required(self):
        node = copy.deepcopy(self.s().node('RQ-001')); node['title'] = 'Changed'
        proposal = workflow.propose(self.s(), [{'op': 'upsert', 'node': node}], 'writer', 'Change')
        with self.assertRaises(WorkspaceError): workflow.apply(self.s(), proposal['id'], 'Author', NOTE)
        self.assertEqual(self.s().state['proposals'][proposal['id']]['status'], 'pending')

    def test_optimistic_concurrency(self):
        a, b = self.s(), self.s()
        a.event('test', 'A'); a.commit()
        b.event('test', 'B')
        with self.assertRaises(WorkspaceError): b.commit()

    def test_cannot_mint_verification_or_executable(self):
        node = make_node('SRC-X', 'source', 'Source', {'category': 'primary', 'url': 'local:x'})
        node['verification'] = {'actor': 'fake'}
        with self.assertRaises(WorkspaceError): workflow.propose(self.s(), [{'op': 'upsert', 'node': node}], 'ai', 'Forgery')
        for path in ('workspace/state.json', 'workspace/methods/evil.py', 'workspace/reports/fake.md'):
            with self.subTest(path=path), self.assertRaises(WorkspaceError): workflow.propose(self.s(), [{'op': 'write', 'path': path, 'text': 'bad', 'expected_sha256': None}], 'ai', 'Write')

    def test_source_tamper_invalidates_evidence(self):
        self.evidence_fixture()
        self.assertFalse(workflow.evidence_problems(self.s(), self.s().node('EVD-1')))
        atomic_write(self.root / 'workspace/sources/snapshots/source.txt', 'Changed original')
        self.assertTrue(workflow.evidence_problems(self.s(), self.s().node('EVD-1')))

    def test_claim_strength_change_invalidates_evidence(self):
        self.evidence_fixture()
        node = copy.deepcopy(self.s().node('CLM-1')); node['data']['strength'] = 'causal'; self.add([node])
        self.assertTrue(any('Claim meaning' in p for p in workflow.evidence_problems(self.s(), self.s().node('EVD-1'))))

    def test_quote_mismatch_blocks_verification(self):
        self.evidence_fixture()
        node = copy.deepcopy(self.s().node('EVD-1')); node.pop('verification'); node['data']['quote'] = 'Invented quotation'; self.add([node])
        with self.assertRaises(WorkspaceError): workflow.verify(self.s(), 'EVD-1', 'Verifier', NOTE, human=True)

    def test_news_requires_primary_object_justification(self):
        self.evidence_fixture()
        node = copy.deepcopy(self.s().node('SRC-1')); node['data']['category'] = 'news'; node.pop('verification'); self.add([node])
        with self.assertRaises(WorkspaceError): workflow.verify(self.s(), 'SRC-1', 'Verifier', NOTE, human=True)
        workflow.verify(self.s(), 'SRC-1', 'Verifier', NOTE, human=True, primary_for='This study analyzes this newspaper text itself as original corpus material.')
        self.assertFalse(workflow.source_problems(self.s(), self.s().node('SRC-1')))

    def test_retraction_blocks_support(self):
        self.evidence_fixture()
        node = copy.deepcopy(self.s().node('SRC-1')); node['data']['retracted'] = True; node.pop('verification'); self.add([node])
        with self.assertRaises(WorkspaceError): workflow.verify(self.s(), 'SRC-1', 'Verifier', NOTE, human=True)

    def test_impact_opens_all_dependent_section_issues(self):
        node = copy.deepcopy(self.s().node('RQ-001')); node['title'] = 'New question'
        result = self.add([node])
        self.assertEqual(len(result['impact']['sections']), 6)
        self.assertEqual(len(self.s().state['issues']), 6)

    def test_workspace_to_manuscript(self):
        node = copy.deepcopy(self.s().node('SEC-ABSTRACT')); node['data']['text'] = '## Abstract\n\nBounded new draft.'; self.add([node])
        proposal = sync.propose_sync(self.s(), 'sync'); workflow.apply(self.s(), proposal['id'], 'Author', NOTE, approve=True)
        self.assertFalse(sync.plan(self.s())['changes'])
        self.assertIn('Bounded new draft.', (self.root / 'manuscript/main.md').read_text())

    def test_manuscript_to_workspace_requires_semantic_review(self):
        path = self.root / 'manuscript/main.md'; atomic_write(path, path.read_text().replace('## Abstract', '## Abstract revised'))
        proposal = sync.propose_sync(self.s(), 'sync'); workflow.apply(self.s(), proposal['id'], 'Author', NOTE, approve=True)
        self.assertIn('revised', self.s().node('SEC-ABSTRACT')['data']['text'])
        self.assertTrue(any('meaning' in i['message'] for i in self.s().state['issues'].values()))

    def test_both_sides_conflict_and_explicit_resolution(self):
        node = copy.deepcopy(self.s().node('SEC-ABSTRACT')); node['data']['text'] = 'Research-side text'; self.add([node])
        path = self.root / 'manuscript/main.md'; atomic_write(path, path.read_text().replace('## Abstract', '## External abstract'))
        self.assertTrue(sync.plan(self.s())['conflicts'])
        with self.assertRaises(WorkspaceError): sync.propose_sync(self.s(), 'sync')
        proposal = sync.propose_sync(self.s(), 'sync', {'SEC-ABSTRACT': 'manuscript'})
        workflow.apply(self.s(), proposal['id'], 'Author', NOTE, approve=True)
        self.assertFalse(sync.plan(self.s())['conflicts'])

    def test_identical_external_changes_still_need_review(self):
        store = self.s(); node = store.node('SEC-ABSTRACT'); old = node['data']['text']; new = old + '\nBoth changed externally.'
        path = self.root / 'manuscript/main.md'; atomic_write(path, path.read_text().replace(sync.block(node['id'], old), sync.block(node['id'], new)))
        node['data']['text'] = new; store.event('test.external-edit', 'Fixture'); store.commit()
        self.assertIn(node['id'], sync.plan(self.s())['semantic_review'])

    def test_unmapped_text_requires_acknowledgment(self):
        path = self.root / 'manuscript/main.md'; atomic_write(path, path.read_text() + '\nExternal note\n')
        with self.assertRaises(WorkspaceError): sync.propose_sync(self.s(), 'sync')
        proposal = sync.propose_sync(self.s(), 'sync', acknowledge_outside=True)
        workflow.apply(self.s(), proposal['id'], 'Author', NOTE, approve=True)
        self.assertTrue(self.s().state['issues'])

    def test_invalid_markers(self):
        for text in ('<!-- rw:section SEC-A -->\ntext', sync.block('SEC-A', 'x') + sync.block('SEC-A', 'y')):
            with self.assertRaises(WorkspaceError): sync.parse(text)

    def test_grouped_citations_recognized(self):
        self.assertEqual(review.citation_ids('See [@SRC-1; @SRC-2] and @SRC-3.'), {'SRC-1', 'SRC-2', 'SRC-3'})
        self.assertEqual(review.citation_ids('mail user@example.org'), set())

    def test_mock_discovery_deduplicates_without_verification(self):
        transport = lambda *_: {'message': {'items': [{'DOI': '10.0000/fixture', 'title': ['Mock'], 'type': 'journal-article'}]}}
        a = adapters.search_crossref(self.s(), 'fixture', 3, 'test', online=True, public_query=True, transport=transport)
        b = adapters.search_crossref(self.s(), 'fixture', 3, 'test', online=True, public_query=True, transport=transport)
        self.assertEqual(len(a['added']), 1); self.assertEqual(b['added'], [])
        node = self.s().node(a['added'][0]); self.assertNotIn('verification', node); self.assertEqual(node['data']['category'], 'unclassified')

    def test_writer_context_filters_unverified_and_decision_data(self):
        self.evidence_fixture(); self.add([make_node('DEC-1', 'decision', 'Preferred narrative', {'text': 'Persuasion'})])
        packet = skills.task_packet(self.s(), 'writing-language', 'Draft honestly')
        ids = {n['id'] for n in packet['untrusted_research_data']}
        self.assertIn('CLM-1', ids); self.assertNotIn('DEC-1', ids)
        atomic_write(self.root / 'workspace/sources/snapshots/source.txt', 'Changed')
        packet = skills.task_packet(self.s(), 'writing-language', 'Draft honestly')
        self.assertNotIn('CLM-1', {n['id'] for n in packet['untrusted_research_data']})

    def test_reviewer_independent_context(self):
        self.add([make_node('DEC-1', 'decision', 'Defense', {'text': 'Trust the author'})])
        packet = skills.task_packet(self.s(), 'reviewer', 'Independent review')
        self.assertFalse(any(n['kind'] == 'decision' for n in packet['untrusted_research_data']))
        self.assertNotIn('non_evidentiary_memory', packet); self.assertIn('manuscript', packet)

    def test_mock_model_creates_pending_proposal_only(self):
        adapters.configure_ai(self.s(), True, ['example.org'], 'Author', NOTE)
        node = copy.deepcopy(self.s().node('RQ-001')); node['title'] = 'Proposed only'
        response = {'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps({'summary': 'Mock proposal', 'base_fingerprint': self.s().fingerprint(), 'operations': [{'op': 'upsert', 'node': node}]})}}]}
        with patch.dict('os.environ', {'RW_API_KEY': 'mock-not-real'}):
            result = adapters.run_agent(self.s(), 'researcher', 'Test', model='mock', endpoint='https://example.org/v1/chat/completions', allow_network=True, transport=lambda *_: response)
        self.assertEqual(result['status'], 'pending'); self.assertNotEqual(self.s().node('RQ-001')['title'], 'Proposed only')

    def test_model_truncation_and_wrong_host_rejected(self):
        adapters.configure_ai(self.s(), True, ['example.org'], 'Author', NOTE)
        with patch.dict('os.environ', {'RW_API_KEY': 'mock'}):
            with self.assertRaises(WorkspaceError): adapters.run_agent(self.s(), 'researcher', 'Test', model='mock', endpoint='https://other.org/v1', allow_network=True, transport=lambda *_: {})
            with self.assertRaises(WorkspaceError): adapters.run_agent(self.s(), 'researcher', 'Test', model='mock', endpoint='https://example.org/v1', allow_network=True, transport=lambda *_: {'choices': [{'finish_reason': 'length'}]})
        self.assertFalse(self.s().state['proposals'])

    def test_fake_run_does_not_establish_execution(self):
        self.add([make_node('RUN-FAKE', 'result', 'Fake', {'exit_code': 0}, status='confirmed')])
        self.assertTrue(any(i['code'] == 'RUN_RECEIPT' for i in review.review(self.s())['issues']))

    def test_existing_output_not_accepted_as_new_run(self):
        atomic_write(self.root / 'workspace/data/input.txt', 'input')
        atomic_write(self.root / 'workspace/results/output.txt', 'old')
        atomic_write(self.root / 'workspace/methods/noop.py', 'print("no output")\n')
        self.add([make_node('MTH-1', 'method', 'Noop', {'script': 'workspace/methods/noop.py', 'inputs': ['workspace/data/input.txt'], 'outputs': ['workspace/results/output.txt']}, status='confirmed')])
        with self.assertRaises(WorkspaceError): run_method(self.s(), 'MTH-1', 'Author', allow_exec=True)
        self.assertFalse(any(n['kind'] == 'result' for n in self.s().state['nodes'].values()))

    def test_audit_chain_corruption_detected(self):
        s = self.s(); s.state['events'][0]['actor'] = 'tampered'; s.commit()
        self.assertTrue(any(i['code'] == 'AUDIT_CHAIN' for i in review.review(self.s())['issues']))

    def test_recover_interrupted_transaction(self):
        s = self.s(); state = copy.deepcopy(s.state); state['revision'] += 1
        writes = {'workspace/state.json': pretty(state), 'workspace/memory.md': 'Recovered memory\n'}
        atomic_write(self.root / '.rw/transaction.json', pretty({'version': 1, 'writes': writes, 'before': {p: file_hash(self.root / p) for p in writes}}))
        with self.assertRaises(WorkspaceError): self.s()
        self.assertTrue(recover(self.root)['recovered'])
        self.assertEqual((self.root / 'workspace/memory.md').read_text(), 'Recovered memory\n')

    def test_recovery_preserves_intervening_user_changes(self):
        writes = {'workspace/state.json': pretty(self.s().state), 'workspace/memory.md': 'Planned change\n'}
        before = {p: file_hash(self.root / p) for p in writes}
        atomic_write(self.root / '.rw/transaction.json', pretty({'version': 1, 'writes': writes, 'before': before}))
        atomic_write(self.root / 'workspace/memory.md', 'New user note after interruption\n')
        with self.assertRaises(WorkspaceError): recover(self.root)
        self.assertIn('New user note', (self.root / 'workspace/memory.md').read_text())

    def test_counterevidence_response_required(self):
        self.evidence_fixture()
        node = copy.deepcopy(self.s().node('EVD-1')); node.pop('verification'); node['data']['relation'] = 'refutes'; self.add([node])
        self.assertTrue(any(i['code'] == 'COUNTEREVIDENCE_RESPONSE' for i in review.review(self.s())['issues']))

    def test_causal_design_and_unknown_rule_block(self):
        self.evidence_fixture()
        node = copy.deepcopy(self.s().node('CLM-1')); node['data']['strength'] = 'causal'
        self.add([node, make_node('RULE-1', 'rule', 'Unknown checker', {'type': 'not-implemented'}, status='confirmed')])
        codes = {i['code'] for i in review.review(self.s())['issues']}
        self.assertIn('CAUSAL_IDENTIFICATION', codes); self.assertIn('RULE_UNIMPLEMENTED', codes)

    def test_cycle_task_deduplication(self):
        a = skills.cycle(self.s(), 'router'); b = skills.cycle(self.s(), 'router')
        self.assertTrue(a['tasks']); self.assertEqual(b['tasks'], [])

    def test_all_nine_skill_contracts(self):
        self.assertEqual(len(skills.SKILLS), 9); self.assertTrue(skills.lint_skills(self.s())['passed'])


class DemonstrationCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); cls.root = Path(cls.tmp.name) / 'demo'; cls.summary = demonstrate(cls.root)
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def test_real_synthetic_computation(self):
        self.assertEqual(self.summary['computed_values']['paired_mean_difference'], -4.5)
        self.assertTrue(all(v is True or v == 'pass' for v in self.summary['checks'].values()))

    def test_demo_cannot_be_real_submission(self):
        self.assertFalse(review.gate(Store(self.root))['ready_for_packaging'])
        self.assertTrue(review.gate(Store(self.root), demonstration=True)['ready_for_packaging'])

    def test_writer_cannot_self_review(self):
        with self.assertRaises(WorkspaceError): review.attest(Store(self.root), 'research_logic', AUTHOR, NOTE, human=True)

    def test_changed_supplement_invalidates_approval(self):
        path = self.root / 'manuscript/supplementary/README.md'; before = path.read_text()
        try:
            atomic_write(path, before + '\nChanged supplement')
            self.assertFalse(review.gate(Store(self.root), demonstration=True)['ready_for_packaging'])
        finally: atomic_write(path, before)

    def test_export_manifest_hashes(self):
        folder = self.root / 'dist/demo-submission'; manifest = json.loads((folder / 'manifest.json').read_text())
        for path, sha in manifest['files'].items(): self.assertEqual(file_hash(folder / path), sha)

    def test_dashboard_escapes_project_text(self):
        from research_workspace.dashboard import dashboard
        s = Store(self.root); s.state['project']['name'] = '<script>alert(1)</script>'
        text = Path(dashboard(s)['dashboard']).read_text()
        self.assertNotIn('<script>', text); self.assertIn('&lt;script&gt;', text)


if __name__ == '__main__': unittest.main()
