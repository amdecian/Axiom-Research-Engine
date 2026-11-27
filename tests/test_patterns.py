import unittest
from axiom.patterns import patterns,direct,mobius,divide_known_multiple,crt_count

class PatternsTests(unittest.TestCase):
    def test_all_signed_patterns(self):
        cases=0
        for k in range(5):
            for w in patterns(k):
                for z in ((0,1,-2,3,0,-1,2,1),(2,-1,0,1,3,-2,1,0),(0,0,1,-1,2,0,-3,4)):
                    for d in range(len(z)):
                        self.assertEqual(direct(w,z,d),mobius(w,z,d)[0],(w,z,d)); cases+=1
        self.assertEqual(cases,576)
    def test_repeated_endpoint(self):
        self.assertEqual(direct((0,1,0),(0,2,3,4),0),29)
        self.assertEqual(mobius((0,1,0),(0,2,3,4),1)[0],0)
    def test_guard(self):
        for w,z,d in [((0,2),(0,1),1),((0,1),(0,1,2),0),((0,1),(0,1),2),((0,1,2,3,4,5),(0,1),1)]:
            with self.assertRaises(ValueError): mobius(w,z,d)
    def test_division(self):
        for k in range(1,7):
            for a in range(-41,42):
                self.assertEqual(divide_known_multiple((11*a)%(11**(k+1)),11,11**k,11**(k+1)),a%(11**k))
        with self.assertRaises(ValueError): divide_known_multiple(1,11,121,1331)
        with self.assertRaises(ValueError): divide_known_multiple(11,11,121,121)
    def test_crt(self):
        for x in range(65): self.assertEqual(crt_count([x%5,x%7,x%11],[5,7,11],6),x)
        for args in [([0],[2],6),([0,0],[5,10],6),([4],[3],1),([6],[7],1)]:
            with self.assertRaises(ValueError): crt_count(*args)
