"""Finite local research loop, matched budget control, replay and evidence export."""
import argparse, hmac, json, random, subprocess, sys, time, platform, os
from pathlib import Path
from . import strategy as st
from .campaign import source_digest
from .store import Ledger, canonical, digest
from .blobstore import BlobStore

FIELDS={'schema_version','name','seed','train_seed','holdout_seed','attempts_per_arm','plateau','attempt_timeout_seconds','campaign_timeout_seconds'}

def validate_plan(p):
    if not isinstance(p,dict) or set(p)!=FIELDS or p['schema_version']!='loop-1': raise ValueError('invalid loop-1 fields')
    if not isinstance(p['name'],str) or not p['name'].strip() or len(p['name'])>120: raise ValueError('invalid name')
    for k in ('seed','train_seed','holdout_seed'):
        if type(p[k]) is not int or not 0<=p[k]<2**32: raise ValueError('invalid seed')
    if p['train_seed']==p['holdout_seed']: raise ValueError('holdout seed must differ')
    for k,lo,hi in [('attempts_per_arm',1,24),('plateau',1,23),('attempt_timeout_seconds',1,120),('campaign_timeout_seconds',1,1200)]:
        if type(p[k]) is not int or not lo<=p[k]<=hi: raise ValueError('invalid '+k)
    return dict(p)

def load(path):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise ValueError('duplicate key '+k)
            d[k]=v
        return d
    with Path(path).open('rb') as f: raw=f.read(16385)
    if len(raw)>16384: raise ValueError('plan too large')
    return validate_plan(json.loads(raw,object_pairs_hook=unique))

def prepare(p):
    p=validate_plan(p)
    train=st.fixtures(p['train_seed']); hold=st.fixtures(p['holdout_seed'])
    # Remove duplicates of actual training inputs. Do not count repeated fixtures as fresh evidence.
    train_keys={canonical([c['n'],c['clauses']]) for c in train}
    hold=[c for c in hold if canonical([c['n'],c['clauses']]) not in train_keys]
    spec={'plan':p,'source_sha256':source_digest(),'train_sha256':digest(canonical(train)), 'holdout_sha256':digest(canonical(hold)), 'train_cases':len(train),'holdout_cases':len(hold),'provider_calls':0,'generated_code':False,'max_evaluations':2*p['attempts_per_arm']+2,'objective':'minimize recursive requests on fixed training suite'}
    return spec|{'approval_digest':digest(canonical(spec))},train,hold

def order_for(p):
    order=st.space(); random.Random(p['seed']).shuffle(order); return order

def evaluate_worker(cases,s,timeout):
    proc=subprocess.run([sys.executable,'-m','axiom.loop_worker'],input=canonical({'cases':cases,'strategy':s}),capture_output=True,text=True,timeout=timeout,check=True)
    if len(proc.stdout)>2_000_000: raise ValueError('worker output oversized')
    return json.loads(proc.stdout)

def run(p,approval,out):
    spec,train,hold=prepare(p)
    if not hmac.compare_digest(spec['approval_digest'],approval): raise ValueError('approval mismatch; preview again')
    root=Path(out); root.mkdir(parents=True,exist_ok=False) # new directory per run; no overwrite or implicit resume
    blobs=BlobStore(root/'blobs'); ledger=Ledger(root/'ledger.db'); started=time.monotonic(); deadline=started+p['campaign_timeout_seconds']
    history={a:[] for a in ('adaptive','blind')}; winners={}; reason='completed'; order=order_for(p)
    try:
        train_ref=blobs.put(train); hold_ref=blobs.put(hold)
        ledger.append('loop.started',{'spec':spec,'train_ref':train_ref,'holdout_ref':hold_ref,'environment':{'python':platform.python_version(),'system':platform.system(),'machine':platform.machine()}})
        expected=st.reference(train)
        train_oracle=blobs.put(expected)
        ledger.append('loop.oracle',{'split':'train','input_ref':train_ref,'oracle_ref':train_oracle})
        def one(arm,split,idx,s,decision,cases,expected,input_ref,oracle_ref):
            if source_digest()!=spec['source_sha256']: raise ValueError('source changed')
            remaining=deadline-time.monotonic()
            if remaining<=0: raise TimeoutError('campaign deadline')
            info={'arm':arm,'split':split,'index':idx,'strategy':s,'decision':decision,'input_ref':input_ref,'oracle_ref':oracle_ref}
            ledger.append('loop.attempt.started',info)
            try:
                before=time.perf_counter_ns(); rows=evaluate_worker(cases,s,min(remaining,p['attempt_timeout_seconds'])); elapsed=time.perf_counter_ns()-before
                if source_digest()!=spec['source_sha256']: raise ValueError('source changed during execution')
                receipt=st.verify(cases,expected,rows)
                receipt_ref=blobs.put(info|receipt|{'output_ref':blobs.put(rows),'source_sha256':spec['source_sha256']})
                record=info|receipt|{'receipt_ref':receipt_ref,'elapsed_ns':elapsed}
                ledger.append('loop.attempt.verified',record)
                print(arm,split,idx,receipt['verdict'],receipt['metrics']['requests'] if receipt['metrics'] else 'rejected',flush=True)
                return record
            except BaseException as e:
                ledger.append('loop.attempt.failed',info|{'error':type(e).__name__}); raise
        # Interleave arms so wall-clock load is less confounded by run order. Neither can read the other's history.
        for idx in range(1,p['attempts_per_arm']+1):
            for arm in ('adaptive','blind'):
                s,decision=st.choose(order,history[arm],arm,p['plateau'])
                row=one(arm,'train',idx,s,decision,train,expected,train_ref,train_oracle)
                history[arm].append(row)
        frozen={}
        for arm,rows in history.items():
            valid=[x for x in rows if x['verdict']=='finite_pass']
            if not valid: raise ValueError('no eligible incumbent: '+arm)
            winner=min(valid,key=lambda x:x['metrics']['requests'])
            # Freeze training winner before evaluating holdout. Never feed holdout into selection.
            ledger.append('loop.winner.frozen',{'arm':arm,'training_receipt_ref':winner['receipt_ref'],'strategy':winner['strategy']})
            frozen[arm]=winner
        hold_expected=st.reference(hold); hold_oracle=blobs.put(hold_expected)
        ledger.append('loop.oracle',{'split':'holdout','input_ref':hold_ref,'oracle_ref':hold_oracle})
        for arm,winner in frozen.items():
            result=one(arm,'holdout',1,winner['strategy'],'frozen_training_winner',hold,hold_expected,hold_ref,hold_oracle)
            winners[arm]={'train':winner,'holdout':result}
        if any(x['holdout']['verdict']!='finite_pass' for x in winners.values()): reason='holdout_rejected'
    except (KeyboardInterrupt,TimeoutError,subprocess.TimeoutExpired,subprocess.CalledProcessError,OSError,ValueError) as e:
        reason='cancelled' if isinstance(e,KeyboardInterrupt) else type(e).__name__
        print('Loop stopped:',reason,file=sys.stderr)
    finally:
        ledger.append('loop.finished',{'reason':reason,'training_attempts':{a:len(v) for a,v in history.items()},'winners':{a:x['train']['receipt_ref'] for a,x in winners.items()}})
        ledger.close()
    report={'schema_version':'loop-report-1','spec':spec,'reason':reason,'history':history,'winners':winners,'elapsed_seconds':round(time.monotonic()-started,3),'claims':'Finite fixture observations. Recursive requests are not runtime, bit complexity, or a proof. No AI or generated code.'}
    (root/'report.pending').write_text(json.dumps(report,indent=2),encoding='utf-8')
    os.replace(root/'report.pending',root/'report.json')
    return report

def replay(root):
    root=Path(root); blobs=BlobStore(root/'blobs'); ledger=Ledger(root/'ledger.db',readonly=True)
    try:
        events=ledger.events()
        if not ledger.validate(events): raise ValueError('ledger integrity failure')
    finally: ledger.close()
    if not events or events[0]['kind']!='loop.started' or events[-1]['kind']!='loop.finished': raise ValueError('incomplete ledger; no implicit resume')
    start=events[0]['payload']; spec=start['spec']; p=spec['plan']; current,_,_=prepare(p)
    if spec!=current: raise ValueError('source, fixture or plan differs; use original source revision')
    if start['train_ref']!=spec['train_sha256'] or start['holdout_ref']!=spec['holdout_sha256']: raise ValueError('input reference mismatch')
    history={a:[] for a in ('adaptive','blind')}; hold_seen=set(); frozen={}; checked=0
    oracle={}; order=order_for(p)
    for e in events:
        a=e['payload']; kind=e['kind']
        if kind=='loop.oracle':
            split=a['split']
            if split not in ('train','holdout') or split in oracle: raise ValueError('invalid oracle sequence')
            if split=='holdout' and set(frozen)!={'adaptive','blind'}: raise ValueError('holdout before winners frozen')
            expected_ref=spec['train_sha256' if split=='train' else 'holdout_sha256']
            if a['input_ref']!=expected_ref: raise ValueError('oracle input mismatch')
            vals=blobs.get(a['oracle_ref']); cases=blobs.get(a['input_ref'])
            if vals!=st.reference(cases): raise ValueError('oracle mismatch')
            oracle[split]=(cases,vals,a['oracle_ref'])
        elif kind=='loop.winner.frozen':
            if a['arm'] in frozen or any(len(v)!=p['attempts_per_arm'] for v in history.values()): raise ValueError('invalid winner sequence')
            valid=[x for x in history[a['arm']] if x['verdict']=='finite_pass']; best=min(valid,key=lambda x:x['metrics']['requests'])
            if a['training_receipt_ref']!=best['receipt_ref'] or a['strategy']!=best['strategy']: raise ValueError('winner mismatch')
            frozen[a['arm']]=best['strategy']
        elif kind=='loop.attempt.verified':
            arm=a['arm']; split=a['split']; cases,vals,ref=oracle[split]
            if a['oracle_ref']!=ref or a['input_ref']!=spec['train_sha256' if split=='train' else 'holdout_sha256']: raise ValueError('wrong evidence scope')
            if split=='train':
                if frozen or len(history[arm])>=p['attempts_per_arm']: raise ValueError('training after freeze or over budget')
                s,d=st.choose(order,history[arm],arm,p['plateau'])
                if a['index']!=len(history[arm])+1 or a['strategy']!=s or a['decision']!=d: raise ValueError('selection mismatch')
            else:
                if arm in hold_seen or frozen.get(arm)!=a['strategy']: raise ValueError('holdout selection mismatch')
                hold_seen.add(arm)
            r=blobs.get(a['receipt_ref']); rows=blobs.get(r['output_ref'])
            if rows!=st.evaluate(cases,a['strategy']): raise ValueError('candidate output replay mismatch')
            verdict=st.verify(cases,vals,rows)
            info={k:a[k] for k in ('arm','split','index','strategy','decision','input_ref','oracle_ref')}
            if r!=info|verdict|{'output_ref':r['output_ref'],'source_sha256':spec['source_sha256']} or any(a[k]!=v for k,v in verdict.items()): raise ValueError('receipt mismatch')
            if split=='train': history[arm].append(a)
            checked+=len(cases)
    if events[-1]['payload']['reason']=='completed' and (any(len(v)!=p['attempts_per_arm'] for v in history.values()) or hold_seen!={'adaptive','blind'}): raise ValueError('completed campaign coverage mismatch')
    return {'ledger':'PASS','replayed_evaluations':sum(len(v) for v in history.values())+len(hold_seen),'fixture_results_rechecked':checked,'terminal_reason':events[-1]['payload']['reason'],'note':'Local consistency and deterministic replay, not signed authenticity.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('plan'); p.add_argument('manifest')
    p=sub.add_parser('run'); p.add_argument('manifest'); p.add_argument('--approve-digest',required=True); p.add_argument('--out',required=True)
    p=sub.add_parser('replay'); p.add_argument('directory')
    a=parser.parse_args()
    try:
        if a.cmd=='plan': print(json.dumps(prepare(load(a.manifest))[0],indent=2)); return 0
        if a.cmd=='replay': print(json.dumps(replay(a.directory),indent=2)); return 0
        r=run(load(a.manifest),a.approve_digest,a.out); print(r['reason']); return 0 if r['reason']=='completed' else 1
    except (ValueError,OSError,KeyError,TypeError) as e: print(str(e),file=sys.stderr); return 1

if __name__=='__main__': raise SystemExit(main())
