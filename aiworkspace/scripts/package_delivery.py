#!/usr/bin/env python3
"""Create clean source/demo ZIPs locally. This script does not upload anything."""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--destination', required=True)
parser.add_argument('--demo', help='Only a generated project explicitly marked mode=demo is accepted')
parser.add_argument('--wheel-dir')
args = parser.parse_args()
out = Path(args.destination).expanduser().resolve()
if out.is_relative_to(root):
    raise SystemExit('Place delivery outputs outside the framework source checkout.')
out.mkdir(parents=True, exist_ok=True)


def pack(folder: Path, target: Path, prefix: str, *, source: bool):
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob('*')):
            if path.is_symlink(): raise SystemExit('Refusing symlink in delivery: ' + str(path))
            if not path.is_file(): continue
            relative = path.relative_to(folder)
            if source and (any(part in ('__pycache__', '.git', '.venv', 'build', 'dist', '.local') or part.endswith('.egg-info') for part in relative.parts) or path.name == '.env' or (path.name.startswith('.env.') and path.name != '.env.example')):
                continue
            if path.suffix.lower() in ('.ppt', '.pptx', '.pyc'):
                continue
            archive.write(path, prefix + '/' + relative.as_posix())


pack(root, out / 'ai-research-workspace-source.zip', 'ai-research-workspace', source=True)
if args.demo:
    demo = Path(args.demo).expanduser().resolve()
    state = json.loads((demo / 'workspace/state.json').read_text(encoding='utf-8'))
    if state.get('project', {}).get('mode') != 'demo':
        raise SystemExit('Refusing to package a real study through the public demonstration delivery path.')
    pack(demo, out / 'research-workspace-synthetic-demo.zip', 'research-workspace-demo', source=False)
if args.wheel_dir:
    for wheel in Path(args.wheel_dir).glob('ai_research_workspace-*.whl'):
        shutil.copy2(wheel, out / wheel.name)
checksums = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(out.iterdir()) if path.is_file() and path.name != 'SHA256SUMS.txt'}
(out / 'SHA256SUMS.txt').write_text(''.join(sha + '  ' + name + '\n' for name, sha in checksums.items()), encoding='utf-8')
print(json.dumps({'delivery': str(out), 'sha256': checksums}, indent=2))
