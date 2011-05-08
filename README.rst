Welcome to SlimIt
==================================

`SlimIt` is a JavaScript minifier written in Python.
It compiles JavaScript into more compact code so that it downloads
and runs faster.

At version `0.2` it provides a library that includes a JavaScript
parser, lexer, pretty printer and a tree visitor.

Iterate over, modify a JavaScript AST and pretty print it
---------------------------------------------------------

>>> from slimit.parser import Parser
>>> from slimit.visitors import nodevisitor
>>> from slimit import ast
>>>
>>> parser = Parser()
>>> tree = parser.parse('for(var i=0; i<10; i++) {var x=5+i;}')
>>> for node in nodevisitor.visit(tree):
...     if isinstance(node, ast.Identifier) and node.value == 'i':
...         node.value = 'hello'
...
>>> print tree.to_ecma() # print awesome javascript :)
for (var hello = 0; hello < 10; hello++) {
  var x = 5 + hello;
}
>>>

`N.B.` First time you invoke ``parse`` method it will generate the
``lextab.py`` and ``yacctab.py`` LALR tables in current directory and
you may see some warnings - that's OK. Previously generated tables
are cached and reused if possible. For more details visit `PLY's
official site <http://www.dabeaz.com/ply/ply.html>`_.


Using lexer in your project
---------------------------

>>> from slimit.lexer import Lexer
>>> lexer = Lexer()
>>> lexer.input('a = 1;')
>>> for token in lexer:
...     print token
...
LexToken(ID,'a',1,0)
LexToken(EQ,'=',1,2)
LexToken(NUMBER,'1',1,4)
LexToken(SEMI,';',1,5)

You can get one token at a time using ``token`` method:

>>> lexer.input('a = 1;')
>>> while True:
...     token = lexer.token()
...     if not token:
...         break
...     print token
...
LexToken(ID,'a',1,0)
LexToken(EQ,'=',1,2)
LexToken(NUMBER,'1',1,4)
LexToken(SEMI,';',1,5)

`LexToken` instance has different attributes:

>>> lexer.input('a = 1;')
>>> token = lexer.token()
>>> token.type, token.value, token.lineno, token.lexpos
('ID', 'a', 1, 0)

Installation
------------

Using ``pip``::

    $ sudo pip install slimit

Using ``easy_install``::

    $ sudo easy_install slimit
