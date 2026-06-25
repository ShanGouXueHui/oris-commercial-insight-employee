# Tenant Usage Ledger Guide

Date: 2026-06-25

## Purpose

Module 24 adds a local deterministic tenant usage ledger. It records monthly request counts by tenant and can feed the entitlement evaluator without using external storage.

## Current Scope

- In-memory tenant usage counts.
- Monthly period keys such as `2026-06`.
- Usage snapshot support.
- Entitlement evaluation against current ledger usage.
- No middleware consumption behavior change in Module 24.

## Why This Is Separate From Middleware

Module 23 activated tenant middleware behind a flag. Module 24 adds the local usage ledger as a separate unit first so request-count behavior can be validated before middleware starts consuming tenant usage.

## Safety Rules

- No external storage is enabled.
- No live external action is performed.
- No production request-count behavior is changed in this module.
- Middleware integration should be handled by a later bounded module.
