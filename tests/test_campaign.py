import json, subprocess, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from axiom import campaign
from axiom.store import Ledger

class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.db=self.root/'test.db'; self.ledger=Ledger(self.db)
        self.plan={'schema_version':'offline-1','name':'test','strategies':['sat.components'],'seeds':[77],'attempt_timeout_seconds':10,'campaign_timeout_seconds':20}
    def tearDown(self): self.ledger.close(); self.tmp.cleanup()
    def write(self,body):
        p=self.root/'plan.json'; p.write_text(json.dumps(body)); return p
    def test_plan(self): self.assertEqual(campaign.load_plan(self.write(self.plan)),self.plan)
    def test_reject_fields(self):
        for changes in [{'seeds':[True]},{'seeds':[1,1]},{'strategies':['shell']},{'schema_version':'future'},{'attempt_timeout_seconds':0},{'network':True},{'name':' '},{'campaign_timeout_seconds':1201}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError): campaign.load_plan(self.write(self.plan|changes))
    def test_duplicate_keys(self):
        p=self.root/'dup.json'; p.write_text('{"name":"a","name":"b"}');
        with self.assertRaises(ValueError): campaign.load_plan(p)
    def test_oversize(self):
        p=self.root/'big.json'; p.write_bytes(b' '*16385)
        with self.assertRaises(ValueError): campaign.load_plan(p)
    def test_approval(self):
        approval=campaign.preview(self.plan)['approval_digest']
        with self.assertRaises(ValueError): campaign.run(self.ledger,self.plan|{'seeds':[1]},approval)
        self.assertEqual(self.ledger.events(),[])
    def test_success(self):
        result=campaign.run(self.ledger,self.plan,campaign.preview(self.plan)['approval_digest'])
        self.assertEqual(result['reason'],'completed'); self.assertEqual(result['verified_attempts'],1); self.assertTrue(self.ledger.validate()); self.assertEqual(self.ledger.snapshot()['attempts'][0]['result']['passed'],80)
    def test_timeout(self):
        with patch('axiom.campaign.subprocess.run',side_effect=subprocess.TimeoutExpired('worker',1)):
            r=campaign.run(self.ledger,self.plan,campaign.preview(self.plan)['approval_digest'])
        self.assertEqual(r['reason'],'attempt_timeout'); self.assertEqual(r['failed_attempts'],1); self.assertEqual(self.ledger.snapshot()['attempts'],[])
        self.assertEqual(self.ledger.events()[-1]['kind'],'campaign.stopped')
    def test_worker_failure(self):
        with patch('axiom.campaign.subprocess.run',side_effect=subprocess.CalledProcessError(1,'worker')):
            r=campaign.run(self.ledger,self.plan,campaign.preview(self.plan)['approval_digest'])
        self.assertEqual(r['reason'],'worker_error')
    def test_negative_control(self):
        p=self.plan|{'strategies':['coef.omit_h']}; r=campaign.run(self.ledger,p,campaign.preview(p)['approval_digest'])
        self.assertEqual(r['reason'],'completed'); self.assertEqual(self.ledger.snapshot()['attempts'][0]['result']['verdict'],'counterexample')
    def test_concurrent_approval(self):
        self.ledger.append('attempt.verified',{'attempt_id':'a','strategy':'sat.components','result':{'verdict':'finite_pass'}})
        def approve(_):
            l=Ledger(self.db)
            try: l.approve('a'); return True
            except ValueError: return False
            finally: l.close()
        with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(approve,range(2)))
        self.assertEqual(sum(results),1); self.assertTrue(self.ledger.validate())
