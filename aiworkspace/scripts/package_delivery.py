#!/usr/bin/env python3
"""Package framework source, optional wheels and a clearly labeled synthetic demo."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parent
EXCLUDED = {'.git', '.venv', '__pycache__', 'build', 'dist', '.pytest_cache'}


def archive(folder: Path, output: Path, prefix: str, *, extra: list[Path] | None = None) -> None:
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as target:
        for path in sorted(folder.rglob('*')):
            relative = path.relative_to(folder)
            excluded = EXCLUDED if prefix == 'aiworkspace' else EXCLUDED - {'dist'}
            if any(x in excluded or x.endswith('.egg-info') for x in relative.parts):
                continue
            if path.is_symlink():
                raise ValueError('Refusing to distribute a symlink: ' + str(path))
            if path.is_file():
                if path.suffix.lower() in ('.ppt', '.pptx', '.pyc') or path.name.startswith('.env'):
                    raise ValueError('Unexpected private/binary build material: ' + str(path))
                target.write(path, prefix + '/' + relative.as_posix())
        for path in extra or []:
            if not path.is_file() or path.is_symlink():
                raise ValueError('Missing/unsafe root delivery file: ' + str(path))
            target.write(path, path.name)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', required=True)
    p.add_argument('--demo')
    p.add_argument('--wheel-dir')
    a = p.parse_args()
    destination = Path(a.destination).expanduser().resolve()
    if destination.is_relative_to(PACKAGE) or destination.exists():
        raise ValueError('Use a new destination outside the framework package.')
    if a.demo and destination.is_relative_to(Path(a.demo).expanduser().resolve()):
        raise ValueError('Delivery destination may not be inside the demo study.')
    destination.mkdir(parents=True)
    archive(PACKAGE, destination / 'aiworkspace-source.zip', 'aiworkspace',
            extra=[ROOT / 'README.md', ROOT / 'update_aiworkspace.py', ROOT / '.gitignore'])
    if a.demo:
        demo = Path(a.demo).expanduser().resolve()
        state = json.loads((demo / 'workspace/state.json').read_text(encoding='utf-8'))
        if state.get('project', {}).get('mode') != 'demo':
            raise ValueError('Only explicitly synthetic demo studies may be distributed by this helper.')
        archive(demo, destination / 'SYNTHETIC-DEMO-ONLY.zip', 'research-demo')
    if a.wheel_dir:
        for path in Path(a.wheel_dir).glob('ai_research_workspace-*.whl'):
            shutil.copy2(path, destination / path.name)
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in destination.iterdir() if p.is_file()}
    (destination / 'SHA256SUMS.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'destination': str(destination), 'files': manifest,
                      'note': 'Source ZIP has no Git history; clone the repository for the root Git updater.'}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
