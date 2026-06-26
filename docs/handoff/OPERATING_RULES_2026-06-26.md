# Operating Rules

Date: 2026-06-26

## Repository and server

Repository: `ShanGouXueHui/oris-commercial-insight-employee`.

Default branch: `main` only. Backup branches may exist, but main is the only active product branch.

Server project directory: `/home/admin/projects/oris-commercial-insight-employee`.

The user prefers short shell entry commands only. Do not paste long scripts or large code blocks in chat. Commit scripts and docs directly to GitHub.

## Interaction protocol

1. Assistant edits GitHub directly.
2. User runs the short module entry command on the server.
3. User pastes output.
4. Assistant verifies GitHub evidence files.
5. Only then can the module be marked accepted.

## Evidence protocol

Use GitHub evidence as the source of truth. Do not infer acceptance from local chat text if evidence was not pushed.

For each module, verify:

- `module` matches the expected module.
- `status` is `passed`.
- `test_exit_code` is `0`.
- `expected_unit_test_count` matches the expected count.
- module-specific feature flag is true.
- `file_written` is false unless explicitly intended.
- execution report confirms passed status.

## Engineering standards

- Layered and decoupled modules.
- Configuration separated through environment flags.
- Safe by default and disabled by default.
- No external service calls unless explicitly designed.
- No release publish from rebuild modules.
- No default request behavior changes from local visibility helpers.
- Keep one mainline commercial version.
- Use small isolated helpers under `app/mNN.py` for rebuild increments.
- Keep tests deterministic and fast.
- Use compact writers and short docs.
- Avoid large monolithic files.
- Prefer reusable commercial architecture over demo-only code.

## Script conventions

Use `scripts/jobNN.sh` for runners when possible. Avoid long or risky script names. Do not use raw `set -e`. Each runner should cd to `${PRODUCT_DIR:-$HOME/projects/oris-commercial-insight-employee}`, run unittest discovery, export `TEST_RC`, run the writer, and exit with `TEST_RC`.

## Documentation conventions

Short rebuild docs live under `docs/rebuild/MNN.md`. Accepted status docs live under `docs/status/MODULES_1_NN_ACCEPTED.md`. Handoff and startup docs live under `docs/handoff/`.
