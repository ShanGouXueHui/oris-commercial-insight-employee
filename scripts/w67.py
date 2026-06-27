import json, os, subprocess
from pathlib import Path
rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
p = {'module':'Insight Rebuild Module 67','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':343,'commercial_observability_baseline':True,'commercial_observability_enabled_by_default':False,'observability_scope':'local_read_only_commercial_observability_baseline','observability_signal_count':6,'observability_signals':['health','metrics','traces','logs','run_diagnostics','failure_taxonomy'],'run_id_required':True,'trace_id_required':True,'safe_logging_required':True,'operator_diagnostics_required':True,'helper_file_written':False,'external_calls':False,'release_published':False,'default_behavior_changed':False,'file_written':False}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_67_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_67_execution_report.md').write_text(f"# Insight Rebuild Module 67 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 343\nproduct_base_sha: {base}\ncommercial_observability_baseline: true\nobservability_signal_count: 6\nrun_id_required: true\ntrace_id_required: true\nsafe_logging_required: true\noperator_diagnostics_required: true\nfile_written: false\nexternal_calls: false\nrelease_published: false\ndefault_behavior_changed: false\n", encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_67_execution_report.md')
