import unittest
from itertools import combinations
from fractions import Fraction as Q
from axiom.research_math import component_count, polynomial_permanent, polynomial_oracle
from axiom.algorithms import sat_oracle, verify

class ResearchMath(unittest.TestCase):
    def test_component_example(self):
        self.assertEqual(component_count(6,[(1,2),(3,4),(-5,)])[0],18)
    def test_empty(self):
        self.assertEqual(component_count(0,[])[0],1)
        self.assertEqual(component_count(0,[()])[0],0)
    def test_unit_free(self):
        self.assertEqual(component_count(5,[(1,), (1,2,3)])[0],16)
    def test_invalid_literal(self):
        for x in [0,4,-4,True,1.5]:
            with self.subTest(x=x), self.assertRaises(ValueError): component_count(3,[(x,)])
    def test_all_two_variable_cnfs(self):
        cs=[(),(1,),(-1,),(2,),(-2,),(1,2),(1,-2),(-1,2),(-1,-2)]
        for mask in range(1<<len(cs)):
            f=[c for i,c in enumerate(cs) if mask>>i&1]
            self.assertEqual(component_count(2,f)[0],sat_oracle(2,f)[0])
    def test_seeded_sat(self):
        for seed in (0,77,20261127): self.assertEqual(verify('sat.components',seed)['verdict'],'finite_pass')
    def test_polynomial_hand(self):
        M=[[[1,2],[3,4]],[[0,1],[1,0]],[[2,0],[0,3]]]
        self.assertEqual(polynomial_permanent(M,6)[0],(Q(10),Q(5),Q(12),Q(0),Q(6),Q(0)))
    def test_polynomial_empty(self): self.assertEqual(polynomial_permanent([[]],3)[0],(1,0,0))
    def test_polynomial_rational(self):
        M=[[[Q(1,2),Q(-2,3)],[Q(3,5),Q(1,7)]],[[0,1],[1,0]]]
        self.assertEqual(polynomial_permanent(M,4)[0],polynomial_oracle(M,4)[0])
    def test_polynomial_shape(self):
        for M,h in [([],1),([[[1,2]]],1),([[[1.0]]],1),([[[1]]],0)]:
            with self.subTest(M=M,h=h),self.assertRaises(ValueError): polynomial_permanent(M,h)
    def test_seeded_polynomial(self):
        for seed in (0,77,20261127): self.assertEqual(verify('coef.all_orders',seed)['verdict'],'finite_pass')
