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

import textwrap
import unittest

from slimit.parser import Parser
from slimit.visitors.ecmavisitor import ECMAVisitor


class ECMAVisitorTestCase(unittest.TestCase):

    TEST_CASES = [
        ################################
        # block
        ################################
        """
        {
          var a = 5;
        }
        """,

        ################################
        # variable statement
        ################################
        """
        var a;
        var b;
        var a, b = 3;
        var a = 1, b;
        var a = 5, b = 7;
        """,

        # empty statement
        """
        ;
        ;
        ;
        """,

        # test 3
        ################################
        # if
        ################################
        'if (true) var x = 100;',

        """
        if (true) {
          var x = 100;
          var y = 200;
        }
        """,

        'if (true) if (true) var x = 100; else var y = 200;',

        # test 6
        """
        if (true) {
          var x = 100;
        } else {
          var y = 200;
        }
        """,
        ################################
        # iteration
        ################################
        """
        for (i = 0; i < 10; i++) {
          x = 10 * i;
        }
        """,

        """
        for (var i = 0; i < 10; i++) {
          x = 10 * i;
        }
        """,

        # test 9
        """
        for (i = 0, j = 10; i < j && j < 15; i++, j++) {
          x = i * j;
        }
        """,

        """
        for (var i = 0, j = 10; i < j && j < 15; i++, j++) {
          x = i * j;
        }
        """,

        """
        for (p in obj) {

        }
        """,

        # test 12
        """
        for (var p in obj) {
          p = 1;
        }
        """,

        """
        do {
          x += 1;
        } while (true);
        """,

        """
        while (false) {
          x = null;
        }
        """,

        # test 15
        ################################
        # continue statement
        ################################
        """
        while (true) {
          continue;
          s = 'I am not reachable';
        }
        """,

        """
        while (true) {
          continue label1;
          s = 'I am not reachable';
        }
        """,

        ################################
        # break statement
        ################################
        """
        while (true) {
          break;
          s = 'I am not reachable';
        }
        """,
        # test 18
        """
        while (true) {
          break label1;
          s = 'I am not reachable';
        }
        """,

        ################################
        # return statement
        ################################
        """
        {
          return;
        }
        """,

        """
        {
          return 1;
        }
        """,

        # test21
        ################################
        # with statement
        ################################
        """
        with (x) {
          var y = x * 2;
        }
        """,

        ################################
        # labelled statement
        ################################
        """
        label: while (true) {
          x *= 3;
        }
        """,
        ]

def make_test_function(input, expected):

    def test_func(self):
        parser = Parser()
        visitor = ECMAVisitor()
        result = visitor.visit(parser.parse(input))
        self.assertMultiLineEqual(result, expected)

    return test_func

for index, input in enumerate(ECMAVisitorTestCase.TEST_CASES):
    input = textwrap.dedent(input).strip()
    func = make_test_function(input, input)
    setattr(ECMAVisitorTestCase, 'test_case_%d' % index, func)
