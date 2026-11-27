# AXIOM Research Engine

**Evidence before conclusions.**

Public bootstrap in progress: the complete Python mathematical and offline research engine, test suite, campaign plans and hosted qualification entry points from v0.4.0 have been imported with verified original Git blob hashes. This is a staged import, not yet the full v0.4.0 publication candidate.

## Run the engine

Requires Python 3.11+; no runtime dependencies. The recommended hosted path is the Actions tab: Free-tier qualification runs the unit tests and exact campaign; Bounded research regression provides manually selected fixed replay profiles.

    python scripts/hosted.py --profile quick
    python scripts/hosted.py --profile loop-replay

The adaptive loop uses trusted, declarative strategies, matched nonadaptive controls, exact finite oracles and deterministic evidence replay. It makes no model calls and executes no generated code. Its subprocesses are not a hardened sandbox.

## Hosting and safety

Standard public GitHub-hosted runners only, bounded software regression and reproducibility jobs; no self-hosted infrastructure, paid inference, cron, routine artifact uploads or automatic releases. Account spending controls and administration settings require owner review.

No general SAT speedup or P=NP proof is claimed. The local dashboard, static portal, full documentation and evidence import remain pending. See issue #1 for publication review, licensing, governance and backlog. Public visibility is not a license grant; the software license is pending owner approval. Do not submit confidential or employer-owned material.
