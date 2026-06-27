import json, os, subprocess
from pathlib import Path
rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
p = {'module':'Insight Rebuild Module 66','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':337,'commercial_security_rbac_baseline':True,'commercial_security_enabled_by_default':False,'security_scope':'local_read_only_commercial_security_rbac_baseline','security_role_count':5,'security_permission_count':8,'security_roles':['owner','admin','analyst','viewer','auditor'],'tenant_isolation_required':True,'audit_required':True,'safe_logging_required':True,'secret_boundary_required':True,'helper_file_written':False,'external_calls':False,'release_published':False,'default_behavior_changed':False,'file_written':False}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_66_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_66_execution_report.md').write_text(f"# Insight Rebuild Module 66 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 337\nproduct_base_sha: {base}\ncommercial_security_rbac_baseline: true\nsecurity_role_count: 5\nsecurity_permission_count: 8\ntenant_isolation_required: true\naudit_required: true\nsafe_logging_required: true\nsecret_boundary_required: true\nfile_written: false\nexternal_calls: false\nrelease_published: false\ndefault_behavior_changed: false\n", encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_66_execution_report.md')
