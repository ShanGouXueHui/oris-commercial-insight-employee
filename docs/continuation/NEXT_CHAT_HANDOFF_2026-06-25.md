# Next Chat Handoff

Date: 2026-06-25

## Why Start a New Chat

The current conversation is long. Continue with GitHub documents as the source of truth.

## Must Read First

1. `docs/status/COMMERCIAL_INSIGHT_REBUILD_STATUS_2026-06-25_MODULES_1_25.md`
2. `docs/engineering/OPERATING_CONTEXT_AND_RULES_2026-06-25.md`
3. `docs/rebuild/INSIGHT_REBUILD_MODULE_25_TENANT_MIDDLEWARE_USAGE_LEDGER.md`
4. `reports/testing/latest_test_result.json`
5. `reports/execution/insight_rebuild_module_25_execution_report.md`
6. `AGENTS.md`
7. `app/config.py`
8. `app/main.py`
9. `app/tenant_guardrails.py`
10. `app/tenant_usage_ledger.py`
11. `app/evidence_harness.py`

## Project State

- Modules 1-25 are accepted.
- Current full-suite count is 144.
- Module 24 added the local deterministic tenant usage ledger.
- Module 25 connected that ledger to tenant middleware behind explicit configuration.
- Module 25 bootstrap evidence was user-controlled and pushed.

## Latest Accepted Evidence

- Module: Insight Rebuild Module 25
- User-controlled bootstrap final pushed commit: `4adc3defb6c3344c2cdcfd47281864e70a60eb1e`
- Evidence commit recorded in report: `5d3d34e44a088ccbbb8a8b6b6eee73eeeb72a775`
- Product base commit tested by bootstrap: `8ae2f3e0ff95fdf2768eb1b59ef04955352f36e0`
- Test command: `python3 -m unittest discover -s tests -p test_*.py -q`
- Test exit code: `0`
- Expected unit test count: `144`

## Next Task

Proceed with Module 26 after reading GitHub state first.

Recommended Module 26 direction:

- Durable tenant usage storage behind explicit configuration; or
- Bounded tenant usage/admin read API behind explicit configuration.

Default behavior must remain unchanged. No external billing, payment, provider call, remote runtime dispatch, or live database connection should be enabled unless explicitly scoped and evidenced.

## Original Startup Context To Preserve

The project is ORIS / OpenClaw / Codex-backed AI Dev Employee moving into commercial Insight Product development. Do not redesign from scratch. Prefer reusable GitHub/OpenClaw skills, harnesses, Loop Engineering, and AGENTS.md guidance before custom code.

## Unfinished From Broad Startup Context

If returning to root ORIS rather than the product repo, read the persistent context in `ShanGouXueHui/oris` first. For this commercial track, continue from the product repo files listed above.
