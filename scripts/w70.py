import json, os, subprocess
from pathlib import Path
rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
p = {'module':'Insight Rebuild Module 104','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':380,'module_104_baseline':True,'external_calls':False,'release_published':False,'default_behavior_changed':False}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_104_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_104_execution_report.md').write_text(f"# Insight Rebuild Module 104 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 380\nproduct_base_sha: {base}\n", encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_104_execution_report.md')
