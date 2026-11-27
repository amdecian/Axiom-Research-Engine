# Worker protocol and orchestration reference

Proposed production protocol. Not implemented by the offline starter.

## Run handshake

1. Controller validates the immutable manifest, operator grant, adapter and resource policy. Atomically reserves quota, writes `attempt.queued`, and creates lease. Inputs and candidate blob are addressed by SHA-256; only public inputs enter candidate guest.
2. Worker authenticates to dispatcher, receives job envelope over a scoped channel; verify digest and lease before guest boot. No provider credential, ledger or holdout mounted. Guest launch policy enforced outside process.
3. Guest executes a fixed entrypoint, reads a single versioned input JSON via stdin or read-only input, emits exactly one bounded output JSON to stdout. For coefficient jobs use `{schema_version, order, coefficients:[{num,den}]}`; modular variant has `{schema_version, order, modulus, residues, retained_precision}`. All integers in exact output are decimal strings. Reject unknown fields, malformed signs, noncanonical fractions, out-of-range residues, unexpected coefficient length, NaN/Infinity, symlink artifacts or size limit overflow.
4. Worker emits termination status, trusted monotonic runtime and resource envelope plus candidate output digest; stdout is not a trusted receipt. Kill guest at deadline, then destroy scratch. Quarantine output, seal artifact manifest.
5. Referee fetches artifact through evidence-plane credentials, checks domain and frozen holdouts. Run oracle independently; produce receipt with exact comparison, minimized witness or reason, signature and environment hash. Formal proof checking is separately dispatched and linked; fixture receipt cannot confer theorem status.
6. Controller reconciles reservation, accepts only one valid terminal receipt per attempt, records signed checkpoint; review and promotion occur separately. A completed attempt has an output verdict, not necessarily a success.

## Reference orchestration pseudocode (not runnable)

```python
async def bounded_campaign(manifest, approval, controller):
    await controller.require_exact_manifest_approval(manifest, approval)
    while await controller.is_running(manifest.id):
        if await controller.stop_requested_or_budget_exhausted(manifest.id):
            break
        snapshot = await controller.freeze_approved_notebook(manifest.project_id)
        proposal = await gateway.propose(manifest.brief, snapshot, allowed_techniques)
        critique = await critic.review(proposal, snapshot)
        # validate proposal and reserve all maximum costs transactionally
        job = await controller.admit_and_lease(proposal, critique, manifest)
        if job is None:
            break
        artifact = await isolated_worker.execute(job)  # deadline enforced externally
        receipt = await independent_referee.verify(job, artifact)
        await controller.accept_signed_receipt_and_reconcile(job, receipt)
        # not an automatic lesson approval; reviewer must validate scope and provenance
        await review_queue.stage_lesson(receipt, proposal)
        if await controller.plateau_detected(manifest.id):
            await controller.pause_for_review(manifest.id)
            break
    await controller.revoke_leases_and_reconcile(manifest.id)
```

For production, enclose the loop in try/finally and reconcile crashes/unknown receipts from durable leases; use an independent watchdog. Reserve budget for both proposal/critique calls *before* dispatch, not only candidate execution. No unbounded automatic retry. A running controller cannot unilaterally extend its own approval.

## Memory promotion decision table

| Candidate result | Allowed record | Forbidden promotion |
|---|---|---|
| Exact counterexample | Rejection with domain/witness | Claim all related algorithms fail |
| Finite pass | Tested fixture scope and receipt | General theorem / asymptotic claim |
| Timeout or resource cap | Operational failure and resource evidence | Mathematical UNSAT or disproven identity |
| Reviewed derivation | Scoped lemma, assumptions, reviewer | Formal proof badge without kernel receipt |
| Trusted proof receipt | Exact checked statement and imports | Stronger theorem or unreviewed complexity bound |
