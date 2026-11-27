# Bootstrap checkpoint — 2026-11-27

Master issue: [#1](https://github.com/amdecian/Axiom-Research-Engine/issues/1). Resume from the issue and current main head; do not repeat completed imports. Bootstrap B001–B008 track deployment only, not completion of engineering S001–S112 or scientific R10–R29.

| Slice | State at this commit | Evidence |
|---|---|---|
| B001 baseline | PASS | Previous commit b3b2cee, hosted qualification 46066387561 successful |
| B002 public source / documentation | Partial | All runnable mathematical Python modules retained, local dashboard restored, six original historical/setup docs restored, capture script restored; archive-only bootstrap materials tracked below |
| B003 branding and packaging | Imported | All 16 editable vector/guide/token files matched original Git blob SHA; concepts provisional, not trademark-cleared |
| B004 engineering issues | PASS | S001–S112 in issues #2–#113, manifest and acceptance criteria audited |
| B005 scientific issues | PASS | R10–R29 in issues #114–#133, zero duplicate/missing/mismatched slice IDs across both manifests |
| B006 hosted replay | Pending hosted result | Local fixed regression matched historical report ignoring timings: 26 evaluations, 2482 rechecked results, 18.676 seconds campaign elapsed. Explicit marker-triggered bounded bootstrap regression only; ordinary replay remains workflow_dispatch only. |
| B007 repository administration | Owner pending | Pages, rulesets, contributor approvals, dependency/security settings, metered-product budget |
| B008 acceptance | Open | License/ownership and original archive disposition; see issue #1 |

## Original distribution identity

- Original archive: Axiom_Research_Engine_Free_Open_Research_v0.4.0.zip
- SHA-256: bdc4ca7f9fc52e8f5849b3923cadb84adff0ff89ca5407d45de1ab525f6d9c3f
- Original distribution contains 98 files. Git is now the evolving source of truth. Preserve original checksums separately rather than replacing the current tree with the original snapshot.
- The original binary `evidence/sat-loop-replay.zip` (51526 bytes, 49 members, SHA-256 a4c98b8954a4013b0319bba8c4f6f86a9c980070a8b066b67e59acfefcfa7b48) remains in the original distribution. The public source can recreate a fresh, independently replayed bundle using `scripts/capture_evidence.py`. A fresh archive has new ledger UUIDs/timestamps and is not byte-identical.
- `LICENSE.proposed` remains an unapproved proposal; no license grant asserted.
- Original `scripts/bootstrap.py` and `BOOTSTRAP_SHA256.json` are for a pristine extracted distribution, not this already initialized evolving Git checkout. Do not run original archive import over main.
- The review-only companion, original R1–R9 archives, raw transcript and paper remain outside the public tree.

## Hosted constraints

Only standard ephemeral GitHub-hosted runners, fixed finite qualification, read-only workflow token, no paid AI, no self-hosted infrastructure, no routine artifacts or caches, no scheduled research. The one-time B006 test is tied to the reviewed bootstrap approval marker, not a recurring discovery campaign. Account-level budget enforcement and repository administration must be verified by the owner. No production proof or asymptotic advance is claimed. Do not interpret the historical local-first documentation as overriding the hosted contract.
