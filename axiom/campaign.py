"""Explicit finite offline campaigns. Approval digest binds the plan and trusted source."""
import hashlib
import hmac
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
from .algorithms import STRATEGIES
from .store import canonical, digest

FIELDS = {'schema_version','name','strategies','seeds','attempt_timeout_seconds','campaign_timeout_seconds'}
MAX_BYTES = 16384


def load_plan(path):
    with Path(path).open('rb') as f:
        raw = f.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:
        raise ValueError('plan exceeds 16 KiB')
    def no_duplicates(pairs):
        d={}
        for k,v in pairs:
            if k in d: raise ValueError('duplicate JSON key: '+k)
            d[k]=v
        return d
    try: plan=json.loads(raw,object_pairs_hook=no_duplicates)
    except (UnicodeError,json.JSONDecodeError) as exc: raise ValueError('invalid plan JSON') from exc
    if not isinstance(plan,dict) or set(plan)!=FIELDS or plan['schema_version']!='offline-1':
        raise ValueError('unknown or incomplete offline-1 plan')
    if not isinstance(plan['name'],str) or not plan['name'].strip() or len(plan['name'])>120:
        raise ValueError('invalid campaign name')
    strategies=plan['strategies']; seeds=plan['seeds']
    if not isinstance(strategies,list) or not 1<=len(strategies)<=5 or any(not isinstance(s,str) or s not in STRATEGIES for s in strategies) or len(set(strategies))!=len(strategies):
        raise ValueError('strategies must be unique trusted registry IDs')
    if not isinstance(seeds,list) or not 1<=len(seeds)<=4 or any(type(s) is not int or not 0<=s<=2**32-1 for s in seeds) or len(set(seeds))!=len(seeds):
        raise ValueError('seeds must be unique unsigned 32-bit integers')
    if len(seeds)*len(strategies)>16: raise ValueError('at most 16 attempts')
    for key,maximum in [('attempt_timeout_seconds',120),('campaign_timeout_seconds',1200)]:
        if type(plan[key]) is not int or not 1<=plan[key]<=maximum:
            raise ValueError('invalid '+key)
    return plan


def source_digest():
    files=sorted(Path(__file__).parent.glob('*.py'))
    return digest(canonical({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))


def preview(plan):
    body={'plan':plan,'source_sha256':source_digest(),'attempts':len(plan['seeds'])*len(plan['strategies']),'provider_calls':0,'generated_code':False}
    return body|{'approval_digest':digest(canonical(body))}


def run(ledger,plan,approved):
    spec=preview(plan)
    if not hmac.compare_digest(spec['approval_digest'],approved):
        raise ValueError('approval digest does not match the current plan and source')
    if not ledger.validate(): raise ValueError('ledger integrity check failed')
    cid=str(uuid.uuid4()); deadline=time.monotonic()+plan['campaign_timeout_seconds']; done=0; reason='completed'; failures=0
    ledger.append('campaign.started',{'campaign_id':cid,'name':plan['name'],'seed':plan['seeds'][0],'seeds':plan['seeds'],'max_attempts':spec['attempts'],'mode':'offline_fixture','plan':plan,'code_sha256':spec['source_sha256'],'approval_digest':approved})
    try:
        for seed in plan['seeds']:
            for strategy in plan['strategies']:
                remaining=deadline-time.monotonic()
                if remaining<=0:
                    reason='deadline'; break
                if source_digest()!=spec['source_sha256']:
                    reason='source_changed'; break
                aid=str(uuid.uuid4()); start=time.perf_counter_ns()
                data={'attempt_id':aid,'campaign_id':cid,'strategy':strategy,'seed':seed,'code_sha256':spec['source_sha256']}
                ledger.append('attempt.started',data)
                try:
                    proc=subprocess.run([sys.executable,'-m','axiom.worker',strategy,str(seed)],capture_output=True,text=True,check=True,timeout=min(remaining,plan['attempt_timeout_seconds']))
                    result=json.loads(proc.stdout)
                    if source_digest()!=spec['source_sha256']: raise ValueError('source changed during attempt')
                    if result['verdict'] not in ('finite_pass','counterexample'): raise ValueError('unexpected worker verdict')
                    ledger.append('attempt.verified',data|{'elapsed_ns':time.perf_counter_ns()-start,'result':result})
                    print(aid,strategy,seed,result['verdict'],f"{result['passed']}/{result['total']}",flush=True)
                    done+=1
                except subprocess.TimeoutExpired:
                    ledger.append('attempt.failed',data|{'error':'timeout'}); failures+=1; reason='attempt_timeout'; break
                except (subprocess.CalledProcessError,ValueError,KeyError,OSError):
                    ledger.append('attempt.failed',data|{'error':'worker_error'}); failures+=1; reason='worker_error'; break
                except KeyboardInterrupt:
                    ledger.append('attempt.failed',data|{'error':'cancelled'}); failures+=1; raise
            if reason!='completed': break
    except KeyboardInterrupt:
        reason='cancelled'
    except Exception:
        reason='controller_error'
        raise
    finally:
        ledger.append('campaign.completed' if reason=='completed' else 'campaign.stopped',{'campaign_id':cid,'reason':reason,'verified_attempts':done,'failed_attempts':failures})
    return {'campaign_id':cid,'reason':reason,'verified_attempts':done,'failed_attempts':failures}
