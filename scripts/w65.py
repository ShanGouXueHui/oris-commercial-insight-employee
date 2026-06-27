import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.commercial_storage import build_storage_boundary_baseline
rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
b = build_storage_boundary_baseline(env={'ORIS_COMMERCIAL_STORAGE_ENABLED': 'true'})
p = {
 'module': 'Insight Rebuild Module 65',
 'status': 'passed' if rc == 0 else 'failed',
 'test_exit_code': rc,
 'product_base_sha': base,
 'expected_unit_test_count': 331,
 'commercial_storage_boundary_baseline': True,
 'commercial_storage_enabled_by_default': False,
 'storage_scope': b['storage_scope'],
 'storage_boundary_count': b['store_count'],
 'storage_boundaries': b['store_names'],
 'local_evidence_separated': b['local_evidence_separated'],
 'helper_file_written': b['file_written'],
 'external_calls': b['external_calls'],
 'release_published': b['release_published'],
 'default_behavior_changed': b['default_behavior_changed'],
 'file_written': False,
}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_65_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_65_execution_report.md').write_text('module 65 execution report\nstatus: '+p['status']+'\nexpected_unit_test_count: 331\n', encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_65_execution_report.md')
