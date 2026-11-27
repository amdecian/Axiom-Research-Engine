# Dual-repository disclosure boundary — S113–S124

Public engineering and separately access-controlled research are distinct workstreams. The public repository is not an intake point for confidential evidence, unpublished hypotheses, draft proofs, hidden verification inputs or original private archives. This policy supersedes any earlier suggestion to keep all research in one repository. Public commits, issues, pull requests, branch names, Actions logs, release assets and Pages are public disclosures; deletion cannot recall downloaded copies.

## Classification and trust

| Class | Storage | Publication |
|---|---|---|
| Public approved | Public repository | Reviewed source, synthetic inputs, approved evidence and published results only |
| Publication candidate | Access-controlled research workspace | Draft sanitized copy; not public until approved |
| Private research | Access-controlled research workspace | Default for new findings, private holdouts, original archives and draft proofs |
| Restricted secret | Neither repository | External authorized secret store; never committed |

No public workflow or contributor gets access to the private repository, its credentials, paths, manifests, holdouts, or hashes. Public CI tests the generic gate against entirely synthetic local Git fixtures only. Never transfer real private data to public compute to avoid quotas. No shared history, cross-repository automatic sync, or secret-bearing connector automation. No scheduled campaigns, paid model calls or self-hosted runners. Private computation remains off unless separately authorized after account budget/feature review. No repository setting is implied by a code-level policy; Free private rulesets and protection may be unavailable.

## Controlled publication

1. Review ownership, intended license, scientific correctness/novelty and security. Review the full text, not merely its hash. A public repository without an approved license is not a general open-source grant.
2. In the restricted workspace, prepare deliberate candidate copies in `publication/candidates/PUB-NNNNNN/<public-relative-path>`. Commit the candidates. Do not export a private branch, entire repository, archive, or raw history.
3. Prepare a private publication-1 manifest referencing that exact commit and current intended public base commit. Require four true attestations (rights, scientific, security, owner), exact file sizes and SHA-256 hashes. Attestations are human declarations, not cryptographic identity or a proof.
4. Use `scripts/publication_gate.py preview` with the source checkout and manifest; inspect exact files and digest in the restricted environment. Only the owner may authorize that digest. `stage` additionally requires explicit owner confirmation. It reads pinned local Git blobs, rejects nonregular or executable modes, restricts approved destinations/types, scans heuristic sensitive markers, validates hashes and bounds, then creates a new staging directory outside Git checkouts. No network, execution, push, release or credentials.
5. Before transferring any approved file, verify actual source visibility and ownership, target identity, current public base revision, manifest digest and exact staged bytes. A local Git origin is not authenticated repository identity. Stage approval is not authorization to publish; obtain separate explicit approval for the exact public diff and its metadata. Only copy approved file bytes. Never copy the private manifest, approval digest, source commit, candidate paths, private filenames, notebook identifiers or logs into the public repo. A public branch or draft PR already discloses its contents.
6. Build a fresh branch from the reviewed public base (do not merge/fetch private history), examine the diff, run bounded public qualification, verify the public result, record public revision and decision privately. No automatic merge or disclosure. Existing public documentation and evidence are not retroactively approved by the gate.

## Limitations and stop rules

This is an offline staging control, not a DLP system, malware scanner, signature system, code sandbox, theorem verifier or enforceable GitHub access control. It does not verify live remote visibility, public branch freshness, reviewer identity, private repository settings or billing. Text can disclose confidential math without recognizable markers; Python files can be harmful despite passing the scan. A trusted reviewer must inspect exact bytes and code, check destination collisions and prove rights/correctness as appropriate. Stop on scope changes, missing objects, stale approvals, unrecognized content or private data. Re-review any changed source, destination, base revision or file bytes. Keep all private audit records private. Restrict connector access and approve storage/retention independently. Do not enter passwords, provider keys, signing material or employer-owned files.

## CLI

The generic gate requires Python 3.11+ and local Git; no dependencies or service credentials. See the manifest contract. The following commands are examples only; do not run against a real release without approval.

```text
python scripts/publication_gate.py preview --source SOURCE_CHECKOUT --manifest PRIVATE_MANIFEST
python scripts/publication_gate.py stage --source SOURCE_CHECKOUT --manifest PRIVATE_MANIFEST --approve-sha256 REVIEWED_DIGEST --confirm-owner-approval --out NEW_STAGING_DIRECTORY
```

The public repository stores only the generic gate and synthetic unit tests. Nothing in this contract authorizes a real private-to-public export.
