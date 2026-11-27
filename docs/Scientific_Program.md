# Scientific program / R10–R29

The research baseline investigates exact coefficient calculations within a structured-permanent SAT reduction. It distinguishes a reduction in enumeration from a measured speedup and a worst-case complexity proof. The original paper's ten-digit experiment has 167,712,948 interiors and 40,143,346,628 eligible ordered walks, but no established general SAT improvement. Original executable R1–R9 archives are not present; no full reproduction is claimed. Their paper remains in the separate review-only package pending publication rights.

## First implemented extensions

For a canonical equality pattern w, fix the first label at zero and last at displacement d in a finite binary group G. Each edge contributes z(label_u XOR label_v). Let Z(H/pi;d) sum over all assignments to the quotient graph satisfying fixed endpoints. If endpoints merge and d is nonzero, the sum is zero. Weighted injections are recovered via partition lattice inversion:

`Inj(H;d) = sum_pi mu(pi) Z(H/pi;d)`

`mu(pi) = product_B (-1)^(|B|-1) (|B|-1)!`.

This is the standard partition Möbius identity applied to weighted walks. Each assignment contributes once precisely when its equality partition is discrete; otherwise the sum of Möbius weights over refining partitions is zero. Repeated edges and loops retain multiplicity. Tests cover length 0–4, three signed integer kernels, group of size eight, every endpoint displacement: 576 exact comparisons. Direct and quotient methods use the same weight convention; tests are finite and no claimed new theorem of complexity. The quotient baseline still enumerates labels and partitions; it may be slower. Next implement low-width contractions and cross-pattern reuse before larger matrices.

For known integer A divisible by q, if r is its canonical residue modulo q*m, then r is divisible by q, and r/q is A/q mod m. The function `divide_known_multiple` checks precision and residue divisibility; it cannot prove the caller's global integrality assumption. Nonintegral rational contributions must be combined or represented with valuations before using this identity. Tests cover signed inputs and bad precision.

Final count CRT: with count in [0,2^n] and coprime moduli product strictly greater than 2^n, unique recovery is possible; reject inconsistent or ambiguous ranges. Current implementation reconstructs supplied residues, not the full SAT-to-permanent reduction. Tests cover all counts 0–64 plus bad moduli. All coefficients through a bounded order can already be computed via existing column-subset DP; its cost remains exponential in matrix dimension. Do not treat that as the desired asymptotic solution.

## Research agenda

`research/scientific-backlog.json` holds R10–R29. Review recent claims about arithmetic-circuit lower bounds, alternative subexponential SAT methods, finite Fourier transforms, tensor topology and combinatorial grouping against their original statements and formal proof status before relying on them. These are investigation targets, not asserted facts of the package. Highest priority: verify model of lower bounds; quotient graph evaluation and treewidth; whole truncated coefficient families; modular interpolation and final CRT; asymmetric SAT-derived cases; formal specification and proof. Track input size, operations, bit complexity, runtime, RSS and negative controls separately. The hosted software tests use modest cases; large exploratory computation is not a default workflow.
