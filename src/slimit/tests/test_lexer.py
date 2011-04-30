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

import unittest
import difflib
import pprint

from slimit.lexer import Lexer


# The structure and some test cases are taken
# from https://bitbucket.org/ned/jslex
class LexerTestCase(unittest.TestCase):

    def _get_lexer(self):
        lexer = Lexer()
        lexer.build()
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

    TEST_CASES = [
        # Identifiers
        ('i my_variable_name c17 _dummy $str $ _ CamelCase',
         ['ID i', 'ID my_variable_name', 'ID c17',
          'ID _dummy', 'ID $str', 'ID $', 'ID _', 'ID CamelCase']
         ),
        (ur'\u03c0 \u03c0_tail var\ua67c',
         [ur'ID \u03c0', ur'ID \u03c0_tail', ur'ID var\ua67c']),

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
        (('== != === !== < > <= >= || && ++ -- << >> '
          '>>> += -= *= /= <<= >>= >>>= &= %= ^= |='),
         ['EQEQ ==', 'NE !=', 'STREQ ===', 'STRNEQ !==', 'LT <', 'GT >',
          'LE <=', 'GE >=', 'OR ||', 'AND &&', 'PLUSPLUS ++', 'MINUSMINUS --',
          'LSHIFT <<', 'RSHIFT >>', 'URSHIFT >>>', 'PLUSEQUAL +=',
          'MINUSEQUAL -=', 'MULTEQUAL *=', 'DIVEQUAL /=', 'LSHIFTEQUAL <<=',
          'RSHIFTEQUAL >>=', 'URSHIFTEQUAL >>>=', 'ANDEQUAL &=', 'MODEQUAL %=',
          'XOREQUAL ^=', 'OREQUAL |=',
          ]
         ),

        # Punctuator literals
        # ('& * ...', ['& &', '* *', ...])
        (' '.join(literal for literal in Lexer.literals),
         ['%s %s' % (literal, literal) for literal in Lexer.literals]
         ),

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

