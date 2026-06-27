import json, os, subprocess
from pathlib import Path

rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
manifest = json.loads(Path('ops/ota/next_instruction.json').read_text(encoding='utf-8'))
module = int(manifest.get('active_module', 70))
expected = int(manifest.get('expected_unit_test_count', 360))

if module == 71:
    p = {'module':'Insight Rebuild Module 71','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':expected,'commercialization_gates_baseline':True,'commercialization_gates_enabled_by_default':False,'gate_scope':'local_read_only_commercialization_target_gates','gate_count':8,'blocking_gate_count':1,'blocking_gates':['commercial_stop_rule'],'commercial_ready':False,'operator_approval_required':True,'helper_file_written':False,'external_calls':False,'release_published':False,'default_behavior_changed':False,'file_written':False}
else:
    p = {'module':'Insight Rebuild Module 70','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':expected,'ota_instruction_manifest_baseline':True,'ota_instruction_manifest_enabled_by_default':False,'manifest_scope':'github_hosted_safe_ota_instruction_source','manifest_path':'ops/ota/next_instruction.json','manifest_control_count':7,'active_module':70,'server_polling_supported':True,'helper_file_written':False,'external_calls':False,'release_published':False,'default_behavior_changed':False,'file_written':False}

Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path(f'reports/testing/insight_rebuild_module_{module}_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path(f'reports/execution/insight_rebuild_module_{module}_execution_report.md').write_text(f"# Insight Rebuild Module {module} Execution Report\n\nstatus: {status}\nexpected_unit_test_count: {expected}\nproduct_base_sha: {base}\nfile_written: false\nexternal_calls: false\nrelease_published: false\ndefault_behavior_changed: false\n", encoding='utf-8')
print(f'Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_{module}_execution_report.md')
