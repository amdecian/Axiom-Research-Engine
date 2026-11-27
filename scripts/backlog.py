"""Preview issues; explicit bounded import to an independently reviewed target."""
import argparse,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def gh(*args): return subprocess.run(['gh',*args],check=True,text=True,capture_output=True).stdout

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--repo'); p.add_argument('--apply',action='store_true'); p.add_argument('--visibility',choices=['public','private']); p.add_argument('--ack-publication',action='store_true'); p.add_argument('--batch',type=int,default=15); p.add_argument('--scope',choices=['engineering','science','all'],default='all'); a=p.parse_args()
    rows=[]
    if a.scope in ('engineering','all'): rows+=json.loads((ROOT/'research/backlog.json').read_text(encoding='utf-8'))
    if a.scope in ('science','all'): rows+=json.loads((ROOT/'research/scientific-backlog.json').read_text(encoding='utf-8'))
    if not a.apply:
        print('\n'.join(f"{x['title']} | depends: {x['dependencies']}" for x in rows)); print(f'{len(rows)} issues; preview only.'); return
    if not a.repo or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',a.repo) or not a.visibility or not 1<=a.batch<=25: p.error('explicit OWNER/REPO, visibility and batch 1–25 required')
    if a.visibility=='public' and not a.ack_publication: p.error('public issue publication requires --ack-publication')
    r=json.loads(gh('repo','view',a.repo,'--json','nameWithOwner,visibility'))
    if r['visibility'].lower()!=a.visibility or r['nameWithOwner'].casefold()!=a.repo.casefold(): raise ValueError('repository identity or visibility mismatch')
    existing=json.loads(gh('issue','list','-R',a.repo,'--state','all','--limit','1000','--json','title'))
    if len(existing)>=1000: raise ValueError('issue listing limit reached; refusing potentially duplicate import')
    seen={m.group(1) for x in existing if (m:=re.match(r'^\[((?:S\d{3}|R\d{2}))\]',x['title']))}
    pending=[x for x in rows if x['id'] not in seen]
    for x in pending[:a.batch]:
        body=f"Dependencies: {x['dependencies']}\n\nAcceptance criteria: {x['acceptance']}\n\nStatus: needs implementation/review. Finite prototype evidence is not production closure or mathematical proof."
        print(gh('issue','create','-R',a.repo,'--title',x['title'],'--body',body).strip(),flush=True)
    print(f'Batch created {min(a.batch,len(pending))}; remaining {max(0,len(pending)-a.batch)}. Run one importer at a time, review before each batch. No automatic retries.')
if __name__=='__main__':
    try: main()
    except subprocess.CalledProcessError as e: print('Import stopped; inspect GitHub response/rate limit before retry:',e.stderr,file=sys.stderr); sys.exit(1)
    except (OSError,ValueError) as e: print(f'Import stopped: {e}',file=sys.stderr); sys.exit(1)
