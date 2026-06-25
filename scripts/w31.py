from __future__ import annotations

import json
import os
from pathlib import Path

rc = int(os.environ.get('TEST_RC', '1'))
v = os.environ.get('VERSION', '2026-06-25-insight-rebuild-module-31-official')
cmd = os.environ.get('TEST_COMMAND', '')
base = os.environ.get('PRODUCT_BASE_SHA', '')
log = os.environ.get('LOG_FILE', '')
status = 'passed' if rc == 0 else 'failed'
p = {
    'module': 'Insight Rebuild Module 31',
    'bootstrap_version': v,
    'status': status,
    'test_command': cmd,
    'test_exit_code': rc,
    'product_base_sha': base,
    'expected_unit_test_count': 183,
    'log_file': log,
    'local_audit_manifest': True,
    'manifest_only': True,
    'file_written': False,
}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_31_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_31_execution_report.md').write_text(f'# Insight Rebuild Module 31 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 183\nproduct_base_sha: {base}\n', encoding='utf-8')
