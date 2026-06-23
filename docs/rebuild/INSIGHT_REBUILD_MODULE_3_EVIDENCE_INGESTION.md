# Insight Rebuild Module 3 - Evidence Ingestion

## Objective

Add deterministic product-side evidence ingestion on top of the Module 2 domain contracts.

## What This Module Adds

- Raw evidence document contract.
- Source normalization into domain source contracts.
- Claim normalization into evidence item contracts.
- Lens coverage calculation.
- Validation against domain quality gates.
- Serializable ingestion summary for future brief generation.

## Runtime v2 Alignment

This module remains deterministic and local. Later modules can execute ingestion through Runtime v2 worker/executor flows and publish evidence through the Runtime v2 evidence publisher.

## Next Module

Insight Rebuild Module 4: Brief Generation Pipeline.
