


# Objetivo:

## Expressions
Plantear expressiones que cumpla con las siguientes caracteristicas
- Identificar variables sin la necesidad de usar un caracter especial, ejemplo $ o {}
- JSON

## Parser
Plantear un parser de expressiones que cumpla con las siguientes caracteristicas
- No depender de un parseador de sintaxis, ejemplo GoldParser
- Poder resolver precedencia de operadores sin la necesidad de usar parentesis, ejemplo: 2+3*4
- Identificar JSON

Aclaraciones:
 - El que se pase el argumenton index en los metodos es por que se priorizo tener metodos independientes de una variable a nivel clase.


type        |pattern
------------|-------------
number      |##.##
variable    |xxx  xxx.xxx
string      |'xxx' "xxx" 'x"x"x' "x'x'x" 'x''x''x' "x""x""x"
function    |xxx() xxx.xxx()
object      | {} {x:'xxx',x:##.##,x:xxx}     

# TODO:
## pendings 
- variables
- resolver precedencia de operadores (exp: * sobre +)
- uso de parentecis
- deteccion de funcionnes
- arrays
- dictionaries
- asignaciones de variables
- separacion por ;
- metodos reduce para resolver previamente las operaciones entre constantes y dejar un solo operando constante

## solved

# References
- [operants](https://www.w3schools.com/python/python_operators.asp)
- [unit test](https://docs.python.org/3/library/unittest.html)
- [example](https://stackoverflow.com/questions/13055884/parsing-math-expression-in-python-and-solving-to-find-an-answer)