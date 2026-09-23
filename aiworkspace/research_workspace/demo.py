"""Executable synthetic workflow. All human review declarations are marked simulations."""
from __future__ import annotations
import json
import shutil
import tempfile
from pathlib import Path
from .analysis import run_method
from .dashboard import dashboard
from .model import DOMAINS, make_node, now, pretty, require
from .review import attest, export_bundle, gate, save_report
from .scaffold import SECTION_NAMES, initialize
from .skills import cycle, task_packet
from .store import Store, atomic_write, file_hash
from .sync import plan, propose_sync
from .upgrade import ASSETS, apply_upgrade, plan_upgrade, rollback
from .workflow import apply, propose, resolve_issue, verify

AUTHOR = 'Demo Author (simulation)'
NOTE = 'DEMONSTRATION ONLY: inspected synthetic fixtures and reconciled declared logic and linked outputs. This is not real independent scientific validation.'
ANALYSIS_SCRIPT = '''"""Synthetic descriptive software fixture, not a real research study."""
import csv, json, statistics
from pathlib import Path
rows = list(csv.DictReader(Path("workspace/data/synthetic.csv").open(encoding="utf-8")))
a = [float(r["baseline"]) for r in rows]
b = [float(r["candidate"]) for r in rows]
result = {"n": len(rows), "baseline_mean": statistics.mean(a), "candidate_mean": statistics.mean(b), "paired_mean_difference": statistics.mean([y-x for x,y in zip(a,b)]), "synthetic": True}
Path("workspace/results/descriptives.json").write_text(json.dumps(result, indent=2)+"\\n", encoding="utf-8")
text = f"SYNTHETIC FIXTURE ONLY: n={len(rows)}; baseline mean={result['baseline_mean']:.2f}; candidate mean={result['candidate_mean']:.2f}; paired mean difference={result['paired_mean_difference']:.2f} arbitrary units. No causal or population inference is justified."
Path("workspace/results/summary.txt").write_text(text+"\\n", encoding="utf-8")
points = "".join(f'<circle cx="{100+i*48}" cy="{280-x*8}" r="4"/><rect x="{97+i*48}" y="{277-y*8}" width="6" height="6"/>' for i,(x,y) in enumerate(zip(a,b)))
svg = '<svg xmlns="http://www.w3.org/2000/svg" width="760" height="360" viewBox="0 0 760 360"><title>Synthetic paired observations</title><desc>Circles: baseline; squares: candidate. Twelve artificial pairs in arbitrary units.</desc><rect width="760" height="360" fill="white"/><path d="M80 40V280H710" stroke="black" fill="none"/><g fill="black">'+points+'</g><g font-family="sans-serif" font-size="14"><text x="80" y="24">SYNTHETIC DEMO - circles: baseline; squares: candidate</text><text x="260" y="330">Observation index (1-12)</text><text x="12" y="44">30</text><text x="12" y="124">20</text><text x="12" y="204">10</text><text x="20" y="284">0</text><text x="94" y="306">1</text><text x="620" y="306">12</text><text x="8" y="352">Vertical axis: arbitrary units; common zero-based scale</text></g></svg>'
Path("manuscript/figures/comparison.svg").write_text(svg, encoding="utf-8")
print(text)
'''


def demonstrate(destination: str | Path) -> dict:
    root = initialize(destination, 'Synthetic research workspace walkthrough', AUTHOR, mode='demo').root
    steps = []
    def accept(nodes, summary):
        proposal = propose(Store(root), [{'op': 'upsert', 'node': n} for n in nodes], 'demo:script', summary)
        apply(Store(root), proposal['id'], AUTHOR, NOTE, approve=True)
        steps.append(summary)
    question = make_node('RQ-001', 'question', 'Trace a synthetic comparison', {'text': 'Can a descriptive paired comparison be traced from artificial inputs to evidence and synchronized manuscript?'}, status='confirmed')
    hypothesis = make_node('HYP-001', 'hypothesis', 'Traceability hypothesis', {'text': 'Explicit IDs and file hashes make the declared provenance of this fixture inspectable.'}, ['RQ-001'], 'confirmed')
    argument = make_node('ARG-001', 'argument', 'Bound calculation and inference', {'text': 'Compute a descriptive difference, retain provenance, bound the assertion to this fixture and block stale output.'}, ['HYP-001'], 'confirmed')
    method = make_node('MTH-001', 'method', 'Paired descriptive means', {'script': 'workspace/methods/descriptives.py', 'inputs': ['workspace/data/synthetic.csv'],
        'outputs': ['workspace/results/descriptives.json', 'workspace/results/summary.txt', 'manuscript/figures/comparison.svg'], 'seed': 0,
        'design': 'Deterministic synthetic pairs; descriptive only. No human participants, sampling or inferential test.'}, ['RQ-001'], 'confirmed')
    accept([question, hypothesis, argument, method], 'Confirm demonstration question, argument and descriptive method')
    atomic_write(root / 'workspace/data/synthetic.csv', 'id,baseline,candidate\n' + ''.join(f'{i+1},{x},{x-(3+i%4)}\n' for i, x in enumerate(range(17, 29))))
    atomic_write(root / 'workspace/methods/descriptives.py', ANALYSIS_SCRIPT)
    result = run_method(Store(root), 'MTH-001', AUTHOR, allow_exec=True)
    values = json.loads((root / 'workspace/results/descriptives.json').read_text(encoding='utf-8'))
    require(values['n'] == 12 and values['paired_mean_difference'] == -4.5, 'Unexpected synthetic calculation.')
    steps.append('Actually execute local Python and hash inputs, script, JSON, text and SVG outputs')
    quote = (root / 'workspace/results/summary.txt').read_text(encoding='utf-8').strip()
    source = make_node('SRC-001', 'source', 'Synthetic run summary', {'category': 'primary', 'url': 'local:synthetic-run', 'snapshot': 'workspace/results/summary.txt', 'synthetic': True, 'retracted': False}, [result['id']])
    claim = make_node('CLM-001', 'claim', 'Bounded descriptive difference', {'text': 'In this synthetic fixture, the paired mean difference is -4.50 arbitrary units.', 'strength': 'descriptive',
        'scope': 'Twelve artificial pairs only, not a sampled population.', 'counterevidence_search': {'query': 'Inspect every generated pair in workspace/data/synthetic.csv; no external literature search', 'date': now(), 'result': 'All 12 pair differences inspected; no inference beyond this deterministic fixture.'}}, ['EVD-001', 'MTH-001'], 'confirmed')
    evidence = make_node('EVD-001', 'evidence', 'Exact computed descriptive result', {'source': 'SRC-001', 'claim': 'CLM-001', 'quote': quote,
        'locator': 'workspace/results/summary.txt, line 1', 'scope': 'Artificial paired means; no real-world or causal inference.', 'relation': 'supports'}, ['SRC-001'])
    figure = make_node('FIG-001', 'figure', 'All synthetic paired observations', {'path': 'manuscript/figures/comparison.svg', 'sha256': file_hash(root / 'manuscript/figures/comparison.svg'), 'claims': ['CLM-001'],
        'caption': 'Twelve artificial pairs on one zero-based scale; circles and squares distinguish conditions.', 'purpose': 'Show all generated observations behind the descriptive mean.',
        'alt_text': 'The candidate values are three to six arbitrary units below baseline in each synthetic pair.'}, ['CLM-001', result['id']], 'confirmed')
    content = {'SEC-ABSTRACT': 'This software demonstration traces a synthetic paired comparison from input to manuscript. The mean difference is -4.50 arbitrary units [@SRC-001]. No real-world effect is claimed.',
               'SEC-INTRO': 'The question is whether explicit provenance remains inspectable across analysis, writing and revision. This is a software demonstration, not a scientific finding.',
               'SEC-METHODS': 'We generated 12 artificial pairs and computed paired descriptive means with the supplied Python standard-library script. There were no participants or inferential tests.',
               'SEC-RESULTS': quote + ' [@SRC-001]\n\n![All synthetic pairs](figures/comparison.svg)\n\nFigure 1. Circles: baseline. Squares: candidate. All observations are artificial.',
               'SEC-DISCUSSION': 'The calculation is reproducible within this synthetic fixture. This does not validate any real-world effect or establish causation.',
               'SEC-CONCLUSION': 'The synthetic descriptive Claim is linked to its source, method, run and figure. Real research needs fresh domain review.'}
    sections = [make_node(key, 'section', title, {'text': '## ' + title + '\n\n' + content[key]}, ['ARG-001', 'CLM-001'], 'confirmed') for key, title in SECTION_NAMES.items()]
    accept([source, claim, evidence, figure, *sections], 'Bind computation, evidence, Claim, figure and all six manuscript sections')
    verify(Store(root), 'SRC-001', AUTHOR, NOTE, human=True)
    verify(Store(root), 'EVD-001', AUTHOR, NOTE, human=True)
    steps.append('Record explicitly simulated human declarations; actually check original quote and byte hashes')
    proposal = propose_sync(Store(root), 'demo:sync')
    apply(Store(root), proposal['id'], AUTHOR, NOTE, approve=True)
    manuscript = root / 'manuscript/main.md'
    atomic_write(manuscript, manuscript.read_text(encoding='utf-8').replace('The calculation is reproducible within this synthetic fixture.', 'The calculation is reproducible only within this synthetic fixture; external validity is unknown.'))
    proposal = propose_sync(Store(root), 'demo:sync')
    apply(Store(root), proposal['id'], AUTHOR, NOTE, approve=True)
    require(not plan(Store(root))['changes'], 'Bidirectional sync failed to converge.')
    steps.append('Synchronize Workspace-to-Manuscript and an external manuscript edit back; require semantic review')
    for issue_id in [i['id'] for i in Store(root).state['issues'].values() if i['status'] == 'open']:
        resolve_issue(Store(root), issue_id, 'Demo Reviewer (simulation)', NOTE)
    idea = root / 'workspace/research/idea-evaluation.md'
    atomic_write(idea, idea.read_text(encoding='utf-8') + '\nUser-owned filled research note: retain this on upgrade.\n')
    protected = [idea, manuscript, root / 'workspace/state.json', root / 'workspace/rules/project-policy.md']
    before = [file_hash(path) for path in protected]
    with tempfile.TemporaryDirectory() as directory:
        staged = Path(directory)
        shutil.copytree(ASSETS, staged / 'research_workspace/assets')
        manifest = staged / 'research_workspace/assets/release.json'
        config = json.loads(manifest.read_text(encoding='utf-8'))
        config['version'] = '0.1.1-demo-fixture'
        atomic_write(manifest, pretty(config))
        skill = staged / 'research_workspace/assets/skills/researcher/SKILL.md'
        atomic_write(skill, skill.read_text(encoding='utf-8') + '\nNew upstream fixture guidance.\n')
        require(not plan_upgrade(root, staged)['conflicts'], 'Unexpected demo upgrade conflict.')
        updated = apply_upgrade(root, staged, AUTHOR, approve=True)
        require(before == [file_hash(path) for path in protected], 'Upgrade touched user research.')
        rollback(root, updated['backup_id'])
        require(before == [file_hash(path) for path in protected], 'Rollback touched user research.')
    steps.append('Incrementally update a used study and roll back; assert research/manuscript/filled template/policy hashes unchanged')
    cycle(Store(root), 'demo:router')
    packet = task_packet(Store(root), 'reviewer', 'Independently inspect this explicitly synthetic walkthrough, not a real scientific study.')
    atomic_write(root / 'workspace/reports/reviewer-task.json', pretty(packet))
    report = save_report(Store(root))
    require(report['machine_status'] == 'pass', 'Demo blocked: ' + pretty(report['issues']))
    require(not gate(Store(root))['ready_for_packaging'], 'Unreviewed release must be blocked.')
    for domain in DOMAINS:
        attest(Store(root), domain, 'Demo Reviewer (simulation)', NOTE, human=True)
    attest(Store(root), 'author_release', AUTHOR, NOTE, human=True)
    require(not gate(Store(root))['ready_for_packaging'], 'Demo must not become a real submission.')
    exported = export_bundle(Store(root), root / 'dist/demo-submission', demonstration=True)
    dashboard(Store(root))
    steps.append('Pass machine checks; simulate all review declarations; export only with explicit demonstration flag')
    summary = {'project': str(root), 'steps': steps, 'computed_values': values, 'checks': {'bidirectional_sync': True, 'incremental_upgrade': True, 'rollback': True,
        'user_data_preserved': True, 'unreviewed_release_blocked': True, 'real_submission_from_demo_blocked': True, 'machine_review': 'pass'},
        'exported': exported['exported'], 'boundary': 'Actual computation and software walkthrough with synthetic data. Human declarations are simulations. No live model, real expert review or scientific validation occurred.'}
    atomic_write(root / 'workspace/reports/walkthrough.json', pretty(summary))
    return summary
