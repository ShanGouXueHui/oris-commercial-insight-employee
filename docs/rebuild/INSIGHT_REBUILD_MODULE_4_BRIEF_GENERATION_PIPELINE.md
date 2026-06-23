# Insight Rebuild Module 4 - Brief Generation Pipeline

## Objective

Transform validated ingestion results into a deterministic, evidence-linked executive brief.

## What This Module Adds

- Generated brief section contract.
- Risk and scenario generation contracts.
- Evidence-linked section generation for all required analytical lenses.
- Confidence calculation based on evidence coverage and ingestion validity.
- Limitations propagation from ingestion validation errors.
- Serializable sample brief output.

## Runtime v2 Alignment

The pipeline is deterministic and can be executed by the Runtime v2 worker/executor in later orchestration modules. Evidence references remain explicit so the Runtime v2 evidence publisher can index generated outputs.

## Next Module

Insight Rebuild Module 5: Quality Gates and Limitations.
