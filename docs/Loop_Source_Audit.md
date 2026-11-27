# AXIOM / upstream research-loop audit

2026-11-27 | Read-only source inspection | Working identity, not a released product

## Scope and evidence
Reviewed the public Blankline repository `blankline-org/extrapolation-n26` documentation, the scorer and runner, memory store, archive and evolutionary search source, configuration, problem checker, edit mechanism and relevant experimental reports. Source URLs below point to main; blob hashes identify inspected versions. The supplied video transcript is a secondary account, not evidence of correctness. No upstream code was executed or copied into AXIOM; source-derived findings are distinguished from proposed AXIOM designs. Some large files were examined in selected excerpts rather than audited line by line. This is not a penetration test or a fresh audit of every earlier product repository.

## Findings and dispositions
| Component / evidence | What the upstream system does | AXIOM decision |
|---|---|---|
| `evolve.mjs` | Population search, elite parents, exploration probability, scratchpad refinements, serial warmup and bounded continuations. Comments record parallel workers inventing prior failures on empty logs. Prompt contains unconditional tool-call instructions despite tools defaulting off. | Use structured plans with immutable observation IDs. No fabricated history; explicit enabled-capability list. Deterministic serial policy first; later parallel read-only snapshot + coordinator CAS. Bound actual evaluations, retries, time and costs, not just outer attempts. |
| `map-elites.mjs` | Diverse elite selection and random sampling, including `Math.random()`. | Diversity by explicit, versioned strategy features; seed PRNG; record exact sequence. Distinguish code novelty from mathematical novelty. |
| `archive.mjs` | JSON file archive rewrite; code tags, failure classification, parent and assignment summaries. `evolve.mjs` notes clobbering when simultaneous runs share paths. | Unique run directories, SQLite transactional append-only ledger, content-addressed immutable-by-convention evidence. No implicit resume. Durable leases/outbox and external anchor are future work. |
| `lesson-store.mjs` | PGlite + pgvector; hashed bag-of-words placeholder embeddings; scoped metadata, active lessons by default, cosine dedup, outcome counts. SQL selects by user and active status but not `scope`; size/dump are not user-scoped. Dedup increments usage rather than establishing mathematical equivalence. | Evidence-based status and project/campaign scoping enforced on every query; separate literature, hypothesis, failure and proof stores. Similarity is retrieval only, not identity/proof. No automatic promotion of model text. |
| `scorer.mjs` | Syntax check, temp candidate source, Node child with heap limit, output collection, wall timeout and direct child kill. Spawn options do not override environment; stdout/stderr accumulated without byte cap. Output JSON accepted when score is finite; exit code not checked in close handler. | Never run generated source until real isolation and independent verifier. v0.3 evaluates only finite declarative strategy records. Production requires restricted credentials, resource/process-tree bounds, output cap, exit-code checks and no trusted output metrics from untrusted code. |
| `score-run.mjs` | Dynamically imports candidate into same process as `problem.verify`. It passes params and evaluates result afterward. | Candidate must not share verifier process, filesystem or credentials. In v0.3 trusted interpreter runs in child; controller computes reference counts independently. This remains a local process boundary, not sandbox. |
| `problems.mjs` | Circle count, finite positive radii, walls and pair gaps with EPS=1e-9; valid score is radius sum. Diagnostic feedback and solution seed. | Exact arithmetic for our mathematical task. Candidate outputs count, oracle decides validity. Separate correctness gate from comparable objective. Keep holdout selection independent and record all errors. |
| `edits.mjs` | Search/replace edits, ambiguity handling on exact path; whitespace fallback returns first trimmed-line match. Partial successful edits remain applied. | For future code mutations, verify parent hash, unique match across all fallback matches, reject partial application, record patch and resulting hash; isolated execution only. |
| `config.mjs` / `provider.mjs` (selected excerpts) | Provider/backend configuration, key preflight, CLI opt-in permission bypass, job/stream options, retries and continuation limits. | Broker-only model API; keys never enter worker environment. No permission bypass. Budget reservation before calls, timeouts and idempotency. Archive structured claims and provider metadata, not private deliberation. |
| Cold control / independent-task report | 91 cold searches of 600 s; zero reached target structure; one search method and budget. Independent-task memory result did not separate. | Match attempt count, objective, fixture suite and initial baseline; disclose differing compute cost. Multiple prespecified seeds and holdout; no general causal claim from a single run. |

## Mathematical limitations of upstream experiment
Contact-graph non-isomorphism under the stated tolerance follows from different degree sequences. It does not prove absence of training-data recall or that AI is necessary to find a shape. The primary checker uses floating point and tolerances; it is not an exact symbolic proof of feasibility. The published best includes a human-authored LP step and model-free sweep. The research contribution is one observed distinct configuration with archived history, not a universal discovery method. We do not adopt the promotional or unrelated claims in the transcript.

## Critical lessons for our loop
1. Make the referee before the proposer; holdout correctness and independent reference evaluation must dominate optimization.
2. Save observations before distilling lessons. Each machine fact has a specific run, input and receipt; any proposed generalization is a separate hypothesis.
3. Avoid a single scalar combining correctness, novelty, and speed. Optimize cost only after exact agreement; use novelty as exploration policy; maintain formal proofs separately.
4. A promising local recurrence may plateau. Periodically select an approach far from the incumbent and the tried set; record the policy and failure reasons.
5. Distinguish attempts, refinements, verifier calls, external API tokens, actual CPU and total cost. Do not report outer-loop count as total work.
6. A candidate cannot self-certify. For arbitrary future code use a separately isolated interpreter/worker, independently measured counters and a verifier in a different trust domain.
7. Separate observed data, retrieved literature and machine-derived hypotheses. Record null results and counterexamples. Never promote a generated explanation simply because a numerical score improved.

## Exact source index
Base: `https://github.com/blankline-org/extrapolation-n26/blob/main/`

| Path | Inspected blob SHA (when recorded) |
|---|---|
| README.md | 64ce0f1daa5b4003f1c194d070e22fe7ed1c828b |
| loop/README.md | f2549e95aaf5c3391d64b61f8e6e4230fe464373 |
| loop/src/evolve.mjs | 143a36eb06a9c6429dbe66ce0b0a2c7fef2057f8 |
| loop/src/scorer.mjs | 75e9f5df04f9a8a4f4b4544feb7b62b5d015ef8c |
| loop/src/score-run.mjs | ba3587e1ce0c707d9aa5f983a295cb070961b6fa |
| loop/src/lesson-store.mjs | 21509513430f8268a57e1c02e35e9573c03fac16 |
| loop/src/map-elites.mjs | 6b3a08a44ff96942be205e1a6bae20ecacd13c75 |
| loop/src/archive.mjs | 53ad01180b6d8c885b0322269615be7959cb11df |
| loop/src/problems.mjs | 4f9b858edd481ea8fca962b4d19262adeb0522c7 |
| loop/src/edits.mjs | 6a4c4e23795594ee5d922f8c835f92e240bd9e07 |
| verify.mjs | 9c356e91c34d4a9b5d76c4b5d0b48773c2666f06 |
| contact-graph.mjs | aa501737ea8a8c98c2bb570ed1016dec8a07d53d |
| control/README.md | 122cc6a630b26b05e5d755465c2725ab5efcdf5f |
| results/report-independent.md | e33ba80efd52976f328f50dffe3dd950a066fce4 |

Reference: https://blankline.org/research/extrapolation-under-an-exact-verifier
