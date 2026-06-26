from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
payload = {
    'module': 'Insight Rebuild Module 39',
    'status': status,
    'test_exit_code': rc,
    'product_base_sha': base,
    'expected_unit_test_count': 215,
    'local_rollup_health': True,
    'file_written': False,
}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_39_test_result.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_39_execution_report.md').write_text(
    f'# Insight Rebuild Module 39 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 215\nproduct_base_sha: {base}\n',
    encoding='utf-8',
)
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_39_execution_report.md')
