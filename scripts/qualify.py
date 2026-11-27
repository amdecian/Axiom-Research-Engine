"""Offline deterministic qualification. Does not upload or call a model."""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)

def command(*args,capture=False):
    return subprocess.run([sys.executable,*args],check=True,text=True,capture_output=capture)

def main():
    command('-m','unittest','discover','-s','tests','-v')
    with tempfile.TemporaryDirectory(prefix='axiom-qualification-') as directory:
        db=str(Path(directory)/'test.db'); snapshot=Path(directory)/'snapshot.json'; plan='research/plans/first-campaign.json'
        spec=json.loads(command('-m','axiom','plan',plan,capture=True).stdout)
        command('-m','axiom','--db',db,'run',plan,'--approve-digest',spec['approval_digest'])
        command('-m','axiom','--db',db,'audit')
        command('-m','axiom','--db',db,'snapshot','--out',str(snapshot))
        data=json.loads(snapshot.read_text(encoding='utf-8'))
        attempts=data['attempts']; expected={'sat.cached_split':80,'sat.components':80,'coef.full_quadratic':36,'coef.all_orders':22}
        if not data['ledger_valid'] or len(attempts)!=10 or data['memory']:
            raise RuntimeError('unexpected qualification ledger')
        for a in attempts:
            r=a['result']; s=a['strategy']
            if s=='coef.omit_h':
                if r['verdict']!='counterexample' or not r['counterexample']: raise RuntimeError('negative control failed')
            elif r['verdict']!='finite_pass' or r['passed']!=expected[s] or r['total']!=expected[s]:
                raise RuntimeError('fixture qualification failed')
        if {(a['strategy'],a['seed']) for a in attempts}!={(s,n) for s in (*expected,'coef.omit_h') for n in (20261127,77)}:
            raise RuntimeError('wrong strategy/seed coverage')
        command('-m','axiom','--db',db,'approve',attempts[0]['attempt_id'])
        command('-m','axiom','--db',db,'audit')
        print('QUALIFIED: 10 attempts; 8 finite passes (436 exact fixture comparisons); 2 expected counterexamples; ledger and explicit approval passed.')
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extended',action='store_true',help='also execute and replay the full adaptive loop')
    args=parser.parse_args()
    main()
    if args.extended: command('scripts/qualify_loop.py')
