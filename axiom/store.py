"""Local evidence ledger. Hash chain detects edits, not privileged rewriting."""
import hashlib,json,sqlite3,datetime,uuid
from pathlib import Path

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
class Ledger:
    def __init__(self,path,readonly=False):
        self.db=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True) if readonly else sqlite3.connect(path); self.db.execute('PRAGMA busy_timeout=5000')
        if readonly: return
        self.db.execute('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL, ts TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL, prev TEXT NOT NULL, hash TEXT NOT NULL)')
        self.db.executescript("CREATE TRIGGER IF NOT EXISTS no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'append only'); END; CREATE TRIGGER IF NOT EXISTS no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'append only'); END;")
    def close(self): self.db.close()
    def _append_locked(self,kind,payload):
        seq,prev=self.db.execute('SELECT seq,hash FROM events ORDER BY seq DESC LIMIT 1').fetchone() or (0,'0'*64)
        e=dict(seq=seq+1,event_id=str(uuid.uuid4()),ts=utc(),kind=kind,payload=payload,prev=prev)
        h=digest(canonical(e)); self.db.execute('INSERT INTO events VALUES(?,?,?,?,?,?,?)',(e['seq'],e['event_id'],e['ts'],kind,canonical(payload),prev,h))
        return e|{'hash':h}
    def append(self,kind,payload):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            return self._append_locked(kind,payload)
    def events(self):
        return [dict(seq=s,event_id=i,ts=t,kind=k,payload=json.loads(p),prev=b,hash=h) for s,i,t,k,p,b,h in self.db.execute('SELECT * FROM events ORDER BY seq')]
    def validate(self,events=None):
        prev='0'*64
        for i,e in enumerate(self.events() if events is None else events,1):
            body={k:v for k,v in e.items() if k!='hash'}
            if e['seq']!=i or e['prev']!=prev or digest(canonical(body))!=e['hash']: return False
            prev=e['hash']
        return True
    def approve(self,attempt_id):
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            if not self.validate(): raise ValueError('invalid ledger')
            events=self.events(); existing=[e for e in events if e['kind']=='attempt.verified' and e['payload']['attempt_id']==attempt_id]
            if len(existing)!=1: raise ValueError('verified attempt not found')
            if any(e['kind']=='memory.approved' and e['payload']['attempt_id']==attempt_id for e in events): raise ValueError('already approved')
            p=existing[0]['payload']; v=p['result']['verdict']
            if v not in ('finite_pass','counterexample'): raise ValueError('not promotable')
            text=('Finite fixture pass only: '+p['strategy'] if v=='finite_pass' else 'Rejected by concrete counterexample: '+p['strategy'])
            return self._append_locked('memory.approved',dict(attempt_id=attempt_id,evidence_event=existing[0]['event_id'],grade=v,lesson=text,source_hash=existing[0]['hash']))
    def snapshot(self):
        es=self.events(); attempts=[e['payload']|{'evidence_hash':e['hash']} for e in es if e['kind']=='attempt.verified']; memory=[e['payload'] for e in es if e['kind']=='memory.approved']
        return dict(schema_version='0.1',mode='offline_fixture',ledger_valid=self.validate(es),attempts=attempts,memory=memory,events=es)
