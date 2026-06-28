import json, os
from pathlib import Path


def current_git_sha():
    git_dir = Path('.git')
    head = (git_dir / 'HEAD').read_text(encoding='utf-8').strip()
    if not head.startswith('ref: '):
        return head
    ref = head.split(' ', 1)[1]
    ref_path = git_dir / ref
    if ref_path.exists():
        return ref_path.read_text(encoding='utf-8').strip()
    packed_refs = git_dir / 'packed-refs'
    if packed_refs.exists():
        for line in packed_refs.read_text(encoding='utf-8').splitlines():
            if line and not line.startswith('#') and line.endswith(' ' + ref):
                return line.split(' ', 1)[0]
    return head


rc = int(os.environ.get('TEST_RC', '1'))
base = current_git_sha()
status = 'passed' if rc == 0 else 'failed'
p = {'module':'Insight Rebuild Module 119','status':status,'test_exit_code':rc,'product_base_sha':base,'expected_unit_test_count':380,'module_119_baseline':True,'external_calls':False,'release_published':False,'default_behavior_changed':False}
Path('reports/testing').mkdir(parents=True, exist_ok=True)
Path('reports/execution').mkdir(parents=True, exist_ok=True)
Path('reports/testing/insight_rebuild_module_119_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/testing/latest_test_result.json').write_text(json.dumps(p, indent=2), encoding='utf-8')
Path('reports/execution/insight_rebuild_module_119_execution_report.md').write_text(f"# Insight Rebuild Module 119 Execution Report\n\nstatus: {status}\nexpected_unit_test_count: 380\nproduct_base_sha: {base}\n", encoding='utf-8')
print('Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_119_execution_report.md')
