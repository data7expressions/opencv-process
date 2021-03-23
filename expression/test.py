import unittest
from expression.core import exp

class TestExpression(unittest.TestCase):

    def test_arithmetic(self):
        self.assertEqual(exp.solve('1+1'),1+1)
        self.assertEqual(exp.solve('3+2-1'),3+2-1) 
        self.assertEqual(exp.solve('3*4-1'),3*4-1)
        self.assertEqual(exp.solve('1+4*2'),1+4*2)
        self.assertEqual(exp.solve('4+4+2+50+600'),4+4+2+50+600)
        self.assertEqual(exp.solve('1-2-5'),1-2-5)
        self.assertEqual(exp.solve('(1+4)*2'),(1+4)*2)
        self.assertEqual(exp.solve('(2+3)*2'),(2+3)*2)
        self.assertEqual(exp.solve('2*(3+2)'),2*(3+2))
        self.assertEqual(exp.solve('2*(3+2)*(2+2)'),2*(3+2)*(2+2))
        self.assertEqual(exp.solve('1+2*3*4'),1+2*3*4)  
        self.assertEqual(exp.solve('2*3+4*5'),2*3+4*5)
        self.assertEqual(exp.solve('(1+(2**3)*4'),(1+(2**3)*4))
        self.assertEqual(exp.solve('1+2**3*4'),1+2**3*4) 
        self.assertEqual(exp.solve('1+2**(3*4)'),1+2**(3*4))

    def test_comparisons(self):         
        self.assertEqual(exp.solve('3>2'),3>2)
        self.assertEqual(exp.solve('3>2*2'),3>2*2)
        self.assertEqual(exp.solve('-3>2*2'),-3>2*22)
        self.assertEqual(exp.solve('4>=2*2'),4>=2*2)
        self.assertEqual(exp.solve('3<=2*2'),3<=2*2)
        self.assertEqual(exp.solve('3!=2*2'),3!=2*2)
        self.assertEqual(exp.solve('4!=2*2'),4!=2*2)
        self.assertEqual(exp.solve('-4!=2*2'),-4!=2*2)
        self.assertEqual(exp.solve('-4==-2*2'),-4==-2*2)
        self.assertEqual(exp.solve('-4==-(2*2)'),-4==-(2*2))

    def test_variables(self):
        self.assertEqual(exp.solve('a>b',{"a":1,"b":2}),False)
        self.assertEqual(exp.solve('a+b',{"a":1,"b":2}),3)
        # self.assertEqual(exp.solve('-a*b',{"a":1,"b":2}),-3)
        

    def test_strings(self):
        self.assertEqual(exp.solve('"a"'),"a") 
        self.assertEqual(exp.solve('"a"<"b"'),"a"<"b") 
        self.assertEqual(exp.solve('"a ""b"" "<"b"'),"a ""b"" "<"b") 


def test():
    unittest.main()