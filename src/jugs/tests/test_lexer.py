###############################################################################
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

from jugs.lexer import Lexer


class LexerTestCase(unittest.TestCase):

    def _get_lexer(self):
        lexer = Lexer()
        lexer.build()
        return lexer

    def _get_token(self, text):
        lexer = Lexer()
        lexer.build()
        lexer.input(text)
        token = lexer.token()
        return token

    def test_identifier(self):
        lexer = self._get_lexer()
        lexer.input('foo')
        token = lexer.token()
        self.assertEquals(token.type, 'ID')

    def test_keywords(self):
        lexer = self._get_lexer()
        for keyword in Lexer.keywords:
            lexer.input(keyword)
            token = lexer.token()
            self.assertEquals(token.type, 'ID')

    def test_literal_null(self):
        lexer = self._get_lexer()
        lexer.input('null')
        token = lexer.token()
        self.assertEquals(token.type, 'NULL')

    def test_literal_true(self):
        lexer = self._get_lexer()
        lexer.input('true')
        token = lexer.token()
        self.assertEquals(token.type, 'TRUE')

    def test_literal_false(self):
        lexer = self._get_lexer()
        lexer.input('false')
        token = lexer.token()
        self.assertEquals(token.type, 'FALSE')

    def test_punctuator_eqeq(self):
        token = self._get_token('==')
        self.assertEquals(token.type, 'EQEQ')

    def test_punctuator_ne(self):
        token = self._get_token('!=')
        self.assertEquals(token.type, 'NE')

    def test_punctuator_streq(self):
        token = self._get_token('===')
        self.assertEquals(token.type, 'STREQ')

    def test_punctuator_strneq(self):
        token = self._get_token('!==')
        self.assertEquals(token.type, 'STRNEQ')

    def test_punctuator_lt(self):
        token = self._get_token('<')
        self.assertEquals(token.type, 'LT')

    def test_punctuator_gt(self):
        token = self._get_token('>')
        self.assertEquals(token.type, 'GT')

    def test_punctuator_or(self):
        token = self._get_token('||')
        self.assertEquals(token.type, 'OR')

    def test_punctuator_and(self):
        token = self._get_token('&&')
        self.assertEquals(token.type, 'AND')

    def test_punctuator_plusplus(self):
        token = self._get_token('++')
        self.assertEquals(token.type, 'PLUSPLUS')

    def test_punctuator_minusminus(self):
        token = self._get_token('--')
        self.assertEquals(token.type, 'MINUSMINUS')

    def test_punctuator_lshift(self):
        token = self._get_token('<<')
        self.assertEquals(token.type, 'LSHIFT')

    def test_punctuator_rshift(self):
        token = self._get_token('>>')
        self.assertEquals(token.type, 'RSHIFT')

    def test_punctuator_urshift(self):
        token = self._get_token('>>>')
        self.assertEquals(token.type, 'URSHIFT')

    def test_punctuator_plusequal(self):
        token = self._get_token('+=')
        self.assertEquals(token.type, 'PLUSEQUAL')

    def test_punctuator_minusequal(self):
        token = self._get_token('-=')
        self.assertEquals(token.type, 'MINUSEQUAL')

    def test_punctuator_multequal(self):
        token = self._get_token('*=')
        self.assertEquals(token.type, 'MULTEQUAL')

    def test_punctuator_divequal(self):
        token = self._get_token('/=')
        self.assertEquals(token.type, 'DIVEQUAL')

    def test_punctuator_lshiftequal(self):
        token = self._get_token('<<=')
        self.assertEquals(token.type, 'LSHIFTEQUAL')

    def test_punctuator_rshiftequal(self):
        token = self._get_token('>>=')
        self.assertEquals(token.type, 'RSHIFTEQUAL')

    def test_punctuator_urshiftequal(self):
        token = self._get_token('>>>=')
        self.assertEquals(token.type, 'URSHIFTEQUAL')

    def test_punctuator_andequal(self):
        token = self._get_token('&=')
        self.assertEquals(token.type, 'ANDEQUAL')

    def test_punctuator_modequal(self):
        token = self._get_token('%=')
        self.assertEquals(token.type, 'MODEQUAL')

    def test_punctuator_xorequal(self):
        token = self._get_token('^=')
        self.assertEquals(token.type, 'XOREQUAL')

    def test_punctuator_orequal(self):
        token = self._get_token('|=')
        self.assertEquals(token.type, 'OREQUAL')
