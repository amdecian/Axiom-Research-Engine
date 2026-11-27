"""Build deterministic self-contained Pages portal from allowlisted public-candidate records."""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def read(path):
    p=ROOT/path
    if p.is_symlink() or not p.resolve().is_relative_to(ROOT) or p.stat().st_size>1024**2: raise ValueError('unsafe input: '+str(path))
    return json.loads(p.read_text(encoding='utf-8'))


def notebook(root=ROOT):
    rows=[]; seen=set(); fields={'schema_version','id','title','status','statement','evidence','reproduce','review_status'}
    for path in sorted((root/'research/notebook').glob('*.json')):
        if path.is_symlink() or path.stat().st_size>16384: raise ValueError('unsafe notebook record')
        d=json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(d,dict) or set(d)!=fields or d['schema_version']!='notebook-1' or not isinstance(d['id'],str) or not re.fullmatch(r'N\d{3,6}',d['id']) or path.stem!=d['id'] or d['id'] in seen: raise ValueError('invalid notebook record')
        for k,lim in [('title',120),('statement',2000),('reproduce',300)]:
            if not isinstance(d[k],str) or not 0<len(d[k])<=lim: raise ValueError('invalid notebook text')
        if d['status'] not in ('finite_pass','counterexample','open') or d['review_status'] not in ('publication_pending','owner_reviewed') or not isinstance(d['evidence'],list) or len(d['evidence'])>8 or (d['status']!='open' and not d['evidence']): raise ValueError('invalid evidence scope')
        for e in d['evidence']:
            if not isinstance(e,dict) or set(e)!={'path','sha256'} or not isinstance(e['path'],str) or not re.fullmatch(r'evidence/[A-Za-z0-9_.-]+',e['path']): raise ValueError('invalid evidence path')
            f=root/e['path']
            if f.is_symlink() or not f.resolve().is_relative_to(root/'evidence') or not f.is_file() or f.stat().st_size>2*1024**2 or hashlib.sha256(f.read_bytes()).hexdigest()!=e['sha256']: raise ValueError('missing or altered evidence '+e['path'])
        seen.add(d['id']); rows.append(d)
    return rows


def build():
    backlog=read('research/backlog.json')+read('research/scientific-backlog.json')
    if len({x['id'] for x in backlog})!=len(backlog): raise ValueError('duplicate backlog ID')
    report=read('evidence/loop-report.json'); replay=read('evidence/loop-replay.json')
    data={'version':'0.4.0','notebook':notebook(),'backlog':backlog,'profile':read('config/free-tier.json'),'replay':replay,'history':{arm:[{'index':a['index'],'requests':a['metrics']['requests']} for a in rows] for arm,rows in report['history'].items()},'results':{arm:{'train':x['train']['metrics'],'holdout':x['holdout']['metrics']} for arm,x in report['winners'].items()},'elapsed_seconds':report['elapsed_seconds']}
    text=json.dumps(data,ensure_ascii=True,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    template=(ROOT/'scripts/portal-template.html').read_text(encoding='utf-8')
    if template.count('@@DATA@@')!=1: raise ValueError('bad template')
    result=template.replace('@@DATA@@',text)
    if len(result.encode())>1024**2: raise ValueError('portal exceeds 1 MiB project budget')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--check',action='store_true'); a=p.parse_args(); f=ROOT/'docs/index.html'; result=build()
    if a.check:
        if f.read_text(encoding='utf-8')!=result: raise ValueError('stale portal: regenerate and review diff')
    else: f.write_text(result,encoding='utf-8',newline='\n')
    print('Portal validated:',len(result.encode()),'bytes; no backend or external requests')
if __name__=='__main__': main()
