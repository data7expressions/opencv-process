import re


# TODO: 
#  variables con $
#  resolver precedencia de operadores (exp: * sobre +)
#  uso de parentecis
#  deteccion de funcionnes
#  arrays
#  dictionaries
#  asignaciones de variables
#  separacion por ;
# metodos reduce para resolver previamente las operaciones entre constantes y dejar un solo operando constante

class Constant():
    def __init__(self,value ):
      self._value  = value
    @property
    def value(self): 
        return self._value 
class Variable():
    def __init__(self,name ):
      self._name  = name
      self._context  = None

    @property
    def context(self):
        return self._context
    @context.setter
    def context(self,value):
        self._context=value

    @property
    def value(self):
        return self._context[self._name]
    @value.setter
    def value(self,value):
        self._context[self._name]=value       
class Function():
    def __init__(self,function,args):
      self.args  = args
      self.function  = function

    @property
    def value(self): 
        args=[]
        for p in self.args:args.append(p.value)
        return self.function(*args)
class Operator():
    def __init__(self,operands ):
      self._operands  = operands

    @property
    def operands(self):
        return self._operands


    @property
    def value(self):
        val=self._operands[0].value
        l=len(self._operands)
        i=1
        while i<l:
            val=self.solve(val,self._operands[i].value)
            i+=1
        return val  

    def solve(self,a,b):
        pass 

class ExpManager():
    def __init__(self):
       self.operators={} 
       self.functions={} 
       self.RE_INT = re.compile('^[-+]?[0-9]+$')
       self.RE_FLOAT = re.compile('[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')

    def add(self,k,imp):
        self.operators[k]=imp
    def addFunction(self,k,imp):
        self.functions[k]=imp    

    def new(self,k,operands):
        return self.operators[k](operands)

    def setContext(self,expression,context):
        if 'operands' in expression:
            for p in expression.operands:
                if isinstance(p,Variable):
                    p.context = context
                elif 'operands' in p:
                    self.setContext(p,context)    


    def parse(self,expression):
        operators = set('+-*/')
        buff = []
        lastOperator= None
        alter=None
        operands=[]
        for char in expression: 
            if char in operators:
                if len(buff)==0: 
                    if char == '-':
                       alter = lambda x : x * -1 # example 2*-1
                    else:    
                        lastOperator+=char  # example **,//,==,!= etc
                else:
                    operands.append(self.solveConstant(''.join(buff),alter))
                    if lastOperator != None and lastOperator!=char:
                        operands=[self.new(lastOperator,operands)]                    
                    lastOperator=char
                    buff=[]
            else:
                buff.append(char)

        operands.append(self.solveConstant(''.join(buff),alter))
        return self.new(lastOperator,operands)

    def solveConstant(self,value,alter):
        result=None
        if self.RE_INT.match(value): 
            result= alter(int(value)) if alter!= None else int(value)
        elif self.RE_FLOAT.match(value):
            result=  alter(float(value)) if alter!= None else float(value)
        else:
            result=  alter(value) if alter!= None else value

        return self.new('constant',result)        




class Addition(Operator):
    def solve(self,a,b):
        return a+b 
class Subtraction (Operator):
    def solve(self,a,b):
        return a-b   
class Multiplication(Operator):
    def solve(self,a,b):
        return a*b 
class Division (Operator):
    def solve(self,a,b):
        return a/b  
class Exponentiation(Operator):
    def solve(self,a,b):
        return a**b 
class FloorDivision (Operator):
    def solve(self,a,b):
        return a//b   
class Mod (Operator):
    def solve(self,a,b):
        return a%b 

class Equal(Operator):
    def solve(self,a,b):
        return a==b
class NotEqual(Operator):
    def solve(self,a,b):
        return a!=b          
class GreaterThan(Operator):
    def solve(self,a,b):
        return a>b
class LessThan(Operator):
    def solve(self,a,b):
        return a<b 
class GreaterThanOrEqual(Operator):
    def solve(self,a,b):
        return a>=b
class LessThanOrEqual(Operator):
    def solve(self,a,b):
        return a<=b                

class And(Operator):
    def solve(self,a,b):
        return a and b   
class Or(Operator):
    def solve(self,a,b):
        return a or b 
class Not(Operator):
    @property
    def value(self):
        return not self._operands[0].value

class BitAnd(Operator):
    def solve(self,a,b):
        return a & b 
class BitOr(Operator):
    def solve(self,a,b):
        return a | b
class BitXor(Operator):
    def solve(self,a,b):
        return a ^ b                  
class BitNot(Operator):
    @property
    def value(self):
        return ~ self._operands[0].value
class LeftShift(Operator):
    def solve(self,a,b):
        return a << b   
class RightShift(Operator):
    def solve(self,a,b):
        return a >> b   

def nvl(a,b):
    return a if a else b




expManager = ExpManager()
expManager.add('constant',Constant)
expManager.add('variable',Variable)
expManager.add('function',Function)

expManager.add('+',Addition)
expManager.add('-',Subtraction)
expManager.add('*',Multiplication)
expManager.add('/',Division)
expManager.add('**',Exponentiation)
expManager.add('//',FloorDivision)
expManager.add('%',Mod)

expManager.add('==',Equal)
expManager.add('!=',NotEqual)
expManager.add('>',GreaterThan)
expManager.add('<',LessThan)
expManager.add('>=',GreaterThanOrEqual)
expManager.add('<=',LessThanOrEqual)

expManager.add('&&',And)
expManager.add('||',Or)
expManager.add('!',Not)

expManager.add('&',BitAnd)
expManager.add('|',BitOr)
expManager.add('^!',BitXor)
expManager.add('~',BitNot)
expManager.add('<<',LeftShift)
expManager.add('>>',RightShift)

expManager.addFunction('nvl',nvl)

strExpression= '2+4-1'
context = {"a":1}
expression=expManager.parse(strExpression)
expManager.setContext(expression,context)
result = expression.value
print(result)