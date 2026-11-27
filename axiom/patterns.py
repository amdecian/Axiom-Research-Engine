"""Bounded exact weighted XOR walk baselines, not a general speedup or R9 replay."""
from itertools import product, permutations
from math import factorial, gcd, prod


def patterns(length):
    if type(length) is not int or not 0 <= length <= 4: raise ValueError('length outside fixture bound')
    def extend(w):
        if len(w) == length + 1: yield w
        else:
            for v in range(max(w)+2):
                if v != w[-1]: yield from extend(w+(v,))
    yield from extend((0,))


def partitions(n):
    def rec(w):
        if len(w)==n: yield w
        else:
            for v in range(max(w)+2): yield from rec(w+(v,))
    yield from rec((0,))


def validate(w,z,d):
    if not isinstance(w,(tuple,list)) or not 1<=len(w)<=7 or w[0]!=0 or any(type(x) is not int or x<0 or x>max(w[:i],default=-1)+1 for i,x in enumerate(w)): raise ValueError('invalid restricted-growth word')
    if not 1<=len(z)<=16 or len(z)&(len(z)-1) or any(type(x) is not int or abs(x)>10**6 for x in z): raise ValueError('bounded integer XOR kernel required')
    if type(d) is not int or not 0<=d<len(z): raise ValueError('invalid displacement')
    if max(w)+1>5: raise ValueError('at most five distinct vertices in pilot')


def _weighted(w,z,labels):
    return prod(z[labels[a]^labels[b]] for a,b in zip(w,w[1:]))


def direct(w,z,d):
    """Independent explicit injection oracle, start=0, end=d."""
    validate(w,z,d)
    if (w[0]==w[-1])!=(d==0): return 0
    fixed={w[0]:0,w[-1]:d}; free=[i for i in range(max(w)+1) if i not in fixed]
    allowed=[i for i in range(len(z)) if i not in fixed.values()]
    return sum(_weighted(w,z,fixed|dict(zip(free,values))) for values in permutations(allowed,len(free)))


def mobius(w,z,d):
    """Partition-lattice inversion; quotient homomorphism sums still enumerate labels.
    Returns exact total and enumeration metrics. No speed claim.
    """
    validate(w,z,d)
    total=0; cache={}; evals=0; terms=0
    for p in partitions(max(w)+1):
        terms+=1
        q=tuple(p[x] for x in w); ren={}; q=tuple(ren.setdefault(x,len(ren)) for x in q)
        if q not in cache:
            s=0
            if not (q[0]==q[-1] and d!=0):
                fixed={q[0]:0,q[-1]:d}; free=[i for i in range(max(q)+1) if i not in fixed]
                for values in product(range(len(z)),repeat=len(free)):
                    s+=_weighted(q,z,fixed|dict(zip(free,values))); evals+=1
            cache[q]=s
        mu=prod((-1)**(p.count(x)-1)*factorial(p.count(x)-1) for x in set(p))
        total+=mu*cache[q]
    return total,{'partitions':terms,'quotients':len(cache),'label_assignments':evals}


def divide_known_multiple(residue,divisor,modulus,extra_modulus):
    """Recover A/divisor mod modulus from A mod (divisor*modulus).
    Caller must prove A is an integer divisible by divisor; no nonunit inverse.
    """
    if any(type(x) is not int for x in (residue,divisor,modulus,extra_modulus)) or divisor<1 or modulus<2 or extra_modulus!=divisor*modulus or not 0<=residue<extra_modulus or residue%divisor: raise ValueError('insufficient precision or inconsistent divisibility')
    return residue//divisor


def crt_count(residues,moduli,n):
    """Reconstruct nonnegative count <= 2**n, requiring uniqueness."""
    if type(n) is not int or not 0<=n<=4096 or not residues or len(residues)!=len(moduli): raise ValueError('invalid count contract')
    x=0; m=1
    for r,q in zip(residues,moduli):
        if type(q) is not int or type(r) is not int or q<2 or not 0<=r<q or gcd(m,q)!=1: raise ValueError('noncanonical or noncoprime modulus')
        x+=m*((r-x)*pow(m,-1,q)%q); m*=q
    if m<=1<<n or x>1<<n: raise ValueError('insufficient range or invalid count')
    return x
