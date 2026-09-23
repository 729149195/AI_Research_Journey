#!/usr/bin/env python3
"""Check local links, packaged defaults and evaluation coverage without network access."""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parent
sys.path.insert(0, str(PACKAGE))
from research_workspace.model import WorkspaceError
from research_workspace.skills import SKILLS, lint_skills
from research_workspace.upgrade import release


def main() -> int:
    errors, checked = [], 0
    skip = {'.git', '.venv', '__pycache__', 'build', 'dist'}
    files = [p for p in PACKAGE.rglob('*') if p.is_file() and not any(x in skip or x.endswith('.egg-info') for x in p.parts)]
    if (ROOT / 'README.md').exists():
        files.append(ROOT / 'README.md')
    for path in files:
        if path.suffix.lower() in ('.ppt', '.pptx'):
            errors.append('Presentation binary must not ship: ' + str(path))
        if path.suffix != '.md':
            continue
        text = path.read_text(encoding='utf-8')
        for link in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^\s)]+)\)', text):
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            checked += 1
            if not target.exists():
                errors.append(str(path.relative_to(ROOT)) + ': missing ' + link)
    try:
        manifest = release()
        skill_lint = lint_skills()
        if not skill_lint['passed']:
            errors.extend(str(e) for e in skill_lint['errors'])
        registry = json.loads((PACKAGE / 'evals/scenarios.json').read_text(encoding='utf-8'))
        scenarios = registry['scenarios']
        if {s['skill'] for s in scenarios} != set(SKILLS):
            errors.append('Behavior scenarios do not cover exactly the registered Skills.')
        if len({s['id'] for s in scenarios}) != len(scenarios):
            errors.append('Duplicate scenario IDs.')
        for item in scenarios:
            if not item.get('prompt') or not item.get('expected') or item.get('status') != 'not_run':
                errors.append('Scenarios must define inputs/checks and not claim unperformed live execution.')
    except (OSError, ValueError, KeyError, WorkspaceError) as exc:
        errors.append(str(exc))
        manifest, scenarios = {'files': {}}, []
    report = {'passed': not errors, 'relative_links_checked': checked,
              'managed_assets': len(manifest['files']), 'skill_scenarios': len(scenarios), 'errors': errors,
              'boundary': 'Offline documentation, asset and scenario structure checks; no live-host behavior evaluation.'}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
