import json, tempfile, unittest, itertools, subprocess
from pathlib import Path
from unittest.mock import patch
from axiom import strategy as s, loop
from axiom.blobstore import BlobStore
from axiom.algorithms import sat_oracle
from axiom.store import Ledger

class StrategyTests(unittest.TestCase):
    def test_space(self):
        self.assertEqual(len({s.key(x) for x in s.space()}),24)
    def test_all_strategies_exhaustive_two_vars(self):
        clauses=[(),(1,),(-1,),(2,),(-2,),(1,2),(1,-2),(-1,2),(-1,-2)]
        for mask in range(512):
            f=[c for i,c in enumerate(clauses) if mask>>i&1]; expected=sat_oracle(2,f)[0]
            for cfg in s.space(): self.assertEqual(s.count(2,f,cfg)['count'],expected)
    def test_signed_duplicate_and_free_vars(self):
        for cfg in s.space():
            self.assertEqual(s.count(5,[(1,-1),(2,2),(-2,3)],cfg)['count'],8)
            self.assertEqual(s.count(0,[],cfg)['count'],1)
    def test_strategy_validation(self):
        for bad in [s.BASELINE|{'branch':'shell'},s.BASELINE|{'memo':1},s.BASELINE|{'code':'x'}]:
            with self.assertRaises(ValueError): s.validate(bad)
    def test_counterexample(self):
        cases=[{'n':1,'clauses':[[1]],'family':'x'}]; row=s.evaluate(cases,s.BASELINE); row[0]['count']=0
        r=s.verify(cases,[1],row); self.assertEqual(r['verdict'],'counterexample'); self.assertEqual(r['counterexample']['expected'],1)
    def test_malformed_worker_data(self):
        cases=[{'n':1,'clauses':[[1]],'family':'x'}]; row=s.evaluate(cases,s.BASELINE); row[0]['requests']=False
        with self.assertRaises(ValueError): s.verify(cases,[1],row)
    def test_diversity(self):
        history=[{'strategy':s.BASELINE,'verdict':'finite_pass','metrics':{'requests':1}}, {'strategy':s.BASELINE|{'unit':True},'verdict':'finite_pass','metrics':{'requests':2}}]
        nxt,why=s.choose(s.space(),history,'adaptive',1); self.assertEqual(why,'plateau_diversity'); self.assertEqual(min(s.distance(nxt,x['strategy']) for x in history),3)

class LoopTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.out=self.root/'run'; self.p={'schema_version':'loop-1','name':'test','seed':77,'train_seed':1,'holdout_seed':2,'attempts_per_arm':2,'plateau':1,'attempt_timeout_seconds':10,'campaign_timeout_seconds':60}
    def tearDown(self): self.tmp.cleanup()
    def test_plan_guards(self):
        for bad in [{'attempts_per_arm':25},{'seed':True},{'holdout_seed':1},{'name':' '},{'network':True},{'plateau':0}]:
            with self.assertRaises(ValueError): loop.prepare(self.p|bad)
    def test_duplicate_key(self):
        p=self.root/'dup.json'; p.write_text('{"name":"a","name":"b"}');
        with self.assertRaises(ValueError): loop.load(p)
    def test_approval_rejects_changed_plan(self):
        spec,*_=loop.prepare(self.p)
        with self.assertRaises(ValueError): loop.run(self.p|{'seed':78},spec['approval_digest'],self.out)
        self.assertFalse(self.out.exists())
    def test_no_overwrite(self):
        self.out.mkdir()
        with self.assertRaises(FileExistsError): loop.run(self.p,loop.prepare(self.p)[0]['approval_digest'],self.out)
    def test_blob_integrity(self):
        b=BlobStore(self.root/'blobs'); key=b.put({'v':2}); self.assertEqual(key,b.put({'v':2})); self.assertEqual(b.get(key),{'v':2})
        with self.assertRaises(ValueError): b.get('../escape')
        (b.root/(key+'.json')).write_text('corrupt')
        with self.assertRaises(ValueError): b.get(key)
    def test_complete_replay_and_tamper(self):
        spec,*_=loop.prepare(self.p); result=loop.run(self.p,spec['approval_digest'],self.out)
        self.assertEqual(result['reason'],'completed'); self.assertEqual(loop.replay(self.out)['replayed_evaluations'],6)
        l=Ledger(self.out/'ledger.db',readonly=True); events=l.events(); l.close()
        self.assertLess(max(e['seq'] for e in events if e['kind']=='loop.winner.frozen'),next(e['seq'] for e in events if e['kind']=='loop.oracle' and e['payload']['split']=='holdout'))
        ref=result['history']['adaptive'][0]['receipt_ref']; (self.out/'blobs'/(ref+'.json')).write_text('{}')
        with self.assertRaises(ValueError): loop.replay(self.out)
    def test_timeout_records_failure(self):
        spec,*_=loop.prepare(self.p)
        with patch('axiom.loop.evaluate_worker',side_effect=subprocess.TimeoutExpired('worker',1)):
            r=loop.run(self.p,spec['approval_digest'],self.out)
        self.assertEqual(r['reason'],'TimeoutExpired'); self.assertEqual(r['history']['adaptive'],[])
        self.assertEqual(loop.replay(self.out)['replayed_evaluations'],0)
    def test_holdout_disjoint(self):
        _,a,b=loop.prepare(self.p)
        keys=lambda rows:{json.dumps([c['n'],c['clauses']]) for c in rows}
        self.assertFalse(keys(a)&keys(b))
