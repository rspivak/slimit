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
