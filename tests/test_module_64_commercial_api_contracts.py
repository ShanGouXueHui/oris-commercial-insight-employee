import unittest

from app.commercial_api_contracts import (
    CONTRACT_ORDER,
    build_api_contract_baseline,
    get_api_contract,
    summarize_api_contracts,
)


class Module64CommercialApiContractsTests(unittest.TestCase):
    def test_disabled_by_default_is_safe(self):
        result = build_api_contract_baseline(env={})
        self.assertFalse(result['allowed'])
        self.assertFalse(result['enabled'])
        self.assertFalse(result['enabled_by_default'])
        self.assertFalse(result['file_written'])
        self.assertFalse(result['external_calls'])
        self.assertFalse(result['release_published'])
        self.assertFalse(result['default_behavior_changed'])
        self.assertEqual(result['contracts'], [])

    def test_enabled_returns_contracts_in_order(self):
        result = build_api_contract_baseline(env={'ORIS_COMMERCIAL_API_CONTRACTS_ENABLED': 'true'})
        self.assertTrue(result['allowed'])
        self.assertEqual(result['status'], 'api_contract_baseline_defined')
        self.assertEqual(result['contract_count'], 7)
        self.assertEqual(result['contract_names'], list(CONTRACT_ORDER))

    def test_tenant_contract_is_public_v1(self):
        contract = get_api_contract('tenant_v1')
        self.assertEqual(contract['resource'], 'tenant')
        self.assertEqual(contract['version'], 'v1')
        self.assertTrue(contract['tenant_scoped'])
        self.assertTrue(contract['public_contract'])

    def test_work_contracts_include_parent_ids(self):
        workspace = get_api_contract('workspace_v1')
        project = get_api_contract('project_v1')
        insight = get_api_contract('insight_v1')
        self.assertIn('tenant_id', workspace['required_fields'])
        self.assertIn('workspace_id', project['required_fields'])
        self.assertIn('project_id', insight['required_fields'])

    def test_evidence_execution_audit_have_limited_operations(self):
        evidence = get_api_contract('evidence_v1')
        execution = get_api_contract('execution_v1')
        audit = get_api_contract('audit_v1')
        self.assertEqual(evidence['operations'], ('create', 'read'))
        self.assertEqual(execution['operations'], ('create', 'read'))
        self.assertEqual(audit['operations'], ('read',))

    def test_summary_is_compact_and_safe(self):
        summary = summarize_api_contracts(env={})
        self.assertFalse(summary['enabled'])
        self.assertFalse(summary['enabled_by_default'])
        self.assertEqual(summary['contract_count'], 0)
        self.assertFalse(summary['file_written'])
        self.assertFalse(summary['external_calls'])
        self.assertFalse(summary['release_published'])


if __name__ == '__main__':
    unittest.main()
