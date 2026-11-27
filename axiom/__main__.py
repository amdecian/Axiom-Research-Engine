import argparse,json,uuid,time,hashlib,sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from .store import Ledger
from . import algorithms, campaign

def main():
    p=argparse.ArgumentParser(description='Axiom offline mathematical research fixture harness'); p.add_argument('--db',default='research.db'); sub=p.add_subparsers(dest='cmd',required=True)
    d=sub.add_parser('demo',help='explicit finite run, trusted built-in strategies only'); d.add_argument('--seed',type=int,default=20261127); d.add_argument('--max-attempts',type=int,choices=[1,2,3],default=3)
    a=sub.add_parser('approve'); a.add_argument('attempt_id'); sub.add_parser('audit'); s=sub.add_parser('snapshot'); s.add_argument('--out',default='snapshot.json'); w=sub.add_parser('serve'); w.add_argument('--port',type=int,default=8765)
    pl=sub.add_parser('plan',help='preview a finite trusted campaign, no execution'); pl.add_argument('manifest')
    rn=sub.add_parser('run',help='run an explicitly hash-approved offline campaign'); rn.add_argument('manifest'); rn.add_argument('--approve-digest',required=True)
    args=p.parse_args()
    if args.cmd=='plan':
        try: print(json.dumps(campaign.preview(campaign.load_plan(args.manifest)),indent=2)); return 0
        except (ValueError,OSError) as e: print(str(e),file=sys.stderr); return 1
    ledger=Ledger(args.db)
    try:
        if args.cmd=='demo':
            if not ledger.validate(): raise ValueError('ledger integrity check failed')
            campaign_id=str(uuid.uuid4()); code_hash=hashlib.sha256(Path(algorithms.__file__).read_bytes()).hexdigest()
            ledger.append('campaign.started',dict(campaign_id=campaign_id,seed=args.seed,max_attempts=args.max_attempts,mode='offline_fixture',code_sha256=code_hash))
            for idx,strategy in enumerate(algorithms.STRATEGIES):
                if idx>=args.max_attempts: break
                aid=str(uuid.uuid4()); ledger.append('attempt.started',dict(attempt_id=aid,campaign_id=campaign_id,strategy=strategy)); start=time.perf_counter_ns()
                try: result=algorithms.verify(strategy,args.seed)
                except Exception as ex:
                    ledger.append('attempt.failed',dict(attempt_id=aid,campaign_id=campaign_id,error=type(ex).__name__)); raise
                ledger.append('attempt.verified',dict(attempt_id=aid,campaign_id=campaign_id,strategy=strategy,seed=args.seed,code_sha256=code_hash,elapsed_ns=time.perf_counter_ns()-start,result=result)); print(aid,strategy,result['verdict'],f"{result['passed']}/{result['total']}")
            ledger.append('campaign.completed',dict(campaign_id=campaign_id))
        elif args.cmd=='run':
            outcome=campaign.run(ledger,campaign.load_plan(args.manifest),args.approve_digest); print(json.dumps(outcome)); return 0 if outcome['reason']=='completed' else 1
        elif args.cmd=='approve': print(json.dumps(ledger.approve(args.attempt_id),indent=2))
        elif args.cmd=='audit': print('PASS' if ledger.validate() else 'FAIL'); return 0 if ledger.validate() else 1
        elif args.cmd=='snapshot': Path(args.out).write_text(json.dumps(ledger.snapshot(),indent=2),encoding='utf-8'); print(args.out)
        elif args.cmd=='serve':
            ledger.close(); path=str(Path(args.db).resolve()); ui=Path(__file__).parent/'dashboard.html'
            class Handler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path=='/': body=ui.read_bytes(); content='text/html; charset=utf-8'
                    elif self.path=='/api/v1/snapshot':
                        l=Ledger(path,readonly=True)
                        try: body=json.dumps(l.snapshot()).encode()
                        finally: l.close()
                        content='application/json; charset=utf-8'
                    else: self.send_error(404); return
                    self.send_response(200); self.send_header('Content-Type',content); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(body)
            server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler); print(f'Local read-only dashboard: http://127.0.0.1:{args.port} (Ctrl+C to stop)',flush=True)
            try: server.serve_forever()
            except KeyboardInterrupt: pass
            finally: server.server_close()
            return 0
    except (ValueError,OSError) as e: print(str(e),file=sys.stderr); return 1
    finally:
        try: ledger.close()
        except Exception: pass
    return 0
if __name__=='__main__': raise SystemExit(main())
