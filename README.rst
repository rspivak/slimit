Welcome to SlimIt
==================================

`SlimIt` is a JavaScript minifier written in Python.
It compiles JavaScript into more compact code so that it downloads
and runs faster.

At version `0.1` it provides only a JavaScript lexer.

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
