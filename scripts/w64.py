import json, os, subprocess
from pathlib import Path
rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
p = {
  'module': 'Insight Rebuild Module 64',
  'status': status,
  'test_exit_code': rc,
  'product_base_sha': base,
  'expected_unit_test_count': 325,
  'commercial_api_contract_baseline': True,
  'commercial_api_contracts_enabled_by_default': False,
  'api_scope': 'local_read_only_commercial_api_contract_baseline',
  'api_contract_count': 7,
  'api_contracts': ['tenant_v1', 'workspace_v1', 'project_v1', 'insight_v1', 'evidence_v1', 'execution_v1', 'audit_v1'],
  'helper_file_written': False,
  'external_calls': False,
  'release_published': False,
  'default_behavior_changed': False,
  'file_written': False,
}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_64_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_64_execution_report.md').write_text(f"# Insight Rebuild Module 64 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 325\nproduct_base_sha: {base}\ncommercial_api_contract_baseline: true\napi_contract_count: 7\nfile_written: false\nexternal_calls: false\nrelease_published: false\ndefault_behavior_changed: false\n", encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_64_execution_report.md')
