# Tenant Guardrail Bridge Guide

Date: 2026-06-25

## Purpose

This guide explains how tenant entitlements are integrated with commercial guardrails without introducing real billing, payment processing, or provider calls.

## Evaluation Order

1. Evaluate existing commercial guardrails first.
2. If the commercial guardrail blocks, stop and return the commercial reason.
3. If the path is exempt, skip tenant entitlement checks.
4. Evaluate tenant entitlement only after the commercial guardrail allows the request.
5. In observe mode, entitlement failures are reported but do not block.
6. In blocking mode, missing entitlement returns `403` and quota exhaustion returns `429`.

## Safety Rules

- No payment provider is integrated.
- No payment processing is enabled.
- No billing API is called.
- No live external action is performed.
- Tenant checks are local and deterministic.
- Existing `evaluate_guardrails` signature remains unchanged.

## Current Integration Shape

Module 22 adds a bridge module instead of mutating the existing middleware path directly. This keeps compatibility with existing Module 10 guardrail tests and makes the tenant bridge independently testable before API-level middleware integration.
