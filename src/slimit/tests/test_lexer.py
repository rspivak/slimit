###############################################################################
# encoding: utf-8
#
# Copyright (c) 2011 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import doctest
import unittest
import difflib
import pprint

from slimit.lexer import Lexer


# The structure and some test cases are taken
# from https://bitbucket.org/ned/jslex
class LexerTestCase(unittest.TestCase):

    def _get_lexer(self):
        lexer = Lexer()
        return lexer

    def assertListEqual(self, first, second):
        """Assert that two lists are equal.

        Prints differences on error.
        This method is similar to that of Python 2.7 'assertListEqual'
        """
        if first != second:
            message = '\n'.join(
                difflib.ndiff(pprint.pformat(first).splitlines(),
                              pprint.pformat(second).splitlines())
                )
            self.fail('Lists differ:\n' + message)

    def test_illegal_unicode_char_in_identifier(self):
        lexer = self._get_lexer()
        lexer.input(u'\u0036_tail')
        token = lexer.token()
        # \u0036_tail is the same as 6_tail and that's not a correct ID
        # Check that the token is NUMBER and not an ID
        self.assertEqual(token.type, 'NUMBER')
        self.assertEqual(token.value, '6')

    TEST_CASES = [
        # Identifiers
        ('i my_variable_name c17 _dummy $str $ _ CamelCase class2type',
         ['ID i', 'ID my_variable_name', 'ID c17', 'ID _dummy',
          'ID $str', 'ID $', 'ID _', 'ID CamelCase', 'ID class2type']
         ),
        (ur'\u03c0 \u03c0_tail var\ua67c',
         [ur'ID \u03c0', ur'ID \u03c0_tail', ur'ID var\ua67c']),
        # https://github.com/rspivak/slimit/issues/2
        ('nullify truelie falsepositive',
         ['ID nullify', 'ID truelie', 'ID falsepositive']),

        # Keywords
        # ('break case ...', ['BREAK break', 'CASE case', ...])
        (' '.join(kw.lower() for kw in Lexer.keywords),
         ['%s %s' % (kw, kw.lower()) for kw in Lexer.keywords]
         ),
        ('break Break BREAK', ['BREAK break', 'ID Break', 'ID BREAK']),

        # Literals
        ('null true false Null True False',
         ['NULL null', 'TRUE true', 'FALSE false',
          'ID Null', 'ID True', 'ID False']
         ),

        # Punctuators
        ('a /= b', ['ID a', 'DIVEQUAL /=', 'ID b']),
        (('= == != === !== < > <= >= || && ++ -- << >> '
          '>>> += -= *= <<= >>= >>>= &= %= ^= |='),
         ['EQ =', 'EQEQ ==', 'NE !=', 'STREQ ===', 'STRNEQ !==', 'LT <',
          'GT >', 'LE <=', 'GE >=', 'OR ||', 'AND &&', 'PLUSPLUS ++',
          'MINUSMINUS --', 'LSHIFT <<', 'RSHIFT >>', 'URSHIFT >>>',
          'PLUSEQUAL +=', 'MINUSEQUAL -=', 'MULTEQUAL *=', 'LSHIFTEQUAL <<=',
          'RSHIFTEQUAL >>=', 'URSHIFTEQUAL >>>=', 'ANDEQUAL &=', 'MODEQUAL %=',
          'XOREQUAL ^=', 'OREQUAL |=',
          ]
         ),
        ('. , ; : + - * % & | ^ ~ ? ! ( ) { } [ ]',
         ['PERIOD .', 'COMMA ,', 'SEMI ;', 'COLON :', 'PLUS +', 'MINUS -',
          'MULT *', 'MOD %', 'BAND &', 'BOR |', 'BXOR ^', 'BNOT ~',
          'CONDOP ?', 'NOT !', 'LPAREN (', 'RPAREN )', 'LBRACE {', 'RBRACE }',
          'LBRACKET [', 'RBRACKET ]']
         ),
        ('a / b', ['ID a', 'DIV /', 'ID b']),

        # Numbers
        (('3 3.3 0 0. 0.0 0.001 010 3.e2 3.e-2 3.e+2 3E2 3E+2 3E-2 '
          '0.5e2 0.5e+2 0.5e-2 33 128.15 0x001 0X12ABCDEF 0xabcdef'),
         ['NUMBER 3', 'NUMBER 3.3', 'NUMBER 0', 'NUMBER 0.', 'NUMBER 0.0',
          'NUMBER 0.001', 'NUMBER 010', 'NUMBER 3.e2', 'NUMBER 3.e-2',
          'NUMBER 3.e+2', 'NUMBER 3E2', 'NUMBER 3E+2', 'NUMBER 3E-2',
          'NUMBER 0.5e2', 'NUMBER 0.5e+2', 'NUMBER 0.5e-2', 'NUMBER 33',
          'NUMBER 128.15', 'NUMBER 0x001', 'NUMBER 0X12ABCDEF',
          'NUMBER 0xabcdef']
         ),

        # Strings
        (""" '"' """, ["""STRING '"'"""]),
        (r'''"foo" 'foo' "x\";" 'x\';' "foo\tbar"''',
         ['STRING "foo"', """STRING 'foo'""", r'STRING "x\";"',
          r"STRING 'x\';'", r'STRING "foo\tbar"']
         ),
        (r"""'\x55' "\x12ABCDEF" '!@#$%^&*()_+{}[]\";?'""",
         [r"STRING '\x55'", r'STRING "\x12ABCDEF"',
          r"STRING '!@#$%^&*()_+{}[]\";?'"]
         ),
        (r"""'\u0001' "\uFCEF" 'a\\\b\n'""",
         [r"STRING '\u0001'", r'STRING "\uFCEF"', r"STRING 'a\\\b\n'"]
         ),
        (ur'"тест строки\""', [ur'STRING "тест строки\""']),
        # Bug - https://github.com/rspivak/slimit/issues/5
        (r"var tagRegExp = new RegExp('<(\/*)(FooBar)', 'gi');",
         ['VAR var', 'ID tagRegExp', 'EQ =',
          'NEW new', 'ID RegExp', 'LPAREN (',
          r"STRING '<(\/*)(FooBar)'", 'COMMA ,', "STRING 'gi'",
          'RPAREN )', 'SEMI ;']
        ),
        # same as above but inside double quotes
        (r'"<(\/*)(FooBar)"', [r'STRING "<(\/*)(FooBar)"']),


        # # Comments
        # ("""
        # //comment
        # a = 5;
        # """, ['LINE_COMMENT //comment', 'ID a', 'EQ =', 'NUMBER 5', 'SEMI ;']
        #  ),
        # ('a//comment', ['ID a', 'LINE_COMMENT //comment']),
        # ('/***/b/=3//line',
        #  ['BLOCK_COMMENT /***/', 'ID b', 'DIVEQUAL /=',
        #   'NUMBER 3', 'LINE_COMMENT //line']
        #  ),
        # ('/*\n * Copyright LGPL 2011 \n*/\na = 1;',
        #  ['BLOCK_COMMENT /*\n * Copyright LGPL 2011 \n*/',
        #   'ID a', 'EQ =', 'NUMBER 1', 'SEMI ;']
        #  ),

        # regex
        (r'a=/a*/,1', ['ID a', 'EQ =', 'REGEX /a*/', 'COMMA ,', 'NUMBER 1']),
        (r'a=/a*[^/]+/,1',
         ['ID a', 'EQ =', 'REGEX /a*[^/]+/', 'COMMA ,', 'NUMBER 1']
         ),
        (r'a=/a*\[^/,1',
         ['ID a', 'EQ =', r'REGEX /a*\[^/', 'COMMA ,', 'NUMBER 1']
         ),
        (r'a=/\//,1', ['ID a', 'EQ =', r'REGEX /\//', 'COMMA ,', 'NUMBER 1']),
        # not a regex, just a division
        # https://github.com/rspivak/slimit/issues/6
        (r'x = this / y;',
         ['ID x', 'EQ =', 'THIS this', r'DIV /', r'ID y', r'SEMI ;']),

        # next two are from
        # http://www.mozilla.org/js/language/js20-2002-04/rationale/syntax.html#regular-expressions
        ("""for (var x = a in foo && "</x>" || mot ? z:/x:3;x<5;y</g/i) {xyz(x++);}""",
         ["FOR for", "LPAREN (", "VAR var", "ID x", "EQ =", "ID a", "IN in",
          "ID foo", "AND &&", 'STRING "</x>"', "OR ||", "ID mot", "CONDOP ?",
          "ID z", "COLON :", "REGEX /x:3;x<5;y</g", "DIV /", "ID i", "RPAREN )",
          "LBRACE {",  "ID xyz", "LPAREN (", "ID x", "PLUSPLUS ++", "RPAREN )",
          "SEMI ;", "RBRACE }"]
         ),

        ("""for (var x = a in foo && "</x>" || mot ? z/x:3;x<5;y</g/i) {xyz(x++);}""",
         ["FOR for", "LPAREN (", "VAR var", "ID x", "EQ =", "ID a", "IN in",
          "ID foo", "AND &&", 'STRING "</x>"', "OR ||", "ID mot", "CONDOP ?",
          "ID z", "DIV /", "ID x", "COLON :", "NUMBER 3", "SEMI ;", "ID x",
          "LT <", "NUMBER 5", "SEMI ;", "ID y", "LT <", "REGEX /g/i",
          "RPAREN )", "LBRACE {", "ID xyz", "LPAREN (", "ID x", "PLUSPLUS ++",
          "RPAREN )", "SEMI ;", "RBRACE }"]
         ),

        # Various "illegal" regexes that are valid according to the std.
        (r"""/????/, /++++/, /[----]/ """,
         ['REGEX /????/', 'COMMA ,',
          'REGEX /++++/', 'COMMA ,', 'REGEX /[----]/']
         ),

        # Stress cases from http://stackoverflow.com/questions/5533925/what-javascript-constructs-does-jslex-incorrectly-lex/5573409#5573409
        (r"""/\[/""", [r"""REGEX /\[/"""]),
        (r"""/[i]/""", [r"""REGEX /[i]/"""]),
        (r"""/[\]]/""", [r"""REGEX /[\]]/"""]),
        (r"""/a[\]]/""", [r"""REGEX /a[\]]/"""]),
        (r"""/a[\]]b/""", [r"""REGEX /a[\]]b/"""]),
        (r"""/[\]/]/gi""", [r"""REGEX /[\]/]/gi"""]),
        (r"""/\[[^\]]+\]/gi""", [r"""REGEX /\[[^\]]+\]/gi"""]),
        ("""
            rexl.re = {
            NAME: /^(?!\d)(?:\w)+|^"(?:[^"]|"")+"/,
            UNQUOTED_LITERAL: /^@(?:(?!\d)(?:\w|\:)+|^"(?:[^"]|"")+")\[[^\]]+\]/,
            QUOTED_LITERAL: /^'(?:[^']|'')*'/,
            NUMERIC_LITERAL: /^[0-9]+(?:\.[0-9]*(?:[eE][-+][0-9]+)?)?/,
            SYMBOL: /^(?:==|=|<>|<=|<|>=|>|!~~|!~|~~|~|!==|!=|!~=|!~|!|&|\||\.|\:|,|\(|\)|\[|\]|\{|\}|\?|\:|;|@|\^|\/\+|\/|\*|\+|-)/
            };
            """,
         ["ID rexl", "PERIOD .", "ID re", "EQ =", "LBRACE {",
          "ID NAME", "COLON :",
          r"""REGEX /^(?!\d)(?:\w)+|^"(?:[^"]|"")+"/""", "COMMA ,",
          "ID UNQUOTED_LITERAL", "COLON :",
          r"""REGEX /^@(?:(?!\d)(?:\w|\:)+|^"(?:[^"]|"")+")\[[^\]]+\]/""",
          "COMMA ,", "ID QUOTED_LITERAL", "COLON :",
          r"""REGEX /^'(?:[^']|'')*'/""", "COMMA ,", "ID NUMERIC_LITERAL",
          "COLON :",
          r"""REGEX /^[0-9]+(?:\.[0-9]*(?:[eE][-+][0-9]+)?)?/""", "COMMA ,",
          "ID SYMBOL", "COLON :",
          r"""REGEX /^(?:==|=|<>|<=|<|>=|>|!~~|!~|~~|~|!==|!=|!~=|!~|!|&|\||\.|\:|,|\(|\)|\[|\]|\{|\}|\?|\:|;|@|\^|\/\+|\/|\*|\+|-)/""",
         "RBRACE }", "SEMI ;"]
          ),
        ("""
            rexl.re = {
            NAME: /^(?!\d)(?:\w)+|^"(?:[^"]|"")+"/,
            UNQUOTED_LITERAL: /^@(?:(?!\d)(?:\w|\:)+|^"(?:[^"]|"")+")\[[^\]]+\]/,
            QUOTED_LITERAL: /^'(?:[^']|'')*'/,
            NUMERIC_LITERAL: /^[0-9]+(?:\.[0-9]*(?:[eE][-+][0-9]+)?)?/,
            SYMBOL: /^(?:==|=|<>|<=|<|>=|>|!~~|!~|~~|~|!==|!=|!~=|!~|!|&|\||\.|\:|,|\(|\)|\[|\]|\{|\}|\?|\:|;|@|\^|\/\+|\/|\*|\+|-)/
            };
            str = '"';
        """,
        ["ID rexl", "PERIOD .", "ID re", "EQ =", "LBRACE {",
         "ID NAME", "COLON :", r"""REGEX /^(?!\d)(?:\w)+|^"(?:[^"]|"")+"/""",
         "COMMA ,", "ID UNQUOTED_LITERAL", "COLON :",
         r"""REGEX /^@(?:(?!\d)(?:\w|\:)+|^"(?:[^"]|"")+")\[[^\]]+\]/""",
         "COMMA ,", "ID QUOTED_LITERAL", "COLON :",
         r"""REGEX /^'(?:[^']|'')*'/""", "COMMA ,",
         "ID NUMERIC_LITERAL", "COLON :",
         r"""REGEX /^[0-9]+(?:\.[0-9]*(?:[eE][-+][0-9]+)?)?/""", "COMMA ,",
         "ID SYMBOL", "COLON :",
         r"""REGEX /^(?:==|=|<>|<=|<|>=|>|!~~|!~|~~|~|!==|!=|!~=|!~|!|&|\||\.|\:|,|\(|\)|\[|\]|\{|\}|\?|\:|;|@|\^|\/\+|\/|\*|\+|-)/""",
         "RBRACE }", "SEMI ;",
         "ID str", "EQ =", """STRING '"'""", "SEMI ;",
         ]),
        (r""" this._js = "e.str(\"" + this.value.replace(/\\/g, "\\\\").replace(/"/g, "\\\"") + "\")"; """,
         ["THIS this", "PERIOD .", "ID _js", "EQ =",
          r'''STRING "e.str(\""''', "PLUS +", "THIS this", "PERIOD .",
          "ID value", "PERIOD .", "ID replace", "LPAREN (", r"REGEX /\\/g",
          "COMMA ,", r'STRING "\\\\"', "RPAREN )", "PERIOD .", "ID replace",
          "LPAREN (", r'REGEX /"/g', "COMMA ,", r'STRING "\\\""', "RPAREN )",
          "PLUS +", r'STRING "\")"', "SEMI ;"]),
        ]


def make_test_function(input, expected):

    def test_func(self):
        lexer = self._get_lexer()
        lexer.input(input)
        result = ['%s %s' % (token.type, token.value) for token in lexer]
        self.assertListEqual(result, expected)

    return test_func

for index, (input, expected) in enumerate(LexerTestCase.TEST_CASES):
    func = make_test_function(input, expected)
    setattr(LexerTestCase, 'test_case_%d' % index, func)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(LexerTestCase),
        doctest.DocFileSuite(
            '../lexer.py',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
            ),
        ))
