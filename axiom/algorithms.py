"""Trusted deterministic fixture algorithms, never generated executable code."""
from fractions import Fraction as Q
from itertools import product, permutations
from functools import lru_cache
import random
from .research_math import component_count, polynomial_permanent, polynomial_oracle

def sat_oracle(n, clauses):
    total=0
    for bits in product((False,True),repeat=n):
        total+=all(any(bits[abs(x)-1] == (x>0) for x in c) for c in clauses)
    return total,2**n

def sat_split(n, clauses):
    # Keep the unassigned universe: unused variables still contribute to #SAT.
    calls=0
    @lru_cache(None)
    def walk(f, remaining):
        nonlocal calls
        calls+=1
        if () in f: return 0
        if not f: return 2**len(remaining)
        x=abs(min(f,key=len)[0]); rest=tuple(y for y in remaining if y!=x)
        def branch(lit):
            return tuple(sorted(set(tuple(y for y in c if y!=-lit) for c in f if lit not in c)))
        return walk(branch(x),rest)+walk(branch(-x),rest)
    f=tuple(sorted(set(tuple(sorted(set(c))) for c in clauses if not any(-x in c for x in c))))
    result=walk(f,tuple(range(1,n+1)))
    return result,calls

def sat_fixtures(seed):
    rng=random.Random(seed)
    cases=[(3,[(1,2,3),(-1,2,3)]),(1,[(1,),(-1,)]),(4,[]),(2,[()]),(3,[(1,-1),(2,2)])]
    for _ in range(75):
        n=rng.randrange(1,9); cases.append((n,[tuple(rng.choice((-1,1))*rng.randrange(1,n+1) for _ in range(rng.randrange(1,4))) for _ in range(rng.randrange(0,16))]))
    return cases

def coefficient_oracle(B,T,H):
    """Independent truncated polynomial multiplication over all permutations."""
    n=len(B); out=Q(0); ops=0
    for p in permutations(range(n)):
        a,b,c=Q(1),Q(0),Q(0)
        for i,j in enumerate(p):
            a,b,c=a*B[i][j],b*B[i][j]+a*T[i][j],c*B[i][j]+b*T[i][j]+a*H[i][j]
            ops+=1
        out+=c
    return out,ops

def quadratic(B,T,H, omit_h=False):
    """General identity; minor cache is exact, not a worst-case acceleration claim."""
    n=len(B); full=tuple(range(n)); calls=0
    @lru_cache(None)
    def minor(rows,cols):
        nonlocal calls
        calls+=1
        if not rows: return Q(1)
        i=rows[0]
        return sum((B[i][j]*minor(rows[1:],tuple(k for k in cols if k!=j)) for j in cols if B[i][j]),Q(0))
    def remaining(s): return tuple(i for i in full if i not in s)
    total=Q(0); support=[(i,j,T[i][j]) for i in full for j in full if T[i][j]]
    if not omit_h:
        for i in full:
            for j in full:
                if H[i][j]: total+=H[i][j]*minor(remaining({i}),remaining({j}))
    for a,(i,j,v) in enumerate(support):
        for k,l,w in support[a+1:]:
            if i!=k and j!=l: total+=v*w*minor(remaining({i,k}),remaining({j,l}))
    return total,calls

def coefficient_fixtures(seed):
    rng=random.Random(seed)
    cases=[([[Q(1),Q(1)],[Q(1),Q(2)]],[[Q(0)]*2 for _ in range(2)],[[Q(1),Q(0)],[Q(0),Q(0)]])]
    for _ in range(35):
        n=rng.randrange(2,6)
        cases.append(tuple([[Q(rng.randrange(-2,3),rng.choice([1,1,2,3])) for _ in range(n)] for _ in range(n)] for _ in range(3)))
    return cases

STRATEGIES={
 'sat.cached_split':('sat','Memoized Shannon splitting; exact counting',sat_split),
 'coef.full_quadratic':('coefficient','Keep H1 and T2; cache surviving minors',quadratic),
 'coef.omit_h':('coefficient','Negative control: omit degree-two perturbation H1',lambda B,T,H:quadratic(B,T,H,True)),
 'sat.components':('sat','Unit propagation and disconnected component counting',component_count),
 'coef.all_orders':('polynomial','Shared subset DP for all truncated Taylor orders',polynomial_permanent),
}

def polynomial_fixtures(seed):
    rng=random.Random(seed)
    cases=[([[[Q(1)]] , [[Q(2)]], [[Q(3)]]],5),([[]],4)]
    for _ in range(20):
        n=rng.randrange(1,5); h=rng.randrange(1,6); d=rng.randrange(1,5)
        cases.append(([[[Q(rng.randrange(-2,3),rng.choice([1,2,3])) for _ in range(n)] for _ in range(n)] for _ in range(d)],h))
    return cases

def plain(x):
    if isinstance(x,Q): return str(x)
    if isinstance(x,(tuple,list)): return [plain(v) for v in x]
    return x

def verify(strategy,seed):
    kind,description,fn=STRATEGIES[strategy]
    fixtures,oracle={'sat':(sat_fixtures,sat_oracle),'coefficient':(coefficient_fixtures,coefficient_oracle),'polynomial':(polynomial_fixtures,polynomial_oracle)}[kind]
    fixtures=fixtures(seed)
    passed=0; candidate_units=oracle_units=0
    for case in fixtures:
        expected,b=oracle(*case); actual,a=fn(*case)
        candidate_units+=a; oracle_units+=b
        if actual!=expected:
            return dict(verdict='counterexample',passed=passed,total=len(fixtures),candidate_units=candidate_units,oracle_units=oracle_units,counterexample={'input':plain(case),'expected':str(expected),'actual':str(actual)},description=description,work_units='Different instrumentation; not comparable as speedup')
        passed+=1
    return dict(verdict='finite_pass',passed=passed,total=len(fixtures),candidate_units=candidate_units,oracle_units=oracle_units,counterexample=None,description=description,work_units='Different instrumentation; not comparable as speedup')
