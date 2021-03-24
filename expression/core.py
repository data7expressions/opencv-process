import re
# from typing import ChainMap

class ExpressionError(Exception):
    pass

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
class Variable(Operand):
    def __init__(self,name ):
      self._name  = name
      self._names = name.split()
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
        for n in self._names:
            _value=_value[n]
        _value=value       

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
        if self.isChild:
            parent = self._operands.pop(0)
            value = parent.value
            _type = type(value).__name__
            function=self.mgr.getFunction(_type+'_'+self.name)            
            for p in self._operands:args.append(p.value)
            args.insert(0,value)            
        else:
            function=self.mgr.getFunction(self.name)
            for p in self._operands:args.append(p.value)    

        return function(*args)

# class FunctionDecorator(Operator):
#     def __init__(self,operand:Operand,func:Function ):
#         super(FunctionDecorator,self).__init__([operand,func])

#     @property    
#     def value(self):
#         value = self._operands[0].value
#         self._operands[1].type = type(value).__name__

#         self._operands[1].operands.insert(0,self._operands[0])
#         return self._operands[1].value
       

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

class ExpManager():
    def __init__(self):
       self.operators={} 
       self.functions={}
       self.reInt = re.compile('[0-9]+$')
       self.reFloat = re.compile('(\d+(\.\d*)?|\.\d+)([eE]\d+)?')
       self.arithmeticOperators = ['+','-','*','/','%','**','//']
       self.comparisonOperators = ['>','<','>=','<=','!=','==']

    def add(self,k,imp):
        self.operators[k]=imp
      
    def __new(self,k,operands):
        return self.operators[k](operands)

    def addFunction(self,key,imp):
        self.functions[key]=imp 

    def getFunction(self,key):
        return self.functions[key]
  
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
        if context != None:
            self.setContext(expression,context)
        return expression.value

    def parse(self,string):
        chars = list(string)
        length=len(chars)
        operand,i= self.__getExpression(chars,0,length)
        return operand

    def __getExpression(self,chars,i,length,a=None,op1=None,_break=''):              
        while i < length:
            if a==None and op1==None: 
                a,i= self.__getOperand(chars,i,length)
                op1,i=self.__getOperator(chars,i,length)
                if op1==None or op1 in _break: return a,i

            b,i= self.__getOperand(chars,i,length)
            op2,i=self.__getOperator(chars,i,length)

            if op2 == None or op2 in _break:
                return self.__new(op1,[a,b]),i
            elif self.__priority(op1)>=self.__priority(op2):
                a=self.__new(op1,[a,b])
                op1=op2
            else:
                b,i = self.__getExpression(chars,i,length,a=b,op1=op2,_break=_break)
                return self.__new(op1,[a,b]),i

        return self.__new(op1,[a,b]),i         

    def __getOperand(self,chars,i,length):        
        isNegative=False
        isNot=False
        operand=None
        char = chars[i]
        if char == '-':
           isNegative=True
           i=i+1
           char = chars[i]
        elif char == '!':
           isNot=True
           i=i+1
           char = chars[i]   

        if char.isalnum():    
            value,i= self.__getValue(chars,i,length)
            if i<length and chars[i] == '(':
                args,i= self.__getArgs(chars,i+1,length)
                if '.' in value:
                    names = value.split()
                    key = names.pop()
                    variable = Variable(names)
                    args.insert(0,variable)
                    Function(self,key,args,True)
                else:
                    key=value
                operand= Function(self,key,args)       

            elif i<length and chars[i] == '[':    
                idx, i= self.__getExpression(chars,i+1,length,_break=']')
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
                operand = Constant(value,'decimal')
            else:
                operand = Variable(value)
        elif char == '\'' or char == '"':
            result,i= self.__getString(chars,i+1,length,char)
            operand= Constant(result,'string')
        elif char == '(':
            operand,i= self.__getExpression(chars,i+1,length,_break=')') 
        elif char == '{':
            operand,i = self.__getObject(chars,i+1,length)  


        if i<length and  chars[i]=='.':
            function,i=self.__getOperand(chars,i+1,length)
            function.operands.insert(0,operand)
            function.isChild = True
            operand=function

        if isNegative:operand=NegativeDecorator(operand)
        if isNot:operand=NotDecorator(operand)
        return operand,i

    def __priority(self,op):
        if op in ['='] : return 1
        if op in self.comparisonOperators : return 2
        if op in ['+','-'] : return 3
        if op in ['*','/'] : return 4
        if op in ['**','//'] : return 5
        return -1

    def __getValue(self,chars,i,length):
        buff=[]
        while i < length and chars[i].isalnum():
            buff.append(chars[i])
            i+=1
        return ''.join(buff),i

    def __getOperator(self,chars,i,length):
        if i == length:
            return None , i
        if chars[i] in self.arithmeticOperators:
            if chars[i]+chars[i+1] in self.arithmeticOperators:
                return chars[i]+chars[i+1], i+2
        elif chars[i] in self.comparisonOperators or chars[i] in ['=','!']:
            if chars[i]+chars[i+1] in self.comparisonOperators:
                return chars[i]+chars[i+1], i+2
        return chars[i],i+1

    def __getString(self,chars,i,length,char):
        buff=[]       
        while i < length :
            if chars[i] == char:
               if not((i+1 < length and chars[i+1] == char) or (chars[i-1] == char)):
                  break 
            buff.append(chars[i])
            i+=1
        return ''.join(buff),i+1

    def __getArgs(self,chars,i,length):
        args= []
        while True:
            arg,i=self.__getExpression(chars,i,length,_break=',)')
            if arg != None:args.append(arg)
            if chars[i-1]==')': break
        return args, i

    def __getObject(self,chars,i,length):
        pass 

def addElements():

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

    #exp.add('Constant',Constant)
    #exp.add('variable',Variable)
    exp.add('function',Function)

    exp.add('+',Addition)
    exp.add('-',Subtraction)
    exp.add('*',Multiplication)
    exp.add('/',Division)
    exp.add('**',Exponentiation)
    exp.add('//',FloorDivision)
    exp.add('%',Mod)

    exp.add('==',Equal)
    exp.add('!=',NotEqual)
    exp.add('>',GreaterThan)
    exp.add('<',LessThan)
    exp.add('>=',GreaterThanOrEqual)
    exp.add('<=',LessThanOrEqual)

    exp.add('&&',And)
    exp.add('||',Or)
    exp.add('!',Not)

    exp.add('&',BitAnd)
    exp.add('|',BitOr)
    exp.add('^!',BitXor)
    exp.add('~',BitNot)
    exp.add('<<',LeftShift)
    exp.add('>>',RightShift)


    exp.addFunction('nvl',lambda a,b: a if a!=None else b )


    exp.addFunction('str_capitalize',lambda str: str.capitalize())
    exp.addFunction('str_count',lambda str,sub,start=None,end=None: str.count(sub,start,end))
    exp.addFunction('str_decode',lambda str,encoding: str.decode(encoding))
    exp.addFunction('str_encode',lambda str,encoding: str.encode(encoding))
    exp.addFunction('str_endswith',lambda str,suffix,start=None,end=None: str.endswith(suffix,start,end))
    exp.addFunction('str_find',lambda str,sub,start=None,end=None: str.find(sub,start,end))
    exp.addFunction('str_index',lambda str,sub,start=None,end=None: str.index(sub,start,end))
    exp.addFunction('str_isalnum',lambda str: str.isalnum())
    exp.addFunction('str_isalpha',lambda str: str.isalpha())
    exp.addFunction('str_isdigit',lambda str: str.isdigit())
    exp.addFunction('str_islower',lambda str: str.islower())
    exp.addFunction('str_isspace',lambda str: str.isspace())
    exp.addFunction('str_istitle',lambda str: str.istitle())
    exp.addFunction('str_isupper',lambda str: str.isupper())
    exp.addFunction('str_join',lambda str,seq: str.join(seq))
    exp.addFunction('str_ljust',lambda str,width,fillchar=None: str.ljust(width,fillchar))
    exp.addFunction('str_lower',lambda str: str.lower())
    exp.addFunction('str_lstrip',lambda str,chars: str.lstrip(chars))
    exp.addFunction('str_partition',lambda str,sep: str.partition(sep))
    exp.addFunction('str_replace',lambda str,old,new,count=None: str.replace(old,new,count))
    exp.addFunction('str_rfind',lambda str,sub,start=None,end=None: str.rfind(sub,start,end))
    exp.addFunction('str_rindex',lambda str,sub,start=None,end=None: str.rindex(sub,start,end))
    exp.addFunction('str_rjust',lambda str,width,fillchar=None: str.rjust(width,fillchar))
    exp.addFunction('str_rpartition',lambda str,sep: str.rpartition(sep))
    exp.addFunction('str_rsplit',lambda str,sep,maxsplit=None: str.rsplit(sep,maxsplit))
    exp.addFunction('str_rstrip',lambda str,chars: str.lstrip(chars))
    exp.addFunction('str_split',lambda str,sep,maxsplit=None: str.split(sep,maxsplit))
    exp.addFunction('str_splitlines',lambda str,keepends=None: str.splitlines(keepends))
    exp.addFunction('str_startswith',lambda str,prefix,start=None,end=None: str.startswith(prefix,start,end))
    exp.addFunction('str_strip',lambda str,chars: str.lstrip(chars))
    exp.addFunction('str_swapcase',lambda str: str.swapcase())
    exp.addFunction('str_title',lambda str: str.title())
    exp.addFunction('str_translate',lambda str,table,deletechars=None: str.translate(table,deletechars))
    exp.addFunction('str_upper',lambda str: str.upper())
    exp.addFunction('str_zfill',lambda str,width: str.zfill(width))





    
    







exp = ExpManager()
addElements()

result=exp.solve('a.count("a")',{"a":"aaa"})
# result=exp.solve('a.count()',{"a":[1,2,3]})
print(result)
# print (1+(2**3)*4) 
# print ((2**3)) 




