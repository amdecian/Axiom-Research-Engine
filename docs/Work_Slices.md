> Historical foundation retained; `Hosted_Engineering_Contract.md` supersedes conflicting hosting and publication requirements.

# Implementation work slices

All 48 are proposed production work; the starter partially addresses S001–S004, S041 and S043. Each slice must deliver a reviewed commit, tests and an evidence receipt. Dependencies are prerequisites, not a duration estimate. A gate passes only after every listed slice and its negative controls are reviewed.

## G1 — Evidence foundation (S001–S008)

| ID / depends | Engineering deliverable | Acceptance test |
|---|---|---|
| S001 / — | Repository scaffolding, architecture decision records, versioning and private default | Clean checkout; offline build, test and no credential in history. |
| S002 / S001 | Validate versioned campaign, job, receipt and lesson schemas | Reject malformed, oversized, unknown-version and invalid rational/decimal fields. |
| S003 / S002 | Transactional append-only event ledger and projection | Replay yields same state; tampering and duplicate events detected. |
| S004 / S002 | SAT exhaustive and permanent-polynomial exact oracles | Match hand examples, signed rational controls, empty CNF/clause, free variables. |
| S005 / S003 | Content-addressed artifact ingestion and quotas | Corrupted blob, path traversal, symlink and duplicate digest cases rejected. |
| S006 / S003,S005 | Signed verifier receipt and externally anchored checkpoints | Recomputed hash without trusted signature is rejected. |
| S007 / S004,S005 | Public fixture registry and separate private holdout commitments | Seeded reproducibility; candidate cannot access expected answers. |
| S008 / S001–S007 | Offline replay and evidence export | Clean environment reproduces exact outputs; timing variance separately labeled. |

## G2 — Isolation and orchestration (S009–S016)

| ID / depends | Engineering deliverable | Acceptance test |
|---|---|---|
| S009 / S008 | Campaign state machine and role policy | Illegal transition, unauthorized start and stale approval denied. |
| S010 / S009 | Durable queue, leases, idempotent receipts and outbox | Duplicate deliveries do not duplicate execution result or cost charge. |
| S011 / S010 | Budget reservation / reconciliation | Parallel jobs cannot overspend; caps stop dispatch. |
| S012 / S010 | Linux guest runner with pinned image and scratch directory | Worker cannot read host files, keys, verifier or other jobs. |
| S013 / S012 | External CPU/RAM/PID/time/output limits | Fork bomb, runaway loop, output flood terminated and classified. |
| S014 / S012 | Separate referee worker, private mounts and egress policy | Candidate cannot see holdouts; forged receipts fail. |
| S015 / S011–S014 | Pause, emergency stop and crash recovery | Kill descendant processes, revoke leases, no automatic resume. |
| S016 / S009–S015 | Security qualification and recovery drill | Negative isolation tests, budget crash test, documented approval. |

## G3 — Agent and memory loop (S017–S024)

| ID / depends | Engineering deliverable | Acceptance test |
|---|---|---|
| S017 / S016 | Provider-neutral gateway and offline mock | No live calls when disabled; key never enters prompt/worker. |
| S018 / S017 | Prompt/response schema and source citation discipline | Nonexistent evidence IDs, unsafe scope and unknown strategy rejected. |
| S019 / S018 | Proposer and bounded portfolio scheduler | Generates distinct typed hypotheses; maximum attempts enforced. |
| S020 / S019 | Independent critic and counterexample queue | Known omitted-H and false symmetry claims trigger adversarial test. |
| S021 / S018 | Immutable memory snapshots and retrieval | Return only approved scoped records with source hashes. |
| S022 / S021,S014 | Review queue, provenance validation, supersession | Phantom prior attempt and stale concurrent revision rejected. |
| S023 / S019–S022 | Plateau detection, diverse approach selection, budget-aware stop | Simulated repeated failures stop; alternative technique slot recorded. |
| S024 / S023 | Memory-on/off/shuffled and conventional controls | Matched budgets, seeds and all failed attempts archived. |

## G4 — Mathematical workstream (S025–S032)

| ID / depends | Engineering deliverable | Acceptance test |
|---|---|---|
| S025 / S008 | Import R1–R9 archives on receipt; validate checksums and manifest | Replay early pilot and coefficient audit; label nonreproduced records. |
| S026 / S025 | Rank-one and two-correction exact adapter | Check mixed terms, signed fixtures and omission counterexamples. |
| S027 / S026 | Cut-rank overlap certificates and scheduling diagnostics | Reproduce low overlap and forced overlap on source families. |
| S028 / S027 | Reproduce full two-crossing Fourier/displacement contraction | Agree with independent small controls and five-size results at fixed precision. |
| S029 / S028 | Exact p-adic normalization, guard precision and integer recurrence | Handle 5408/11 nonunit witness without invalid modular inverse. |
| S030 / S029 | Alternative shared-interior representation, measure precision growth | Compare against known ten digits; attempt eleven only within approved limits; count all work. |
| S031 / S026,S029 | Higher Taylor/crossing orders and asymmetry suite | Independent oracle agreement on signed, combined and higher-order inputs. |
| S032 / S031 | End-to-end CNF-to-permanent interpolation and final count recovery | Exact counts match exhaustive SAT; complete bit/time accounting, CRT conditions verified. |

## G5 — Proof and complexity (S033–S040)

| ID / depends | Engineering deliverable | Acceptance test |
|---|---|---|
| S033 / S008 | Formal statement and assumption registry | Scope and quantifiers included in versioned statement hash. |
| S034 / S033,S014 | Pinned Lean proof checker, dependency/axiom policy | Reject `sorry`, unapproved axioms/imports and theorem statement drift. |
| S035 / S034 | Formalize simple permanent expansion/degree-two identity | Kernel receipt matches reviewed theorem statement. |
| S036 / S035,S026 | Formalize low-rank completion and retirement invariants | Explicit domain assumptions; counterexample tests challenge weakened hypotheses. |
| S037 / S030,S033 | Complexity instrumentation by phase and bit size | Detect preprocessing, integer growth and storage omitted from score. |
| S038 / S031,S037 | Parameterized bound for shared computation | State n,N,h,rank,width,k, bit cost; stress worst-case families. |
| S039 / S032,S038 | General SAT reduction accounting and baseline bound comparison | Includes all nodes/orders/sparsification/recovery; no empirical proof claims. |
| S040 / S034–S039 | Independent proof review and negative-result report | Reproducible theorem checks or explicitly open obligations; no forced claim. |

## G6 — Product, UI and controlled pilot (S041–S048)

| ID / depends | Engineering deliverable | Acceptance test |
|---|---|---|
| S041 / S003 | Overview, campaign and experiment browser | Live read model, exact evidence, accessible navigation and no fabricated metrics. |
| S042 / S009,S015 | Campaign builder and live controls | Dry run, hash approval, pause/stop visible and operational. |
| S043 / S022,S041 | Notebook and verification detail | Filter grades, inspect receipts and explicit approval, no silent history edits. |
| S044 / S034,S037 | Proof workspace and benchmark explorer | Show assumptions, checker status, matched workloads and comparable metrics. |
| S045 / S016,S042 | Settings, roles, privacy, provider and worker health | Default OFF, opt-in policy, auth/CSRF and stop test. |
| S046 / S008,S043 | Research graph, reproducible report and export | Trace assertion to archived evidence; private data excluded from public export. |
| S047 / S045,S046 | Packaging, signing, SBOM, CI and backup/restore | Signed reproducible manifest, clean install/uninstall; no service starts silently. |
| S048 / G1–G5,S047 | Controlled pilot campaign and readiness decision | Independent review, budget reconciliation, negative controls, reproducible output and human go/no-go. |

### Next build order

S001–S004 harden the supplied starter before S005–S008. Then isolate before introducing model execution. In parallel after S008, ingest research archives (S025) and define formal statement registry (S033). S030 and S032 are the principal scientific objectives. G6 is usable progressively; a production start control is never enabled before G2. No commitment to an autonomous overnight run is part of this handoff.
