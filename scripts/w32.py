from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

rc = int(os.environ.get('TEST_RC', '1'))
v = os.environ.get('VERSION', '2026-06-26-insight-rebuild-module-32-official')
cmd = os.environ.get('TEST_COMMAND', 'python3 -m unittest discover -s tests -p test_*.py -q')
base = os.environ.get('PRODUCT_BASE_SHA', '') or subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
log = os.environ.get('LOG_FILE', 'reports/execution/insight_rebuild_module_32_bootstrap_latest.log')
status = 'passed' if rc == 0 else 'failed'
p = {
    'module': 'Insight Rebuild Module 32',
    'bootstrap_version': v,
    'status': status,
    'test_command': cmd,
    'test_exit_code': rc,
    'product_base_sha': base,
    'expected_unit_test_count': 187,
    'log_file': log,
    'local_manifest_checksum': True,
    'local_manifest_checksum_default_enabled': False,
    'checksum_visible': True,
    'file_written': False,
    'explicit_configuration_required': True,
    'request_path_unchanged_by_default': True,
    'local_manifest_checksum_version': '2026-06-26-module-32',
    'external_storage_enabled': False,
    'live_external_action_enabled': False,
}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_32_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_32_execution_report.md').write_text(
    f'# Insight Rebuild Module 32 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 187\nproduct_base_sha: {base}\n',
    encoding='utf-8',
)
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_32_execution_report.md')
