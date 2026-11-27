"""Offline loop qualification; no external model calls or uploads."""
import json, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from axiom import loop

def main():
    p=loop.load(ROOT/'research/plans/adaptive-sat.json')
    with tempfile.TemporaryDirectory(prefix='axiom-loop-qa-') as d:
        root=Path(d)/'run'; spec=loop.prepare(p)[0]; r=loop.run(p,spec['approval_digest'],root)
        assert r['reason']=='completed' and len(r['history']['adaptive'])==len(r['history']['blind'])==p['attempts_per_arm']
        for arm in ('adaptive','blind'):
            assert all(x['verdict']=='finite_pass' for x in r['history'][arm]) and r['winners'][arm]['holdout']['verdict']=='finite_pass'
        replay=loop.replay(root); assert replay['replayed_evaluations']==spec['max_evaluations']; print(json.dumps(replay,indent=2))
if __name__=='__main__': main()
