# Operating Context and Engineering Rules

Date: 2026-06-25

## Environment

- Product repo: `ShanGouXueHui/oris-commercial-insight-employee`
- Primary branch: `main`
- User-controlled path: `/home/admin/projects/oris-commercial-insight-employee`

Official validation pattern:

```bash
cd /home/admin/projects/oris-commercial-insight-employee
git pull --ff-only origin main
bash scripts/bootstrap_insight_rebuild_module_<N>.sh
```

## Interaction Habit

- Prefer direct GitHub file updates.
- Keep long state in GitHub files, not chat.
- Verify `reports/testing/latest_test_result.json` and the matching execution report before accepting a module.
- Keep user-facing replies short.

## Engineering Rules

- Keep layers decoupled.
- Keep configuration separate from implementation.
- Preserve deterministic local behavior by default.
- Use explicit flags for behavior changes.
- Maintain existing interfaces unless a module explicitly changes them.
- Prefer reusable skills, harnesses, and templates before custom scaffolding.
- Keep `main` as the mainstream commercial branch.
- Build a generic commercial product, not a one-off demo.

## Bootstrap Rules

- Do not use `set -e` in user copy-paste shell commands or official bootstrap scripts.
- Terminal output should stay short.
- Detailed evidence goes to `reports/testing` and `reports/execution`.
- New bootstrap scripts should use `app.evidence_harness`.

## Product Direction

- Continue commercializing the Insight Product / Commercial Insight Employee.
- Keep tenant, entitlement, usage, protection, and loop orchestration boundaries explicit.
- Loop Engineering means bounded workflows with evidence, not unlimited autonomy.
- Next work should move from local components toward controlled commercial operation.
