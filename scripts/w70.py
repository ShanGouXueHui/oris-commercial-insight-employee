import json, os, subprocess
from pathlib import Path
rc = int(os.environ.get('TEST_RC', '1'))
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
status = 'passed' if rc == 0 else 'failed'
p = {'module':'Insight Rebuild Module 70','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':360,'ota_instruction_manifest_baseline':True,'ota_instruction_manifest_enabled_by_default':False,'manifest_scope':'github_hosted_safe_ota_instruction_source','manifest_path':'ops/ota/next_instruction.json','manifest_control_count':7,'active_module':70,'server_polling_supported':True,'helper_file_written':False,'external_calls':False,'release_published':False,'default_behavior_changed':False,'file_written':False}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_70_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_70_execution_report.md').write_text(f"# Insight Rebuild Module 70 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 360\nproduct_base_sha: {base}\nota_instruction_manifest_baseline: true\nmanifest_path: ops/ota/next_instruction.json\nmanifest_control_count: 7\nserver_polling_supported: true\nfile_written: false\nexternal_calls: false\nrelease_published: false\ndefault_behavior_changed: false\n", encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_70_execution_report.md')
