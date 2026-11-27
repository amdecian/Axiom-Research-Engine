"""Declarative #SAT search space. No generated source, eval, plugins or shell.
The objective is recursive requests on this kernel, not runtime or bit complexity.
"""
from itertools import product
from collections import Counter
from .algorithms import sat_oracle, sat_fixtures
import random

POLICIES = ('shortest', 'frequency', 'balanced')
FIELDS = ('branch', 'unit', 'components', 'memo')
BASELINE = {'branch':'shortest','unit':False,'components':False,'memo':False}

def validate(s):
    if not isinstance(s, dict) or set(s)!=set(FIELDS) or s['branch'] not in POLICIES or any(type(s[k]) is not bool for k in FIELDS[1:]):
        raise ValueError('invalid declarative strategy')
    return dict(s)

def space():
    return [dict(zip(FIELDS, p)) for p in product(POLICIES,(False,True),(False,True),(False,True))]

def key(s): return tuple(s[k] for k in FIELDS)
def distance(a,b): return sum(a[k]!=b[k] for k in FIELDS)

def count(n, clauses, strategy):
    s = validate(strategy)
    if type(n) is not int or not 0<=n<=16 or len(clauses)>128: raise ValueError('invalid fixture bounds')
    if any(len(c)>8 or any(type(x) is not int or not 1<=abs(x)<=n for x in c) for c in clauses): raise ValueError('invalid clause')
    f=tuple(sorted({tuple(sorted(set(c))) for c in clauses if not any(-x in c for x in c)}))
    memo={}; requests=0; expanded=0; hits=0; restriction_visits=0
    def active(f): return {abs(x) for c in f for x in c}
    def restrict(f,l):
        nonlocal restriction_visits
        restriction_visits+=sum(map(len,f))
        return tuple(sorted({tuple(x for x in c if x!=-l) for c in f if l not in c}))
    def walk(f):
        nonlocal requests, expanded, hits
        requests+=1
        if s['memo'] and f in memo:
            hits+=1; return memo[f]
        expanded+=1
        ans=solve(f)
        if s['memo']: memo[f]=ans
        return ans
    def solve(f):
        if () in f: return 0
        if not f: return 1
        variables=active(f)
        def branch(l):
            rest=restrict(f,l)
            return (1 << len(variables-active(rest)-{abs(l)}))*walk(rest)
        if s['unit']:
            u=next((c[0] for c in f if len(c)==1),None)
            if u is not None: return branch(u)
        if s['components']:
            parent={v:v for v in variables}
            def root(x):
                while parent[x]!=x: x=parent[x]
                return x
            for c in f:
                for l in c[1:]: parent[root(abs(l))]=root(abs(c[0]))
            groups={}
            for c in f: groups.setdefault(root(abs(c[0])),[]).append(c)
            if len(groups)>1:
                ans=1
                for k in sorted(groups): ans*=walk(tuple(groups[k]))
                return ans
        if s['branch']=='shortest': v=abs(min(f,key=len)[0])
        else:
            pos=Counter(x for c in f for x in c)
            if s['branch']=='frequency': v=max(sorted(variables),key=lambda x:pos[x]+pos[-x])
            else: v=max(sorted(variables),key=lambda x:(min(pos[x],pos[-x]),pos[x]+pos[-x]))
        return branch(v)+branch(-v)
    value=(1 << (n-len(active(f))))*walk(f)
    return {'count':value,'requests':requests,'expanded':expanded,'cache_hits':hits,'restriction_literal_visits':restriction_visits}

def fixtures(seed):
    """Fixed training/holdout recipe: tiny random CNF plus structured families."""
    cases=[{'n':n,'clauses':[list(c) for c in f],'family':'tiny'} for n,f in sat_fixtures(seed)]
    rng=random.Random(seed)
    for i in range(8):
        # disconnected, planted and frustrated motifs; includes unused variables.
        n=12; cs=[]
        for base in (0,4,8):
            for _ in range(5):
                cs.append([rng.choice((-1,1))*(base+j) for j in rng.sample(range(1,5),3)])
        cases.append({'n':n,'clauses':cs,'family':'disconnected'})
        cs=[[(1 if rng.randrange(2) else -1)*j for j in rng.sample(range(1,13),3)] for _ in range(30+i)]
        cases.append({'n':n,'clauses':cs,'family':'connected_random'})
    return cases

def reference(cases): return [sat_oracle(c['n'],c['clauses'])[0] for c in cases]

def evaluate(cases,s): return [count(c['n'],c['clauses'],s) for c in cases]

def verify(cases, expected, rows):
    if not isinstance(rows,list) or len(rows)!=len(cases) or len(expected)!=len(cases): raise ValueError('bad output cardinality')
    metrics=('requests','expanded','cache_hits','restriction_literal_visits')
    for i,row in enumerate(rows):
        if not isinstance(row,dict) or set(row)!={'count',*metrics} or any(type(v) is not int or v<0 for v in row.values()): raise ValueError('malformed candidate output')
        if row['requests']!=row['expanded']+row['cache_hits'] or not row['expanded'] or row['count']>2**cases[i]['n']: raise ValueError('invalid counters or count')
        if row['count']!=expected[i]:
            return {'verdict':'counterexample','checked':i+1,'total':len(cases),'counterexample':{'index':i,'case':cases[i],'expected':expected[i],'actual':row['count']},'metrics':None}
    return {'verdict':'finite_pass','checked':len(cases),'total':len(cases),'counterexample':None,'metrics':{k:sum(r[k] for r in rows) for k in metrics}}


def choose(order, history, condition, plateau):
    """Return next candidate and transparent decision, given verified observations only."""
    tried={key(x['strategy']) for x in history}; remaining=[x for x in order if key(x) not in tried]
    if not remaining: raise ValueError('search exhausted')
    if not history: return BASELINE.copy(),'baseline'
    if condition=='blind': return remaining[0],'seeded_nonadaptive'
    valid=[x for x in history if x['verdict']=='finite_pass']
    if not valid: return remaining[0],'explore_no_valid_incumbent'
    incumbent=min(valid,key=lambda x:x['metrics']['requests'])
    after=len(history)-1-history.index(incumbent)
    if after>=plateau:
        return max(remaining,key=lambda s:min(distance(s,x['strategy']) for x in history)),'plateau_diversity'
    return min(remaining,key=lambda s:distance(s,incumbent['strategy'])),'mutate_incumbent'
