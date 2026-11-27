# AXIOM Research Engine — v0.4.0 publication candidate

**Evidence before conclusions.**

GitHub-hosted mathematical research software: exact SAT counting, structured permanents, weighted XOR walk aggregation, modular arithmetic and a finite adaptive strategy loop. The public bootstrap is in progress; the core engine, tests, static research portal, notebook and work-slice manifests have been imported. This is not a claim of general SAT improvement, P=NP, or a formally verified autonomous research system.

## Hosted qualification

- [Cross-platform core qualification passed](https://github.com/amdecian/Axiom-Research-Engine/actions/runs/46065480354) on Windows, macOS, Linux x64 and Linux ARM64.
- [Actions](https://github.com/amdecian/Axiom-Research-Engine/actions): Free-tier qualification checks the engine and generated portal; Bounded research regression is a manual finite replay.
- [Research portal source](docs/index.html): enable GitHub Pages from main:/docs to serve this static application.
- [Hosted engineering contract](docs/Hosted_Engineering_Contract.md) and [scientific program](docs/Scientific_Program.md).
- [Engineering backlog](research/backlog.json): S001–S112; [scientific backlog](research/scientific-backlog.json): R10–R29.
- [Evidence](evidence/) and [notebook](research/notebook/) preserve finite results and negative controls. The imported evidence describes the original local candidate run; remote qualification is separately referenced above.

## Reproduce

Python 3.11+; no third-party runtime dependencies.

    python scripts/hosted.py --profile quick
    python scripts/hosted.py --profile loop-replay
    python scripts/hosted.py --profile portal-check
    python scripts/backlog.py

## Publication and operational limits

Use standard public GitHub-hosted runners for finite project testing, qualification and reproducibility only. No paid inference, self-hosted servers, scheduled discovery or routine artifact uploads. Owner billing controls require verification. The optional localhost dashboard, historical engineering documents, three provisional branding concepts and capture script are now included. The original R1–R9 executable archives and original binary replay archive are not imported. The companion archive remains excluded. See [bootstrap checkpoint](docs/Bootstrap_Checkpoint.md), [original setup guide](docs/GitHub_Bootstrap.md) and [branding concepts](branding/README.md).

Public visibility is not a software license grant; licensing is pending owner approval. Do not submit confidential or employer-owned material. See [bootstrap issue #1](https://github.com/amdecian/Axiom-Research-Engine/issues/1).
