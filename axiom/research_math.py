"""Trusted, finite experiment algorithms. No model or generated code execution."""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import permutations


def component_count(n, clauses):
    """Exact #SAT with unit propagation, disconnected components, and memoization.

    Unassigned variables not appearing in clauses contribute powers of two.
    Complexity remains exponential on general instances.
    """
    if type(n) is not int or n < 0:
        raise ValueError('invalid variable count')
    if any(type(x) is not int or not 1 <= abs(x) <= n for c in clauses for x in c):
        raise ValueError('invalid literal')
    f = tuple(sorted({tuple(sorted(set(c))) for c in clauses if not any(-x in c for x in c)}))
    calls = 0

    def restrict(f, lit):
        return tuple(sorted({tuple(x for x in c if x != -lit) for c in f if lit not in c}))

    @lru_cache(None)
    def walk(f):
        nonlocal calls
        calls += 1
        if () in f:
            return 0
        if not f:
            return 1
        active = {abs(x) for c in f for x in c}
        def branch(lit):
            rest = restrict(f, lit)
            surviving = {abs(x) for c in rest for x in c}
            return (1 << len(active - surviving - {abs(lit)})) * walk(rest)
        unit = next((c[0] for c in f if len(c) == 1), None)
        if unit is not None:
            return branch(unit)
        # Union-find on the clause-variable incidence graph.
        parent = {x:x for x in active}
        def root(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for c in f:
            for lit in c[1:]:
                parent[root(abs(lit))] = root(abs(c[0]))
        groups = {}
        for c in f:
            groups.setdefault(root(abs(c[0])), []).append(c)
        if len(groups) > 1:
            ans = 1
            for group in groups.values():
                ans *= walk(tuple(group))
            return ans
        x = abs(min(f, key=len)[0])
        return branch(x) + branch(-x)

    active = {abs(x) for c in f for x in c}
    return (1 << (n - len(active))) * walk(f), calls


def _shape(coefficients, h):
    if type(h) is not int or h < 1 or not coefficients:
        raise ValueError('positive truncation and at least one coefficient matrix required')
    n = len(coefficients[0])
    if any(len(M) != n or any(len(row) != n for row in M) for M in coefficients):
        raise ValueError('coefficient matrices must have equal square dimensions')
    if any(not isinstance(x, (int, Q)) or isinstance(x, bool) for M in coefficients for row in M for x in row):
        raise ValueError('exact integer or rational entries required')
    return n


def polynomial_permanent(coefficients, h):
    """Column-subset DP over Q[z]/(z**h); all h coefficients in one traversal.

    O(n*2**n*h*min(h,d+1)) rational multiply-adds and O(2**n*h)
    rational slots (upper bounds, not bit complexity or a new SAT bound).
    """
    n = _shape(coefficients, h)
    D = [ [Q(1)] + [Q(0)]*(h-1) ] + [None]*((1<<n)-1)
    work = 0
    for mask in range(1<<n):
        if D[mask] is None or mask == (1<<n)-1:
            continue
        row = mask.bit_count()
        for j in range(n):
            if mask & (1<<j):
                continue
            target = mask | (1<<j)
            if D[target] is None:
                D[target] = [Q(0)]*h
            for b, M in enumerate(coefficients[:h]):
                v = M[row][j]
                if not v:
                    continue
                for a in range(h-b):
                    D[target][a+b] += D[mask][a]*v
                    work += 1
    return tuple(D[-1]), work


def polynomial_oracle(coefficients, h):
    """Independent permutation/degree-choice oracle for tiny matrices."""
    from itertools import product
    n = _shape(coefficients, h)
    out = [Q(0)]*h
    work = 0
    for p in permutations(range(n)):
        for degrees in product(range(min(h,len(coefficients))), repeat=n):
            degree = sum(degrees)
            if degree >= h:
                continue
            value = Q(1)
            for i,d in enumerate(degrees):
                value *= coefficients[d][i][p[i]]
                work += 1
            out[degree] += value
    return tuple(out), work
