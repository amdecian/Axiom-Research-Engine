"""Finite allowlisted developer qualification jobs. No model calls or publication.

The repository and Actions workflow are the outer trust boundary. This is not
an arbitrary-code sandbox. No metered product is called by this program.
"""
import argparse,json,os,platform,signal,subprocess,sys,time,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROFILES={
    'quick': (['scripts/qualify.py'],300),
    'loop-replay': (['scripts/qualify_loop.py'],300),
    'pattern-regression': (['-m','unittest','discover','-s','tests','-p','test_patterns.py','-v'],60),
    'portal-check': (['scripts/build_portal.py','--check'],30),
}


def validate_event(event, name, ref, runner):
    repo=event.get('repository',{})
    if repo.get('private') is not False or repo.get('visibility') not in ('public',None): raise ValueError('public repository required')
    if runner!='github-hosted': raise ValueError('GitHub-hosted runner required')
    if name not in ('push','pull_request','workflow_dispatch'): raise ValueError('unsupported event')
    if name in ('push','workflow_dispatch') and ref!='refs/heads/main': raise ValueError('main branch required')


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--profile',choices=PROFILES,required=True); a=p.parse_args()
    if os.getenv('GITHUB_ACTIONS')=='true':
        with open(os.environ['GITHUB_EVENT_PATH'],encoding='utf-8') as f: event=json.load(f)
        validate_event(event,os.environ['GITHUB_EVENT_NAME'],os.environ['GITHUB_REF'],os.environ.get('RUNNER_ENVIRONMENT'))
        if a.profile not in ('quick','portal-check') and os.environ['GITHUB_EVENT_NAME']!='workflow_dispatch': raise ValueError('extended tests require manual dispatch')
    args,limit=PROFILES[a.profile]; start=time.monotonic()
    if shutil.disk_usage(ROOT).free<512*1024**2: raise ValueError('insufficient working disk')
    # Only trusted registered programs. Clean inherited provider/GH tokens, not a sandbox.
    env={k:v for k,v in os.environ.items() if k in {'PATH','HOME','USERPROFILE','SYSTEMROOT','WINDIR','TEMP','TMP','TMPDIR','LANG','LC_ALL','PYTHONIOENCODING','PATHEXT','COMSPEC','APPDATA','LOCALAPPDATA','LD_LIBRARY_PATH','DYLD_LIBRARY_PATH'} }
    env['PYTHONIOENCODING']='utf-8'; env['PYTHONUNBUFFERED']='1'
    kw={}; r=None
    if platform.system()=='Linux':
        import resource as r
        def limits():
            # Per-process limits; not aggregate memory/disk limits or hostile code containment.
            r.setrlimit(r.RLIMIT_AS,(3*1024**3,3*1024**3)); r.setrlimit(r.RLIMIT_FSIZE,(64*1024**2,64*1024**2))
            r.setrlimit(r.RLIMIT_CPU,(limit,limit+5))
        kw={'start_new_session':True,'preexec_fn':limits}
    code=1; result='failed'
    proc=subprocess.Popen([sys.executable,*args],cwd=ROOT,env=env,**kw)
    try:
        code=proc.wait(timeout=limit); result='passed' if code==0 else 'failed'
    except (subprocess.TimeoutExpired,KeyboardInterrupt):
        if kw:
            try: os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError: pass
        else: proc.kill()
        proc.wait(); code=1; result='timeout_or_cancelled'
    metrics={'profile':a.profile,'status':result,'elapsed_seconds':round(time.monotonic()-start,3),'python':platform.python_version(),'platform':platform.system(),'machine':platform.machine(),'provider_calls':0,'artifacts_uploaded':0,'timeout_seconds':limit,'source_commit':os.getenv('GITHUB_SHA','local-uncommitted')}
    if r:
        u=r.getrusage(r.RUSAGE_CHILDREN); metrics.update(child_user_cpu_seconds=round(u.ru_utime,3),child_system_cpu_seconds=round(u.ru_stime,3),max_child_rss_kib=u.ru_maxrss)
    print(json.dumps(metrics,sort_keys=True),flush=True)
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a',encoding='utf-8') as f: f.write('## AXIOM qualification\n\n```json\n'+json.dumps(metrics,indent=2)+'\n```\n\nFinite tests only; child RSS is not total concurrent RAM. No autonomous research.\n')
    return 0 if code==0 else 1

if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,OSError,KeyError) as e: print('Qualification stopped:',e,file=sys.stderr); sys.exit(1)
