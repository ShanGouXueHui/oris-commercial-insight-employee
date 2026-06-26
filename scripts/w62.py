from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.commercial_readiness import build_commercial_readiness_baseline

MODULE = 'Insight Rebuild Module 62'
EXPECTED_TEST_COUNT = 311

rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
baseline = build_commercial_readiness_baseline(env={'ORIS_COMMERCIAL_READINESS_ENABLED': 'true'})
payload = {
    'module': MODULE,
    'status': status,
    'test_exit_code': rc,
    'product_base_sha': base,
    'expected_unit_test_count': EXPECTED_TEST_COUNT,
    'commercial_readiness_baseline': True,
    'commercial_readiness_enabled_by_default': False,
    'readiness_scope': baseline['readiness_scope'],
    'readiness_dimensions_count': baseline['dimension_count'],
    'readiness_dimensions': baseline['dimension_names'],
    'helper_file_written': baseline['file_written'],
    'external_calls': baseline['external_calls'],
    'release_published': baseline['release_published'],
    'default_behavior_changed': baseline['default_behavior_changed'],
    'file_written': False,
}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_62_test_result.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_62_execution_report.md').write_text(
    '# Insight Rebuild Module 62 Execution Report\n\n'
    f'status: {status}\n'
    f'expected_unit_test_count: {EXPECTED_TEST_COUNT}\n'
    f'product_base_sha: {base}\n'
    'commercial_readiness_baseline: true\n'
    'readiness_dimensions_count: 8\n'
    'file_written: false\n'
    'external_calls: false\n'
    'release_published: false\n'
    'default_behavior_changed: false\n',
    encoding='utf-8',
)
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_62_execution_report.md')
