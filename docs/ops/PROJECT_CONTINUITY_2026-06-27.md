# Project Continuity Archive - 2026-06-27

This document is the handoff archive for continuing the ORIS Commercial Insight Employee commercialisation workflow in a new ChatGPT conversation without relying on the previous chat memory.

## 1. Project Identity

- Repository: `ShanGouXueHui/oris-commercial-insight-employee`
- Main branch: `main`
- Server project path: `/home/admin/projects/oris-commercial-insight-employee`
- Project mode: commercial, general-purpose, production-oriented version.
- Current narrow task family: OpenClaw专项研究 / ORIS commercial insight employee OTA rebuild and commercialisation.
- User interaction language: Chinese by default, concise, operational, no long theoretical replies unless explicitly requested.

## 2. Operating Environment

### 2.1 Runtime and OTA

The server-side OTA loop is expected to run every minute through cron:

```bash
cd /home/admin/projects/oris-commercial-insight-employee && bash unified-OTA-entry.sh >> reports/ota/unified_ota_loop.log 2>&1
```

The OTA loop pulls `origin/main`, runs tests, executes `scripts/w70.py`, writes evidence files, commits them, and pushes back to GitHub.

Current OTA staged evidence paths are expected under:

- `reports/testing/`
- `reports/execution/`
- `reports/ota/`

The OTA shell stages evidence with `git add reports/testing reports/execution reports/ota "$log" "$state"` and typically commits with message `Add OTA execution evidence`.

### 2.2 Current OTA Control Files

- Module writer: `scripts/w70.py`
- Instruction trigger: `ops/ota/next_instruction.json`
- Latest evidence pointer: `reports/testing/latest_test_result.json`
- Per-module evidence: `reports/testing/insight_rebuild_module_<N>_test_result.json`
- Per-module execution report: `reports/execution/insight_rebuild_module_<N>_execution_report.md`

### 2.3 OTA Execution Rule

Do not jump multiple instruction sequences expecting multiple executions. The server executes one OTA cycle per new `instruction_seq`. The correct cycle is:

1. Verify latest evidence for the current pending module.
2. Fetch module-specific JSON and execution report.
3. If passed, accept that module.
4. Update `scripts/w70.py` to the next module number.
5. Increment `ops/ota/next_instruction.json` by exactly `+1`.
6. Wait/poll for evidence commit to return.
7. Repeat.

## 3. Interaction Habits and Constraints

- The assistant should directly modify GitHub when asked; do not ask the user to perform copy-paste file edits unless connector write is blocked.
- Logs and execution state should be read from GitHub files and commits, not from long terminal outputs pasted into chat.
- When human execution is necessary, provide only a short, single-purpose command block. Do not print long scripts in the chat.
- Long design notes, memory, prompts, and progress logs must be written to GitHub docs instead of kept only in the chat.
- Keep final chat responses short because long messages can timeout.
- Prefer evidence-backed status: cite GitHub evidence files or commits when reporting progress.

## 4. Engineering Design Memory

### 4.1 Mainline Only

Production code must have one mainline logic path. Avoid compatibility branches, old code paths, duplicated functions, duplicated variables, and hidden fallback behavior. If legacy behavior must be retained, archive it in GitHub documentation or backup files, but do not leave it active in production execution paths.

### 4.2 Architecture Principles

- Layered architecture: separate domain logic, application orchestration, infrastructure adapters, configuration, and presentation/API/UI.
- Configuration separation: no deployment-specific secrets or constants in production code. Use environment variables or deployment configuration.
- Single source of truth: avoid multiple active definitions for the same concept.
- Explicit evidence: every OTA or release step must produce machine-readable evidence and a human-readable execution report.
- Commercial readiness: design for tenant isolation, auditability, operability, predictable costs, and replaceable infrastructure.
- Backup is allowed; active production logic should remain single-path.

### 4.3 External Best-Practice Anchors

Future architecture work should reference and adapt recognized practices rather than only reacting to chat requests:

- Twelve-Factor App: config separated from code; build/release/run stages are separated.
- AWS Well-Architected: architecture should be evaluated for operational excellence, security, reliability, performance, cost, and sustainability.
- Google Cloud Well-Architected / Architecture Framework: emphasize operational excellence, security/privacy/compliance, reliability, cost optimization, performance, and sustainability.
- OWASP Secure Coding Practices: apply secure coding by default and verify inputs, authentication/authorization, error handling, logging, data protection, and dependency/security posture.

## 5. Known Business/Product Direction

The project should move toward a commercial, general-purpose ORIS insight employee product. It should avoid one-off patching and should converge toward a systematically designed product architecture:

- Clear product modules and responsibilities.
- Stable OTA/release pipeline.
- Evidence-driven testing and deployment.
- Production-grade observability and audit trail.
- Security by design.
- No accidental external calls during baseline/evidence modules.
- No release publication or default behavior change unless explicitly planned and evidenced.

## 6. Current Status Summary

As of this archive, Module 102 has been accepted and Module 103 has been published for OTA execution. See `docs/ops/OTA_TASK_PROGRESS.md` for the exact task state.

## 7. Open Work / Not Yet Done

- Continue OTA sequence from Module 103 evidence verification.
- Replace baseline-only module progression with meaningful commercial product modules once safety checker and repository write constraints permit.
- Review existing production code for duplicate definitions, duplicate variables, compatibility branches, old code paths, and inactive legacy logic.
- Create a clean architecture map for product modules and commercial roadmap.
- Strengthen test suite beyond the current 380-test baseline when product code changes are allowed.
- Build production design around explicit tenant, configuration, data, audit, security, and observability boundaries.

## 8. Assistant Behavior for Next Conversation

The next assistant should:

- Read this archive and the progress/guardrail docs first.
- Continue by checking latest GitHub evidence for Module 103.
- Avoid printing long code or long commands in chat.
- Use GitHub connector operations as the primary execution channel.
- Keep chat responses short and evidence-based.
