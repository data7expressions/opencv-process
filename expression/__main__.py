import re
from .core import *

if __name__ == "__main__":
    exp = Manager()

# context = {"a":"1","b":2,"c":{"a":4,"b":5}}

# context = {"a":9,"b":4,"c":{"a":4,"b":5}}
# # result=exp.solve('a*3==b+1',context)
# result=exp.getEnum('DayOfWeek')
# result=manager.solve('"a/b"',context)
# result=manager.solve('DayOfWeek',context)
# print(result)
# print(context)
context = {"a":1,"b":2}

op1 = exp.parse('a+1')
op2 = exp.parse('b')
op3 = op1+op2


print(op3.eval({"a":1,"b":2}))
print(op3.eval({"a":5,"b":2}))







