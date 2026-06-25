# Next Chat Start Prompt

Date: 2026-06-25

Copy this into a new conversation.

```text
Continue ORIS / OpenClaw / Codex-backed AI Dev Employee commercial insight product work.

Do not redesign from scratch.
Do not rely on chat memory.
Use GitHub as the source of truth.
Keep replies concise; write long state into GitHub files.

Product repo:
https://github.com/ShanGouXueHui/oris-commercial-insight-employee

First read these files in order:

1. docs/status/COMMERCIAL_INSIGHT_REBUILD_STATUS_2026-06-25_MODULES_1_24.md
2. docs/engineering/OPERATING_CONTEXT_AND_RULES_2026-06-25.md
3. docs/rebuild/INSIGHT_REBUILD_MODULE_24_TENANT_USAGE_LEDGER.md
4. reports/testing/latest_test_result.json
5. reports/execution/insight_rebuild_module_24_execution_report.md
6. AGENTS.md
7. app/config.py
8. app/main.py
9. app/tenant_guardrails.py
10. app/tenant_usage_ledger.py
11. app/evidence_harness.py

Current state:
- Modules 1-24 are accepted.
- Latest accepted module: Module 24 Tenant Usage Ledger.
- Latest full-suite unittest count: 137.
- Latest local validation commit: 3cacdf778a8693c1e311a3da8cc960d79579030a.
- Latest report evidence commit: 309a26a20447856b19cf5173bb8a7dc3433e4ae8.

Working rules:
- Directly modify GitHub files through the connector when possible.
- User runs official bootstrap locally/server-side and pastes output.
- Verify GitHub evidence before marking any module accepted.
- Do not use set -e in user copy-paste commands or official bootstrap scripts.
- Use app.evidence_harness for new module bootstraps.
- Preserve deterministic local defaults.
- Use explicit flags for behavior changes.
- Keep layers decoupled and configuration separate.
- Prefer reusable skills, harnesses, Loop Engineering patterns, and AGENTS.md guidance before custom code.
- Keep main as the mainstream commercial branch.

Next task:
Proceed with Module 25: connect the Module 24 tenant usage ledger to the Module 23 tenant middleware behind explicit configuration. Default behavior must remain unchanged. Add implementation, tests, docs, test plan, and official bootstrap. Do not mark accepted until user-controlled bootstrap evidence is pushed and verified.

If Module 25 proves risky, stop at a boundary module and document the decision in GitHub.
```
