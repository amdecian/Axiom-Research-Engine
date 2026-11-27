> Historical foundation retained; `Hosted_Engineering_Contract.md` supersedes conflicting hosting and publication requirements.

# Extended work slices (S049–S072)

Existing S001–S048 remain intact and open to review. These additions refine the discovery loop and integrate the portfolio lessons; no issues are marked closed merely because a prototype exists. Dependencies listed are engineering gates, not an assertion of completion.

| ID | Objective | Dependency | Acceptance |
|---|---|---|---|
| S049 | Baseline source audit | S001 | Upstream source identity and limitations recorded; no upstream executable reuse. |
| S050 | Declarative strategy space | S025 | Strict schema; all 24 configurations on exhaustive 512 CNFs; no dynamic code. |
| S051 | Independent exact oracle | S007,S050 | Incorrect count and malformed result rejected; independent oracle in verifier process/role. |
| S052 | Matched adaptive and blind arms | S050,S051 | Same fixtures, attempt caps and baseline; fixed seeds; separate histories; null results preserved. |
| S053 | Diverse selection and plateau | S052 | Seeded tie-breaking; no duplicates; escape policy test; characterize novelty metrics. |
| S054 | Freeze winners and holdout | S052 | Both winners frozen before evaluation; held-out disjoint and independent; no feedback to selection. |
| S055 | Evidence CAS | S005,S051 | Hash validate on read, atomic local writes; production immutable versioned store with backup. |
| S056 | Deterministic replay | S008,S055 | Replay exact results and policy, reject altered blob, malformed state, wrong source; signed external ledger anchor. |
| S057 | Multi-seed experimental protocol | S052,S054 | Prespecified seeds; matched total evaluation and compute budgets; report distributions and nulls. |
| S058 | Operation and resource instrumentation | S057 | Same kernel cost model, timing/RSS/bit lengths, trust external measurements; no misleading speed ratio. |
| S059 | Provider proposal schema | S017,S050 | Bounded strict typed proposals, evidence snapshot ID validation, no generated execution, provider error classification. |
| S060 | Provider broker and budgets | S011,S059 | Explicit model and token caps, cost reservation/reconciliation, retries count, keys only in broker. |
| S061 | Verified scoped memory | S020,S055,S056 | Namespace/ACL enforcement, evidence-linked notes, revocation and dependency checks, empty history cannot invent observations. |
| S062 | Matched memory controls | S057,S061 | Memory on/off/shuffled with equal provider, seed, evaluation and cost budget; leakage audit. |
| S063 | Candidate patch lineage | S012,S059 | Parent hash, unique context, all-or-nothing apply, size/format caps; no edit executes before isolation gate. |
| S064 | Hardened worker qualification | S012–S016,S063 | Deny network/files/secrets, process-tree termination, bounded output, PID/RAM/disk/CPU, adversarial tests. |
| S065 | Separate referee trust domain | S014,S064 | Candidate cannot access hidden tests, modify verifier or forge receipt; signed trusted measurement. |
| S066 | Permanent polynomial search plugin | S026–S028,S051 | Compare all coefficient orders on signed inputs against independent oracle; keep higher-order terms. |
| S067 | Precision and arithmetic plugin | S029,S066 | Nonunit denominator and valuation regression; proof of precision bound; report bit complexity. |
| S068 | General SAT transfer benchmark | S030–S032,S058,S066 | Reproduce reduction, compare count and complete resource cost on asymmetric/full inputs. |
| S069 | Formal proof and cost gates | S033–S040,S065 | Pin toolchain, inspect axioms, reject admitted proofs, explicit correctness/complexity theorem. |
| S070 | Research dashboard integration | S041–S044,S056 | Evidence-linked loop views, accessibility, actual status, dark/light, filters, export, authorization separation. |
| S071 | Release and restore drill | S045–S047,S055,S064 | Build once, provenance, SBOM/signing, restore evidence, rollback exact artifact, no automatic publisher. |
| S072 | Controlled independent pilot | S048,S062,S065,S068,S069,S070,S071 | Operator-authorized limits, emergency stop, independent review, report failures and no unjustified scientific claims. |
