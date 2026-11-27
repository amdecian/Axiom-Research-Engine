import unittest,tempfile,sqlite3
from pathlib import Path
from fractions import Fraction as Q
from axiom.algorithms import *
from axiom.store import Ledger
class Algorithms(unittest.TestCase):
    def test_example(self): self.assertEqual(sat_split(3,[(1,2,3),(-1,2,3)])[0],6)
    def test_unsat(self): self.assertEqual(sat_split(1,[(1,),(-1,)])[0],0)
    def test_free(self): self.assertEqual(sat_split(5,[])[0],32)
    def test_tautology(self): self.assertEqual(sat_split(2,[(1,-1)])[0],4)
    def test_empty_clause(self): self.assertEqual(sat_split(3,[()])[0],0)
    def test_sweep(self): self.assertEqual(verify('sat.cached_split',7)['verdict'],'finite_pass')
    def test_quadratic(self): self.assertEqual(verify('coef.full_quadratic',7)['verdict'],'finite_pass')
    def test_bad(self): self.assertEqual(verify('coef.omit_h',7)['verdict'],'counterexample')
    def test_exact(self): self.assertEqual(quadratic([[Q(1)]],[[Q(0)]],[[Q(2,3)]])[0],Q(2,3))
class Store(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.l=Ledger(str(Path(self.tmp.name)/'test.db'))
    def tearDown(self): self.l.close(); self.tmp.cleanup()
    def test_chain(self): self.l.append('campaign.started',{}); self.l.append('campaign.completed',{}); self.assertTrue(self.l.validate())
    def test_no_edit(self):
        self.l.append('campaign.started',{})
        with self.assertRaises(sqlite3.IntegrityError): self.l.db.execute("UPDATE events SET kind='fake'")
    def test_tamper_detection(self):
        self.l.append('campaign.started',{}); self.l.db.execute('DROP TRIGGER no_update'); self.l.db.execute("UPDATE events SET kind='fake'"); self.assertFalse(self.l.validate())
    def test_unknown(self):
        with self.assertRaises(ValueError): self.l.approve('no')
    def test_approve(self):
        self.l.append('attempt.verified',{'attempt_id':'a','strategy':'coef.full_quadratic','result':{'verdict':'finite_pass'}}); self.l.approve('a'); self.assertEqual(self.l.snapshot()['memory'][0]['grade'],'finite_pass')
        with self.assertRaises(ValueError): self.l.approve('a')
if __name__=='__main__': unittest.main()
