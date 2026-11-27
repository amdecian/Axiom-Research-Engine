"""Capture finite software replay in a new local directory; no upload or promotion."""
import argparse,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from axiom import loop

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--out',required=True); a=p.parse_args(); out=Path(a.out).resolve()
    if out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/'local'): raise ValueError('within repo use ignored local/; review before committing')
    out.mkdir(parents=True,exist_ok=False)
    plan=loop.load(ROOT/'research/plans/adaptive-sat.json'); spec=loop.prepare(plan)[0]
    run=out/'run'; report=loop.run(plan,spec['approval_digest'],run)
    if report['reason']!='completed' or any(x['verdict']!='finite_pass' for rows in report['history'].values() for x in rows): raise ValueError('campaign did not qualify')
    replay=loop.replay(run); print(json.dumps(replay,indent=2))
    (out/'loop-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (out/'loop-replay.json').write_text(json.dumps(replay,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(out/'sat-loop-replay.zip','w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(run.rglob('*')):
            if f.is_file(): z.write(f,f.relative_to(run))
if __name__=='__main__': main()
