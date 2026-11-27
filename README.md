# AXIOM Research Engine

**Evidence before conclusions.**

Public bootstrap in progress. The exact mathematical core from the v0.4.0 publication candidate has been imported, with original Git blob hashes verified. This is a staged subset, not the full v0.4.0 release.

## Run the mathematical core

Requires Python 3.11 or newer. No third-party dependencies.

    python -m unittest discover -s tests -v

The initial imported suite tests exact SAT counting, truncated polynomial permanents, signed XOR walk aggregation, modular division and CRT reconstruction. Finite tests are not proofs of general correctness or better asymptotic complexity.

## Hosting and safety

Use standard GitHub-hosted runners for bounded software regression and reproducibility only. No self-hosted servers, paid inference, scheduled research, automatic publishing or routine artifact uploads. Account billing and repository administration settings require owner review.

The remaining application, research-loop implementation, documentation, historical evidence and licensing decision are tracked in issue #1. Do not submit confidential or employer-owned material. Public visibility is not an open-source license grant; licensing is pending explicit owner approval.
