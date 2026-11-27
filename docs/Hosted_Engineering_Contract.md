# AXIOM v0.4 — Hosted engineering contract

**Status:** implementation candidate, 2026-11-27. This contract supersedes conflicting deployment guidance in the historical engineering and loop specifications. Existing local APIs remain optional development tools. Target: $0 additional recurring infrastructure cost within GitHub Free allowances, no maintained server, no paid AI inference, no dedicated worker hardware. No account-level billing guarantee.

## Architecture and trust boundaries

```text
Human researcher / ChatGPT (manual)
           |
  Reviewed issue + source branch
           |
  Public GitHub repository (main protected by maintainer)
           |                              |
  Finite hosted qualification       Versioned notebook
  (read-only, no secrets)           (JSON, evidence hashes)
           |                              |
  Trusted fixture oracle            Deterministic portal build
  (separate algorithms,             main:/docs, GitHub Pages
   not independent security role)         |
           |                         Read-only browser UI
  Logs + summary -> human review -> evidence PR
```

No dynamic API server on Pages. No browser token. No cloud SQLite persistence; SQLite is temporary inside a developer job, exact output may be exported as reviewed evidence. CI is not a distributed batch discovery platform. Candidate code in public PRs executes on ephemeral GitHub runners and has no intended secrets or write permissions. The public PR can change its own test code: a pass is not independent adjudication. Require maintainer review of verifier, workflow, notebook and mathematical specification changes. Neither subprocess nor GitHub-hosted ephemeral VM provides a security boundary between arbitrary candidate code and a verifier in the same job. AI-generated execution remains disabled. Distinct verifier identity, holdout secrecy, signatures and hardened guest isolation remain future research gates.

## Contract register

| ID | Requirement | Implemented / acceptance |
|---|---|---|
| HOST-01 | Standard public hosted runners only | Workflow labels fixed; job guard and Python preflight reject private and non-hosted event. Remote labels and quotas must be checked. |
| HOST-02 | Finite qualification | Only `quick`, `portal-check`, `loop-replay`, `pattern-regression` registered; manual extended jobs only. No arbitrary commands, schedules or run chains. |
| HOST-03 | Resource controls | 10-minute workflow ceiling; 30–300 s child timeout; Linux 3 GiB address-space / 64 MiB per-file / CPU limits per process; 512 MiB free-disk preflight; max-parallel 2 per workflow matrix. No total RSS, disk or account concurrency enforcement. Windows/macOS rely on job limits and trusted code, not process-tree containment. |
| HOST-04 | No metered integrations | No provider API calls, larger runners, routine artifact/cache upload, external database or self-hosted worker. Set owner budgets manually. Pages built-in managed deployment may use GitHub-managed artifacts. |
| HOST-05 | Evidence retention | Logs and summaries are transient, not durable evidence. Maintainer reviews exact source and output, commits compact approved evidence; no write token in testing jobs. |
| NOTE-01 | Git-backed memory | Strict JSON notebook records, file ID and evidence SHA-256; only evidence-directory filenames, capped sizes, checked at portal build. No arbitrary note execution. |
| NOTE-02 | Claim status | `finite_pass`, `counterexample`, `open`; `publication_pending` until owner reviews. Hash is consistency, not signer identity or mathematical proof. |
| UI-01 | Static portal | Self-contained HTML, offline search, dark/light, filtered CSV, no API credentials or external requests; deterministic build ≤1 MiB; CI freshness check. |
| GOV-01 | Publication | Independent ownership, review all public files, approve license, keep historical/private material outside repo. No auto-push or auto-release. |
| GOV-02 | GitHub operations | Explicit owner/repo and visibility, public acknowledgement, batch cap 25, stop on API errors. Manual ruleset and security settings. |
| MATH-01 | Exact verification | Compare signed weighted XOR walk aggregation with explicit injection, retain failures, fixed bounded tests. |
| MATH-02 | Arithmetic | Known-divisible modular quotient requires extra modulus; CRT requires pairwise coprime moduli product >2^n and valid range. Does not implement modular SAT reduction. |
| MATH-03 | Proof and complexity | Finite tests cannot promote a theorem. Lean statements, axiom checks, asymptotic analysis remain required. |

### Free resource envelope

Public GitHub standard Linux x64 and ARM runners: documented 4 CPUs, 16 GB RAM, 14 GB SSD; macOS ARM has 3 CPUs / 7 GB RAM. Standard job maximum 6 hours; Free concurrency 20 with separate macOS cap. Package uses much smaller limits. Free artifact/cache allowances remain separate, and larger runners are billed even for public repos. Avoid assuming an organization has free personal Codespaces hours or that zero budget applies to every product; review the account billing dashboard. GitHub's usage policy governs whether an experiment may use Actions independent of time and cost. The only default hosted activity is actual project software qualification. No chaining jobs to evade usage or service limits.

Sources reviewed 2026-11-27:
- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/reference/limits
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.github.com/en/site-policy/acceptable-use-policies/github-acceptable-use-policies

## Engineering workflow

1. Write a testable research question and exact acceptance conditions in an issue.
2. Implement a small reviewed algorithm change, not a live model execution. Pin input fixture, seed and source; include a counterexample or independent oracle.
3. PR checks exercise known source; manual extended replay for changed loop code. Do not promote results until independently reviewed. Negative results remain visible.
4. Append reviewed notebook JSON and compact evidence; regenerate portal; review and merge via protected main.
5. When rights and technical qualification permit, publish exact source and evidence via an approved GitHub Release. Attestation, SBOM, immutable release and native signing are separate future slices. No release workflow included to avoid accidental write privileges.

## Research program

Preserve original SAT/permanent algorithms and exact local oracles. New `axiom/patterns.py` provides bounded reference aggregation and arithmetic; see `docs/Scientific_Program.md`. It is not a proof of improvement and does not import R1–R9 executable archives. All 124 engineering and 20 scientific slices remain open; implementation evidence informs closure, but only maintainers close after acceptance. Original paper and concept artwork remain in review-only companion. New 0.4 replay is tied to current Python sources; historical evidence requires original source.

## Wireframes

`docs/index.html` is the working static portal, not a mock live server. Overview: version, exact replay count, backlog counts, strategy comparison. Notebook: searchable finite passes, counterexamples and open claims with evidence hashes. Experiments: matched control and attempt history. Work slices: filter by ID/area, CSV export. Hosting: configured source policy versus pending manual controls. Future live campaign controls, provider configuration, formal proof dashboard and independent verifier are not present. No misleading active execution indicator.

The [dual-repository disclosure boundary](Disclosure_Boundary.md) adds S113–S124 and supersedes conflicting research storage guidance. Public CI uses synthetic data only.
