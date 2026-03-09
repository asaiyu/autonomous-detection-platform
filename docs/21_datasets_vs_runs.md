# Datasets vs Runs

This is a core architecture decision to make coverage comparisons valid and reproducible.

## Attack Dataset (stable)
A dataset is a **frozen, versioned** collection of:
- canonical events (and optional raw events)
- findings (ground truth)
- metadata (target fingerprint, config hash, seed)

Datasets are **immutable** once created.
Updates create a new dataset version.

Examples:
- juice_shop_local_v1
- synth_windows_priv_esc_v2

## Attack Run (ephemeral)
A run is an execution of an attack source (Shannon or synthetic).
Runs may:
- succeed, fail, or be partial
- create or attach to a dataset
- produce operational logs

## Why this matters
Coverage must be compared on the same dataset:

coverage(dataset D, ruleset R1) vs coverage(dataset D, ruleset R2)

This enables honest "before → after" coverage improvement claims.
