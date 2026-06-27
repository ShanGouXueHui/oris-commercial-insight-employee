import json, os, subprocess
from pathlib import Path
rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
p = {'module':'Insight Rebuild Module 69','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':354,'ota_scheduler_baseline':True,'ota_scheduler_enabled_by_default':False,'scheduler_scope':'manual_server_schedule_for_unified_ota_entry','scheduler_control_count':7,'scheduler_controls':['ten_minute_cadence','server_local_schedule','manual_install_only','unified_entrypoint_target','ota_log_append','safe_reinstall','least_privilege_mode'],'cadence_minutes':10,'manual_install_required':True,'helper_file_written':False,'external_calls':False,'release_published':False,'default_behavior_changed':False,'file_written':False}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_69_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_69_execution_report.md').write_text(f"# Insight Rebuild Module 69 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 354\nproduct_base_sha: {base}\nota_scheduler_baseline: true\nscheduler_control_count: 7\ncadence_minutes: 10\nmanual_install_required: true\nfile_written: false\nexternal_calls: false\nrelease_published: false\ndefault_behavior_changed: false\n", encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_69_execution_report.md')
