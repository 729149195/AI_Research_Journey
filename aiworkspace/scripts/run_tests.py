#!/usr/bin/env python3
"""Run the actual offline unit suite and optionally save a machine-readable record."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
import time
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', help='Optional JSON report path outside a framework checkout')
    a = p.parse_args()
    started = time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(PACKAGE / 'tests'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {'at': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
              'platform': platform.system(), 'tests_run': result.testsRun,
              'successful': result.wasSuccessful(), 'failures': len(result.failures),
              'errors': len(result.errors), 'skipped': len(result.skipped),
              'elapsed_seconds': round(time.monotonic() - started, 3),
              'boundary': 'Actual local software tests; mock APIs and synthetic data are not live-model or scientific validation.'}
    text = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if a.output:
        path = Path(a.output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    print(text, end='')
    return 0 if report['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
