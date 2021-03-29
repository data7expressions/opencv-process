import re
from mgr.base import *

class ExpressionError(Exception):pass

class Operand():
    @property
    def value(self): 
        pass
class Constant(Operand):
    def __init__(self,value,type ):
      self._value  = value
      self._type  = type

    @property
    def value(self): 
        return self._value 

    def __str__(self):
        return str(self._value)
    def __repr__(self):
        return str(self._value)    
class Variable(Operand):
    def __init__(self,name ):
      self._name  = name
      self._names = name.split('.')
      self._context  = None

    @property
    def name(self):
        return self._name

    @property
    def context(self):
        return self._context
    @context.setter
    def context(self,value):
        self._context=value

    @property
    def value(self):
        _value = self._context
        for n in self._names:
            _value=_value[n]
        return _value

    @value.setter
    def value(self,value):
        _value = self._context
        length = len(self._names)
        i=1
        for n in self._names:
            if i == length:
                _value[n]=value
            else:                    
                _value=_value[n]
            i+=1

    def __str__(self):
        return self._name
    def __repr__(self):
        return self._name      
class Operator(Operand):
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
class Function(Operator):
    def __init__(self,mgr,name,args,isChild=False):
      super(Function,self).__init__(args)
      self.mgr  = mgr
      self.name  = name
      self._isChild  = isChild

    @property
    def isChild(self):
        return self._isChild
    @isChild.setter
    def isChild(self,value):
        self._isChild=value
    @property
    def value(self): 
        args=[]
        if self._isChild:
            parent = self._operands.pop(0)
            value = parent.value
            _type = type(value).__name__
            function=self.mgr.getFunction(self.name,_type)            
            for p in self._operands:args.append(p.value)
            args.insert(0,value)            
        else:
            function=self.mgr.getFunction(self.name)
            for p in self._operands:args.append(p.value)    

        return function(*args)
class KeyValue(Operator):
    def __init__(self,name,value:Operand):
      super(KeyValue,self).__init__([value])
      self._name  = name

    @property
    def name(self):
        return self._name  
    @property
    def value(self): 
        return self._operands[0].value
class Array(Operator):
    def __init__(self,elements=[]):
      super(Array,self).__init__([elements])

    @property
    def value(self):
        list= []
        for p in self._operands:
            list.append(p.value)
        return list 
class Object(Operator):
    def __init__(self,attributes=[]):
      super(Object,self).__init__(attributes)

    @property
    def value(self):
        dic= {}
        for p in self._operands:
            dic[p.name]=p.value
        return dic  
class NegativeDecorator(Operator):
    def __init__(self,operand:Operand ):
        super(NegativeDecorator,self).__init__([operand])

    @property
    def value(self): 
        return self._operands[0].value * -1
class NotDecorator(Operator):
    def __init__(self,operand:Operand ):
      super(NotDecorator,self).__init__([operand])

    @property
    def value(self): 
        return not self._operands[0].value 
class IndexDecorator(Operator):
    def __init__(self,operand:Operand,idx:Operand ):
      super(IndexDecorator,self).__init__([operand,idx])        

    @property
    def value(self): 
        return self._operands[0].value[self._operands[1].value]
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
        if not a : return False
        return b
        # return a and b   
class Or(Operator):
    def solve(self,a,b):
        if a : return True
        return b
        # return a or b 
class Not(Operator):
    @property
    def value(self):
        return not self._operands[0].value

class Assigment(Operator):
    @property
    def value(self):
        self._operands[0].value = self._operands[1].value
        return self._operands[0].value
class AssigmentAddition(Operator):
    @property
    def value(self):
        self._operands[0].value += self._operands[1].value
        return self._operands[0].value
class AssigmentSubtraction (Operator):
    @property
    def value(self):
        self._operands[0].value -= self._operands[1].value
        return self._operands[0].value  
class AssigmentMultiplication(Operator):
    @property
    def value(self):
        self._operands[0].value *= self._operands[1].value
        return self._operands[0].value 
class AssigmentDivision (Operator):
    @property
    def value(self):
        self._operands[0].value /= self._operands[1].value
        return self._operands[0].value  
class AssigmentExponentiation(Operator):
    @property
    def value(self):
        self._operands[0].value **= self._operands[1].value
        return self._operands[0].value 
class AssigmentFloorDivision (Operator):
    @property
    def value(self):
        self._operands[0].value //= self._operands[1].value
        return self._operands[0].value   
class AssigmentMod (Operator):
    @property
    def value(self):
        self._operands[0].value %= self._operands[1].value
        return self._operands[0].value 
class AssigmentBitAnd(Operator):
    @property
    def value(self):
        self._operands[0].value &= self._operands[1].value
        return self._operands[0].value 
class AssigmentBitOr(Operator):
    @property
    def value(self):
        self._operands[0].value |= self._operands[1].value
        return self._operands[0].value
class AssigmentBitXor(Operator):
    @property
    def value(self):
        self._operands[0].value ^= self._operands[1].value
        return self._operands[0].value
class AssigmentLeftShift(Operator):
    @property
    def value(self):
        self._operands[0].value <<= self._operands[1].value
        return self._operands[0].value
class AssigmentRightShift(Operator):
    @property
    def value(self):
        self._operands[0].value >>= self._operands[1].value
        return self._operands[0].value

class Manager(metaclass=Singleton):
    def __init__(self):
       self.operators={}
       self.enums={} 
       self.functions={}
       self.initOperators()
       self.initFunctions()
       self.initEnums()
    def initOperators(self):        
        self.add('+',Addition)
        self.add('-',Subtraction)
        self.add('*',Multiplication)
        self.add('/',Division)
        self.add('**',Exponentiation)
        self.add('//',FloorDivision)
        self.add('%',Mod)

        self.add('&',BitAnd)
        self.add('|',BitOr)
        self.add('^',BitXor)
        self.add('~',BitNot)
        self.add('<<',LeftShift)
        self.add('>>',RightShift)

        self.add('==',Equal)
        self.add('!=',NotEqual)
        self.add('>',GreaterThan)
        self.add('<',LessThan)
        self.add('>=',GreaterThanOrEqual)
        self.add('<=',LessThanOrEqual)

        self.add('&&',And)
        self.add('||',Or)
        self.add('!',Not)

        self.add('=',Assigment)
        self.add('+=',AssigmentAddition)
        self.add('-=',AssigmentSubtraction)
        self.add('*=',AssigmentMultiplication)
        self.add('/=',AssigmentDivision)
        self.add('**=',AssigmentExponentiation)
        self.add('//=',AssigmentFloorDivision)
        self.add('%=',AssigmentMod)
        self.add('&=',AssigmentBitAnd)
        self.add('|=',AssigmentBitOr)
        self.add('^=',AssigmentBitXor)
        self.add('<<=',AssigmentLeftShift)
        self.add('>>=',AssigmentRightShift)
    def initFunctions(self): 
        self.addFunction('nvl',lambda a,b: a if a!=None else b )
        # https://docs.python.org/2.5/lib/string-methods.html
        self.addFunction('capitalize',lambda str: str.capitalize(),['str'])
        self.addFunction('count',lambda str,sub,start=None,end=None: str.count(sub,start,end),['str'])
        self.addFunction('decode',lambda str,encoding: str.decode(encoding),['str'])
        self.addFunction('encode',lambda str,encoding: str.encode(encoding),['str'])
        self.addFunction('endswith',lambda str,suffix,start=None,end=None: str.endswith(suffix,start,end),['str'])
        self.addFunction('find',lambda str,sub,start=None,end=None: str.find(sub,start,end),['str'])
        self.addFunction('index',lambda str,sub,start=None,end=None: str.index(sub,start,end),['str'])
        self.addFunction('isalnum',lambda str: str.isalnum(),['str'])
        self.addFunction('isalpha',lambda str: str.isalpha(),['str'])
        self.addFunction('isdigit',lambda str: str.isdigit(),['str'])
        self.addFunction('islower',lambda str: str.islower(),['str'])
        self.addFunction('isspace',lambda str: str.isspace(),['str'])
        self.addFunction('istitle',lambda str: str.istitle(),['str'])
        self.addFunction('isupper',lambda str: str.isupper(),['str'])
        self.addFunction('join',lambda str,seq: str.join(seq),['str'])
        self.addFunction('ljust',lambda str,width,fillchar=None: str.ljust(width,fillchar),['str'])
        self.addFunction('lower',lambda str: str.lower(),['str'])
        self.addFunction('lstrip',lambda str,chars: str.lstrip(chars),['str'])
        self.addFunction('partition',lambda str,sep: str.partition(sep))
        self.addFunction('replace',lambda str,old,new,count=None: str.replace(old,new,count),['str'])
        self.addFunction('rfind',lambda str,sub,start=None,end=None: str.rfind(sub,start,end),['str'])
        self.addFunction('rindex',lambda str,sub,start=None,end=None: str.rindex(sub,start,end),['str'])
        self.addFunction('rjust',lambda str,width,fillchar=None: str.rjust(width,fillchar),['str'])
        self.addFunction('rpartition',lambda str,sep: str.rpartition(sep),['str'])
        self.addFunction('rsplit',lambda str,sep,maxsplit=None: str.rsplit(sep,maxsplit),['str'])
        self.addFunction('rstrip',lambda str,chars: str.lstrip(chars),['str'])
        self.addFunction('split',lambda str,sep,maxsplit=None: str.split(sep,maxsplit),['str'])
        self.addFunction('splitlines',lambda str,keepends=None: str.splitlines(keepends),['str'])
        self.addFunction('startswith',lambda str,prefix,start=None,end=None: str.startswith(prefix,start,end),['str'])
        self.addFunction('strip',lambda str,chars: str.lstrip(chars),['str'])
        self.addFunction('swapcase',lambda str: str.swapcase(),['str'])
        self.addFunction('title',lambda str: str.title(),['str'])
        self.addFunction('translate',lambda str,table,deletechars=None: str.translate(table,deletechars),['str'])
        self.addFunction('upper',lambda str: str.upper(),['str'])
        self.addFunction('zfill',lambda str,width: str.zfill(width),['str'])   
    def initEnums(self): 
        self.addEnum('DayOfWeek',{"Monday":1,"Tuesday":2,"Wednesday":3,"Thursday":4,"Friday":5,"Saturday":6,"Sunday":0})
    def add(self,k,imp):
        self.operators[k]=imp
    def new(self,k,operands):
        try:
            return self.operators[k](operands)
        except:
            raise ExpressionError('error with operator: '+str(k))    
    def addEnum(self,key,imp:dict):
        self.enums[key] =imp 
    def isEnum(self,name):    
        names = name.split('.')
        return names[0] in self.enums.keys()
    def getEnumValue(self,name,option): 
        return self.enums[name][option]
    def getEnum(self,name): 
        return self.enums[name]
    def addFunction(self,key,imp,types=['any']):
        if key not in self.functions.keys():
            self.functions[key]= []
        self.functions[key].append({'types':types,'imp':imp})         
    def getFunction(self,key,type='any'):
        for p in self.functions[key]:
            if type in p['types']:
                return p['imp']
        return None

    def setContext(self,expression,context):
        if type(expression).__name__ ==  'Variable':
            expression.context = context
        if hasattr(expression, 'operands'):
            for p in expression.operands:
                if type(p).__name__ ==  'Variable':
                    p.context = context
                elif hasattr(p, 'operands'):
                    self.setContext(p,context)    

    def solve(self,string:str,context:dict=None):        
        expression=self.parse(string)
        return self.eval(expression,context)

    def eval(self,expression:Operand,context:dict=None):
        if context != None:
            self.setContext(expression,context)
        return expression.value   

    def parse(self,string):
        try:
            parser = Parser(self,string)
            expression= parser.parse() 
            del parser
            return expression  
        except:
            raise ExpressionError('error in expression: '+string)  

class Parser():
    def __init__(self,mgr,string):
       self.mgr = mgr 
       self.chars = self.clear(string)
       self.length=len(self.chars)
       self.index=0
       self.reAlphanumeric = re.compile('[a-zA-Z0-9_.]+$') 
       self.reInt = re.compile('[0-9]+$')
       self.reFloat = re.compile('(\d+(\.\d*)?|\.\d+)([eE]\d+)?')
  

    @staticmethod
    def clear(string):
        isString=False
        quotes=None
        result =[]
        chars = list(string)
        for p in chars:
            if isString and p == quotes: isString=False 
            elif not isString and (p == '\'' or p=='"'):
                isString=True
                quotes=p
            if p != ' ' or isString:
               result.append(p)
        return result

    def parse(self):
        operands=[]
        while not self.end:
            operand =self.getExpression(_break=';')
            if operand == None:break
            operands.append(operand)
        if len(operands)==1 :
            return operands[0]
        return Array(operands) 

    @property
    def previous(self):
        return self.chars[self.index-1] 
    @property
    def current(self):
        return self.chars[self.index]    
    @property
    def next(self):
        return self.chars[self.index+1]
    @property
    def end(self):
        return self.index >= self.length   

    def getExpression(self,a=None,op1=None,_break=''):
        expression = None
        b = None
        isbreak = False               
        while not self.end:
            if a==None and op1==None: 
                a=  self.getOperand()
                op1= self.getOperator()
                if op1==None or op1 in _break: 
                    expression = a
                    isbreak= True
                    break
            b=  self.getOperand()
            op2= self.getOperator()
            if op2 == None or op2 in _break:
                expression= self.mgr.new(op1,[a,b])
                isbreak= True
                break
            elif self.priority(op1)>=self.priority(op2):
                a=self.mgr.new(op1,[a,b])
                op1=op2
            else:
                b = self.getExpression(a=b,op1=op2,_break=_break)
                expression= self.mgr.new(op1,[a,b])
                isbreak= True
                break
        if not isbreak: expression=self.mgr.new(op1,[a,b])
        # if all the operands are constant, reduce the expression a constant 
        if expression != None and hasattr(expression, 'operands'):
            allConstants=True              
            for p in expression.operands:
                if type(p).__name__ !=  'Constant':
                    allConstants=False
                    break
            if  allConstants:
                value = expression.value
                _type = type(value).__name__
                return Constant(value,_type)
        return expression             

    def getOperand(self):        
        isNegative=False
        isNot=False
        operand=None
        char = self.current
        if char == '-':
           isNegative=True
           self.index+=1
           char = self.current
        elif char == '!':
           isNot=True
           self.index+=1
           char = self.current   

        if char.isalnum():    
            value=  self.getValue()
            if not self.end and self.current == '(':
                self.index+=1
                args=  self.getArgs(end=')')
                if '.' in value:
                    names = value.split('.')
                    key = names.pop()
                    variableName= '.'.join(names)
                    variable = Variable(variableName)
                    args.insert(0,variable)
                    operand= Function(self.mgr,key,args,True)
                else:
                    operand= Function(self.mgr,value,args)       

            elif not self.end and self.current == '[':
                self.index+=1    
                idx, i= self.getExpression(_break=']')
                operand= Variable(value)
                operand = IndexDecorator(operand,idx)                
            elif self.reInt.match(value): 
                if isNegative:
                    value = int(value)* -1
                    isNegative= False 
                else:
                    value =int(value)
                operand = Constant(value,'int')
            elif self.reFloat.match(value):
                if isNegative:
                    value = float(value)* -1
                    isNegative= False 
                else:
                    value =float(value)
                operand = Constant(value,'float')
            elif self.mgr.isEnum(value):                
                if '.' in value and self.mgr.isEnum(value):
                    names = value.split('.')
                    enumName = names[0]
                    enumOption = names[1] 
                    enumValue= self.mgr.getEnumValue(enumName,enumOption)
                    enumType = type(enumValue).__name__
                    operand = Constant(enumValue,enumType)
                else:
                    values= self.mgr.getEnum(value)
                    attributes= []
                    for name in values:
                        _value = values[name]
                        _valueType = type(_value).__name__
                        attribute = KeyValue(name,Constant(_value,_valueType))
                        attributes.append(attribute)
                    operand= Object(attributes)
            else:
                operand = Variable(value)
        elif char == '\'' or char == '"':
            self.index+=1
            result=  self.getString(char)
            operand= Constant(result,'str')
        elif char == '(':
            self.index+=1
            operand=  self.getExpression(_break=')') 
        elif char == '{':
            self.index+=1
            operand,i = self.getObject()  
        elif char == '[':
            self.index+=1
            elements=  self.getArgs(end=']')
            operand = Array(elements)

        if not self.end and  self.current=='.':
            self.index+=1
            function= self.getOperand()
            function.operands.insert(0,operand)
            function.isChild = True
            operand=function

        if isNegative:operand=NegativeDecorator(operand)
        if isNot:operand=NotDecorator(operand)
        return operand

    def priority(self,op):
        if op in ['=','+=','-=','*=','/=','%=','**=','//=','&=','|=','^=','<<=','>>='] : return 1        
        if op in ['&&','||'] : return 2
        if op in ['>','<','>=','<=','!=','==']: return 3
        if op in ['+','-'] : return 4
        if op in ['*','/'] : return 5
        if op in ['**','//'] : return 6
        return -1

    def getValue(self):
        buff=[]
        while not self.end and self.reAlphanumeric.match(self.current):
            buff.append(self.current)
            self.index+=1
        return ''.join(buff)

    def getOperator(self):
        if self.end:return None 
        op=None
        if self.index+2 < self.length:
            triple = self.current+self.next+self.chars[self.index+2]
            if triple in ['**=','//=','<<=','>>=']:op=triple
        if op == None and  self.index+1 < self.length:
            double = self.current+self.next
            if double in ['**','//','>=','<=','!=','==','+=','-=','*=','/=','%=','&&','||','|=','^=','<<','>>']  :op=double
        if op == None:op=self.current 
        self.index+=len(op)
        return op

    def getString(self,char):
        buff=[]       
        while not self.end :
            if self.current == char:
                if not((self.index+1 < self.length and self.next == char) or (self.previous == char)):
                    break 
            buff.append(self.current)
            self.index+=1
        self.index+=1    
        return ''.join(buff)

    def getArgs(self,end=')'):
        args= []
        while True:
            arg= self.getExpression(_break=','+end)
            if arg != None:args.append(arg)
            if self.previous==end: break
        return args

    def getObject(self):
        attributes= []
        while True:
            name= self.getValue()
            if self.current!=':':
                raise ExpressionError('attribute '+name+' without value')
            value= self.getExpression(_break=',}')
            attribute = KeyValue(name,value)
            attributes.append(attribute)
            if self.previous=='}': break
        
        return Object(attributes) 