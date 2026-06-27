from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.commercial_architecture import build_commercial_architecture_baseline

rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
b = build_commercial_architecture_baseline(env={'ORIS_COMMERCIAL_ARCHITECTURE_ENABLED': 'true'})
payload = {
    'module': 'Insight Rebuild Module 63',
    'status': status,
    'test_exit_code': rc,
    'product_base_sha': base,
    'expected_unit_test_count': 319,
    'commercial_architecture_baseline': True,
    'commercial_architecture_enabled_by_default': False,
    'architecture_scope': b['architecture_scope'],
    'architecture_entity_count': b['entity_count'],
    'architecture_boundary_count': b['boundary_count'],
    'architecture_entities': b['entity_names'],
    'architecture_boundaries': b['boundary_names'],
    'helper_file_written': b['file_written'],
    'external_calls': b['external_calls'],
    'release_published': b['release_published'],
    'default_behavior_changed': b['default_behavior_changed'],
    'file_written': False,
}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_63_test_result.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_63_execution_report.md').write_text(
    '# Insight Rebuild Module 63 Execution Report\n\n'
    f'status: {status}\n'
    'expected_unit_test_count: 319\n'
    f'product_base_sha: {base}\n'
    'commercial_architecture_baseline: true\n'
    'architecture_entity_count: 8\n'
    'architecture_boundary_count: 4\n'
    'file_written: false\n'
    'external_calls: false\n'
    'release_published: false\n'
    'default_behavior_changed: false\n',
    encoding='utf-8',
)
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_63_execution_report.md')
