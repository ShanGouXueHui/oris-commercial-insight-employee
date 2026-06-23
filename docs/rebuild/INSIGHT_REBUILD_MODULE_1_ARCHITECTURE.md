# Insight Rebuild Module 1 - Architecture Alignment with Runtime v2

## Objective

Rebuild the commercial insight employee on top of the accepted ORIS Runtime v2 substrate instead of extending the old interactive stub blindly.

## Current Product Baseline

The product repository contains a Phase 0 FastAPI service with Pydantic models and deterministic executive brief generation. Module 1 preserves that baseline and adds the rebuild alignment layer.

## Runtime v2 Capabilities To Use

- state machine
- persistent run store
- worker loop
- safe executor adapter
- GitHub evidence publisher
- approval gate
- end-to-end acceptance harness

## Rebuild Sequence

1. Architecture alignment.
2. Domain contracts.
3. Evidence ingestion.
4. Brief generation pipeline.
5. Quality gates and limitations.
6. API surface and acceptance.

## Boundary

This module does not add business-specific insight logic yet. It establishes the product-side rebuild plan and verifies that the product is allowed to mutate after Runtime v2 final acceptance.
