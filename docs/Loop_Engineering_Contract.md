> Historical v0.3 design. The v0.4 Hosted Engineering Contract supersedes conflicting deployment requirements.

# Research-loop engineering contract / v0.3.0

## Product and deployment
AXIOM is a local-first mathematical research workstation. Keep the established independent brand until explicitly chosen. First research program: exact SAT counting and shared arithmetic for structured permanents. Local use needs no subscription, API key, or network. Managed control plane, enterprise multi-tenant operation and provider integration are target architecture, not implemented. Do not use enterprise work credentials or employer-controlled production runners for this personal research unless separately authorized.

## Implemented data-only discovery loop
```
plan -> approve digest -> generate fixed train/holdout suites
     -> same baseline + seeded order (24 strategy options)
     -> adaptive arm                  blind arm
        mutate / explore              seeded nonadaptive
        -> trusted subprocess         -> trusted subprocess
        -> independent oracle         -> independent oracle
        -> receipt, observed history  -> receipt, observed history
        -> repeat within budget       -> repeat within budget
     -> freeze both training winners -> evaluate holdout once each
     -> append terminal event -> report -> independent local replay
```
The search space consists of three branch policies (shortest clause, total frequency, polarity balance), unit propagation on/off, decomposition on/off and memoization on/off. One kernel implements all 24 configurations. Exact answers are independently enumerated from assignments. Primary objective is the number of recursive requests on the fixed training suite; expanded states, cache hits and restriction literal visits are secondary counts. Worker time includes process startup and is diagnostic only. None is a proof of runtime speed or asymptotic complexity. `sat_oracle` is an exponential oracle for bounded test sizes, not a production SAT algorithm. Holdout filters exact serialized duplicate input pairs; it does not remove all equivalent formulas or conceal the fixture generator from a local operator. Both winners frozen before holdout evaluation. No result of the holdout may influence winner choice. Seeds and budget fixed in the approved plan. Adaptive and blind arms interleaved and do not share observations. Blind still uses the same trusted kernel and baseline; this measures adaptive selection against randomized nonadaptive selection, not an LLM memory benefit.

### Runtime contract
- `python -m axiom.loop plan <manifest>` validates strict `loop-1` fields, enumerates fixtures, prints exact source and dataset hashes, max evaluations and approval digest. No execution.
- `run <manifest> --approve-digest <digest> --out <new directory>` rechecks source and plan before starting. No reuse or overwrite of run directory. No network, provider, generated code, arbitrary import, scheduler, credential, or dynamic shell. Source hash covers Python module bytes, not the entire OS or build environment. Digest is a local confirmation, not authenticated authorization.
- `loop.started`, `loop.oracle`, `loop.attempt.started`, `loop.attempt.verified` / `loop.attempt.failed`, `loop.winner.frozen`, `loop.finished` are append-only event types. Full datasets and candidate outputs and receipts are stored as JSON blobs keyed by SHA-256. Hash chain is local tamper evidence; no external signature/anchor. `report.json` is derived presentation, not authoritative evidence. Oracle is computed in controller; worker is trusted, not a hardened sandbox. Timeout bounds subprocess call, campaign deadline checked before calls; bounded oracle work and cleanup can exceed nominal deadline. Keyboard interrupt stops foreground run; no daemon or automatic restart. Abrupt kill may leave incomplete ledger, replay refuses incomplete runs.
- `replay <run dir>` validates event hashes, original plan/source/fixture hashes, recomputes oracle, strategy sequence and candidate result counters, checks receipts and completed coverage. Current implementation does not prove authenticity, validate every possible event ordering, verify derived report bytes or replay elapsed time. Retain original source revision with each archive. Do not silently repair a corrupt ledger.

### Memory and evidence contract
Current loop's memory is verified observation history within its arm, archived to disk. Legacy manual notebook approval exists for offline fixture receipts. Cross-campaign retrieval, semantic memory, model-generated lesson promotion and authenticated reviewer identity are NOT implemented. Production lesson record: lesson_id, workspace_id, campaign_id, claim_kind, statement, assumptions, evidence_receipt_ids, source_hashes, verifier_identity, reviewer_identity, status, created_at, supersedes, scope, expiry/revocation, counterexample_refs. `finite_pass` only asserts enumerated cases; `counterexample` disproves the exact proposed universal statement if assumptions met; `derived` needs derivation; `formal_proof` requires checked theorem and axiom audit; complexity claim needs explicit cost model and proof. Text from literature, proposals, numerical observations and verified theorem records live in distinct namespaces. Only explicit review can promote a lesson; exact retractions propagate to dependent claims. Retrieval is bounded by workspace, permissions, problem family, status and source version, then ranked; returned evidence IDs must exist in the supplied snapshot. Empty retrieval must be represented as empty. Use serialized coordinator writes, not agents writing directly.

## Target service architecture and interfaces
| Service | API / durable contract | Trust and failure semantics |
|---|---|---|
| UI/CLI | create/preview/authorize/cancel campaign; read receipts and snapshots; export | Read-only by default; explicit confirmation for state changes; no secret display; no fake progress |
| Coordinator | campaign state planned -> approved -> running -> completed/stopped/failed; durable version/lease and idempotency token | Separate authenticated operator, expiry/revocation, transactional lease and outbox; no implicit restart |
| Provider broker | request_id, workspace, model alias/version, prompt template hash, evidence snapshot IDs, max input/output tokens, max cost, structured proposal response | Server-side credentials; no arbitrary tools; validate schema and cap response; record provider failure separately from algorithm failure; no hidden reasoning logs |
| Candidate store | parent hash, bounded JSON strategy or approved patch, problem family, intended theorem, assumptions, predicted test, expected metric | No execution from unvalidated data. Patch requires exact unique parent context. Reject incomplete edits |
| Worker queue | job id, attempt id, immutable input refs, deadline, cancellation epoch, image digest, CPU/RAM/disk/output caps | Separate ephemeral identity; no persistent credentials, host mounts, broad network, verifier tests. Kill entire process tree; quarantine partial output |
| Verifier | immutable data-only output ref, oracle version, fixture set digest, expected count/proof, signed receipt | Independently administered; no candidate source imported in verifier process. Verify counts before scoring; resource caps; no raw solver access to hidden holdout |
| Evidence store | content hash, byte size, media type, owner, immutable object version, retention | Append-only, encryption at rest, backup/export, verify on read; externally anchored ledger; signed receipts |
| Notebook | scoped search, candidate lesson, independent promotion and revocation | Machine facts with existing receipt refs; no unsupported model claims promoted; data not instruction |
| Formal prover | theorem source hash, Lean toolchain and dependencies, theorem statement, axiom/dependency list, output and proof receipt | Separate sandbox; reject admitted proof or unapproved axioms; proof of correctness is distinct from complexity proof |
| Release controller | exact source commit, build image, SBOM, artifact SHA, signature, qualification receipts, previous version, rollback | Build once and promote identical bytes; dedicated signing identity; manual publication only; no unattended updater until approved |

## Budget and campaign controls (target)
Before dispatch reserve maximum provider tokens/cost and worker time atomically. Reconcile actual usage including failures, refinements and retries. Reject unknown provider cost rather than treating as zero. Lease expires, cancellation increments epoch, pending work revoked; enforce time/CPU/memory/disk/PID/output limits at OS boundary. On restart inspect orphaned leases and require explicit resume authorization. Scheduled execution disabled initially. Separate GitHub CI from research compute and signing. Never execute a PR or model-generated source on a privileged workstation runner.

## Research program contracts
- SAT: input variable universe incl. unused variables, signed clauses, exact nonnegative assignment count and witness (optional). Independent exhaustive count for small fixtures; compare established exact #SAT baselines on larger instances, including connected hard, signed asymmetric, planted and UNSAT examples. Track wall time, peak RSS, work and bit lengths using same instrumentation.
- Permanent: polynomial matrix with exact integer/rational coefficients; output truncated coefficient vector and degree bound. Preserve H1+T2 and low-rank mixed terms. Existing polynomial subset DP is an exponential baseline, not an asymptotic advance. Add independent permutation oracle, modular ring/precision checks, sparse block families, adversarial nonunit denominator fixtures and full deformation inputs. Compare against same full pipeline and preserve original SAT count via exact reduction.
- P-adic: no division by nonunit without quantified extra precision. If p^v divides denominator, retain sufficient digits and check integrality or use valuation-aware rationals. Distinguish numerator digits from Taylor order and crossing order. Verify exact recovery via valid moduli and bit bound on final count; no claim of recovering full coefficient from ten digits.
- Complexity: explicit input length, all preprocessing, grouping, interpolation nodes and orders, output size, arithmetic and bit costs; separate finite checks from theorem. Model must not treat low fixed-precision groups or one translated permutation input as general improvement.
- Original baseline paper (included): 239x reduction in enumeration at ten base-11 digits, not measured speed; 6,234 eligible patterns, 167,712,948 interiors. 11/12 digit census only. Nine R1-R9 archives must be imported and replayed before treating their results as independently requalified; source paper does not substitute for code/data.

## UI / wireframe
```
+ AXIOM | Research campaign       [Dark/Light] [Provider OFF] [Stop status]
| Overview         | plan/source/fixture approval, elapsed budget, status |
| Campaigns        | arms: adaptive / blind; attempts used vs budget      |
| Experiments      | filters, strategy switches, exact verdict, work/time |
| Evidence         | dataset -> candidate output -> receipt -> replay     |
| Notebook         | observations / proposed lessons / approved / revoked|
| Proof workspace  | theorem statement, assumptions, toolchain, axioms   |
| Benchmarks       | frozen winners, holdout, null/negative comparisons    |
| Workers          | leases, resource caps, cancellation, trust boundary  |
| Engineering      | work slices, qualification, release identity          |
+ no simulated progress; no automatic background execution -------------+
```
Existing v0.2 fixture dashboard retained; additional loop report viewer is read-only snapshot, not a live orchestrator. Production UI: compact dark default, contrast-verified light mode, consistent focus/hover/selected states, keyboard operation, no truncated inaccessible results, virtualized tables with sort/filter/export, explicit data freshness, no silently substituted sample data, accessible motion/reduced motion, graphics preserve aspect ratio. Brand boards are concepts only; no metrics shown there are live evidence.

## GitHub process
Private repo; review extracted source and manifest; qualification on hosted ephemeral Windows/Linux workers; no scheduled research or artifact upload; read-only workflow token and pinned actions. `scripts/bootstrap.py` initializes local main after qualification; no push. `scripts/backlog.py` previews issue list; explicit `--apply` verifies private target. Import manually after review. Required checks/branch protection must be enabled in GitHub, not implied by YAML. Separate future hosted build, isolated research pool, acceptance runner and signing environment. No persistent runner secrets passed to candidate; signed release/rollback/SBOM and durable artifact retention are gates, not shipped. Use exact approved artifact hash for promotion. Do not add source paper or branding to public repositories without ownership review.
