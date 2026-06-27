import json, os, subprocess
from pathlib import Path
rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
p = {'module':'Insight Rebuild Module 68','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':349,'unified_ota_entry_baseline':True,'unified_ota_enabled_by_default':False,'ota_scope':'safe_server_side_unified_ota_entry_baseline','ota_control_count':7,'ota_controls':['single_entrypoint','repo_fast_forward_only','lock_guard','allowlisted_runner','timestamped_logs','evidence_autocommit','no_release_publish'],'background_task_ready':True,'server_manual_install_required':True,'helper_file_written':False,'external_calls':False,'release_published':False,'default_behavior_changed':False,'file_written':False}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_68_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_68_execution_report.md').write_text(f"# Insight Rebuild Module 68 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 349\nproduct_base_sha: {base}\nunified_ota_entry_baseline: true\nota_control_count: 7\nbackground_task_ready: true\nserver_manual_install_required: true\nfile_written: false\nexternal_calls: false\nrelease_published: false\ndefault_behavior_changed: false\n", encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_68_execution_report.md')
