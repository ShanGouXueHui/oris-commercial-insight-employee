# Next Chat Handoff

Date: 2026-06-25

## Why Start a New Chat

The current conversation is long. Continue with GitHub documents as the source of truth.

## Must Read First

1. `docs/status/COMMERCIAL_INSIGHT_REBUILD_STATUS_2026-06-25_MODULES_1_24.md`
2. `docs/engineering/OPERATING_CONTEXT_AND_RULES_2026-06-25.md`
3. `docs/continuation/NEXT_CHAT_START_PROMPT_2026-06-25.md`
4. `docs/rebuild/INSIGHT_REBUILD_MODULE_24_TENANT_USAGE_LEDGER.md`
5. `reports/testing/latest_test_result.json`
6. `reports/execution/insight_rebuild_module_24_execution_report.md`
7. `AGENTS.md`

## Project State

- Modules 1-24 are accepted.
- Current full-suite count is 137.
- Module 24 added the local tenant usage ledger.
- Module 25 is next.

## Next Task

Implement Module 25:

- Connect tenant usage ledger to tenant middleware behind an explicit flag.
- Keep default behavior unchanged.
- Add implementation, tests, docs, test plan, and official bootstrap.
- Use `app.evidence_harness`.
- Ask user to run the official bootstrap.
- Verify pushed evidence before marking accepted.

## Original Startup Context To Preserve

The project is ORIS / OpenClaw / Codex-backed AI Dev Employee moving into commercial Insight Product development. Do not redesign from scratch. Prefer reusable GitHub/OpenClaw skills, harnesses, Loop Engineering, and AGENTS.md guidance before custom code.

## Unfinished From Broad Startup Context

If returning to root ORIS rather than the product repo, read the persistent context in `ShanGouXueHui/oris` first. For this commercial track, continue from the product repo files listed above.
