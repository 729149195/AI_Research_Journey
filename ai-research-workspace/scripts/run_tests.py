#!/usr/bin/env python3
"""Run tests and emit evidence of this actual execution, not a hard-coded pass count."""
import argparse
import json
import platform
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', required=True)
args = parser.parse_args()
suite = unittest.defaultTestLoader.discover(str(root / 'tests'))
discovered = suite.countTestCases()
result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
report = {'at': datetime.now(timezone.utc).isoformat(), 'python': sys.version.split()[0], 'os': platform.platform(),
          'status': 'passed' if result.wasSuccessful() else 'failed', 'discovered': discovered, 'executed': result.testsRun,
          'failures': [{'test': str(test), 'traceback': text} for test, text in result.failures],
          'errors': [{'test': str(test), 'traceback': text} for test, text in result.errors],
          'skipped': [{'test': str(test), 'reason': reason} for test, reason in result.skipped],
          'boundary': 'Deterministic and synthetic integration tests; not live model-quality or scientific validation.'}
path = Path(args.output).expanduser().resolve()
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in ('failures', 'errors', 'skipped')}, ensure_ascii=False, indent=2))
raise SystemExit(0 if result.wasSuccessful() else 1)
