# Insight Rebuild Module 2 Test Plan

## Scope

Validate the commercial insight domain contracts and evidence validation gates.

## Test Targets

1. Default domain contract contains all required analytical lenses.
2. Invalid subject is rejected.
3. Low source credibility is detected.
4. Missing source references are detected.
5. Complete evidence set passes validation.
6. Dictionary serialization uses stable string enum values.

## Acceptance

Module 2 passes only when tests pass and evidence is written to:

- reports/testing/insight_rebuild_module_2_test_result.json
- reports/testing/latest_test_result.json
- reports/execution/insight_rebuild_module_2_execution_report.md
