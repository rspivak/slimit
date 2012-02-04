::

      _____ _      _____ __  __ _____ _______
     / ____| |    |_   _|  \/  |_   _|__   __|
    | (___ | |      | | | \  / | | |    | |
     \___ \| |      | | | |\/| | | |    | |
     ____) | |____ _| |_| |  | |_| |_   | |
    |_____/|______|_____|_|  |_|_____|  |_|


Welcome to SlimIt
==================================

`SlimIt` is a JavaScript minifier written in Python.
It compiles JavaScript into more compact code so that it downloads
and runs faster.

`SlimIt` also provides a library that includes a JavaScript parser,
lexer, pretty printer and a tree visitor.

`http://slimit.org/ <http://slimit.org/>`_

Installation
------------

::

    $ [sudo] pip install slimit

Or the bleeding edge version from the git master branch:

::

    $ [sudo] pip install git+https://github.com/rspivak/slimit.git#egg=slimit


Let's minify some code
----------------------

From the command line:

::

    $ slimit -h
    Usage: slimit [options] [input file]

    If no input file is provided STDIN is used by default.
    Minified JavaScript code is printed to STDOUT.


    Options:
      -h, --help    show this help message and exit
      -m, --mangle  mangle names

    $ cat test.js
    var a = function( obj ) {
            for ( var name in obj ) {
                    return false;
            }
            return true;
    };
    $
    $ slimit --mangle < test.js
    var a=function(a){for(var b in a)return false;return true;};

Or using library API:

>>> from slimit import minify
>>> text = """
... var a = function( obj ) {
...         for ( var name in obj ) {
...                 return false;
...         }
...         return true;
... };
... """
>>> print minify(text, mangle=True)
var a=function(a){for(var b in a)return false;return true;};


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

Writing custom node visitor
---------------------------

>>> from slimit.parser import Parser
>>> from slimit.visitors.nodevisitor import ASTVisitor
>>>
>>> text = """
... var x = {
...     "key1": "value1",
...     "key2": "value2"
... };
... """
>>>
>>> class MyVisitor(ASTVisitor):
...     def visit_Object(self, node):
...         """Visit object literal."""
...         for prop in node:
...             left, right = prop.left, prop.right
...             print 'Property key=%s, value=%s' % (left.value, right.value)
...             # visit all children in turn
...             self.visit(prop)
...
>>>
>>> parser = Parser()
>>> tree = parser.parse(text)
>>> visitor = MyVisitor()
>>> visitor.visit(tree)
Property key="key1", value="value1"
Property key="key2", value="value2"

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

Benchmarks
----------

**SAM** - JQuery size after minification in bytes (the smaller number the better)

+-------------------------------+------------+------------+------------+
| Original jQuery 1.6.1 (bytes) | SlimIt SAM | rJSmin SAM | jsmin SAM  |
+===============================+============+============+============+
| 234,995                       | 94,290     | 134,215    | 134,819    |
+-------------------------------+------------+------------+------------+

Roadmap
-------
- when doing name mangling handle cases with 'eval' and 'with'
- foo["bar"] ==> foo.bar
- consecutive declarations: var a = 10; var b = 20; ==> var a=10,b=20;
- reduce simple constant expressions if the result takes less space:
  1 +2 * 3 ==> 7
- IF statement optimizations

  1. if (foo) bar(); else baz(); ==> foo?bar():baz();
  2. if (!foo) bar(); else baz(); ==> foo?baz():bar();
  3. if (foo) bar(); ==> foo&&bar();
  4. if (!foo) bar(); ==> foo||bar();
  5. if (foo) return bar(); else return baz(); ==> return foo?bar():baz();
  6. if (foo) return bar(); else something(); ==> {if(foo)return bar();something()}

- remove unreachable code that follows a return, throw, break or
  continue statement, except function/variable declarations
- parsing speed improvements

Acknowledgments
---------------
- The lexer and parser are built with `PLY <http://www.dabeaz.com/ply/>`_
- Several test cases and regexes from `jslex <https://bitbucket.org/ned/jslex>`_
- Some visitor ideas - `pycparser <http://code.google.com/p/pycparser/>`_
- Many grammar rules are taken from `rkelly <https://github.com/tenderlove/rkelly>`_
- Name mangling and different optimization ideas - `UglifyJS <https://github.com/mishoo/UglifyJS>`_
- ASI implementation was inspired by `pyjsparser <http://bitbucket.org/mvantellingen/pyjsparser>`_

License
-------
The MIT License (MIT)