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


class ECMAVisitorTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = 2000

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

        ################################
        # switch statement
        ################################
        """
        switch (day_of_week) {
          case 6:
          case 7:
            x = 'Weekend';
            break;
          case 1:
            x = 'Monday';
            break;
          default:
            break;
        }
        """,

        # test 24
        ################################
        # throw statement
        ################################
        """
        throw 'exc';
        """,

        ################################
        # debugger statement
        ################################
        'debugger;',

        ################################
        # expression statement
        ################################
        """
        5 + 7 - 20 * 10;
        ++x;
        --x;
        x++;
        x--;
        x = 17 /= 3;
        s = mot ? z : /x:3;x<5;y</g / i;
        """,

        # test 27
        ################################
        # try statement
        ################################
        """
        try {
          x = 3;
        } catch (exc) {
          x = exc;
        }
        """,

        """
        try {
          x = 3;
        } finally {
          x = null;
        }
        """,

        """
        try {
          x = 5;
        } catch (exc) {
          x = exc;
        } finally {
          y = null;
        }
        """,

        # test 30
        ################################
        # function
        ################################
        """
        function foo(x, y) {
          z = 10;
          return x + y + z;
        }
        """,

        """
        function foo() {
          return 10;
        }
        """,

        """
        var a = function() {
          return 10;
        };
        """,
        # test 33
        """
        var a = function foo(x, y) {
          return x + y;
        };
        """,
        # nested function declaration
        """
        function foo() {
          function bar() {

          }
        }
        """,

        """
        var mult = function(x) {
          return x * 10;
        }();
        """,

        # function call
        # test 36
        'foo();',
        'foo(x, 7);',
        'foo()[10];',
        # test 39
        'foo().foo;',

        ################################
        # misc
        ################################

        # new
        'var foo = new Foo();',
        # dot accessor
        'var bar = new Foo.Bar();',

        # test 42
        # bracket accessor
        'var bar = new Foo.Bar()[7];',

        # object literal
        """
        var obj = {
          foo: 10,
          bar: 20
        };
        """,
        """
        var obj = {
          1: 'a',
          2: 'b'
        };
        """,
        # test 45
        """
        var obj = {
          'a': 100,
          'b': 200
        };
        """,
        """
        var obj = {
        };
        """,

        # array
        """
        var a = [1,2,3,4,5];
        var res = a[3];
        """,
        # test 48
        # elision
        'var a = [,,,];',
        'var a = [1,,,4];',
        'var a = [1,,3,,5];',

        # test 51
        """
        String.prototype.foo = function(data) {
          var tmpl = this.toString();
          return tmpl.replace(/{{\s*(.*?)\s*}}/g, function(a, b) {
            var node = data;
            if (true) {
              var value = true;
            } else {
              var value = false;
            }
            $.each(n.split('.'), function(i, sym) {
              node = node[sym];
            });
            return node;
          });
        };
        """,

        #######################################
        # Make sure parentheses are not removed
        #######################################

        # ... Expected an identifier and instead saw '/'
        'Expr.match[type].source + (/(?![^\[]*\])(?![^\(]*\))/.source);',

        '(options = arguments[i]) != null;',

        # test 54
        'return (/h\d/i).test(elem.nodeName);',

        """
        (function() {
          x = 5;
        })();
        """,

        'return !(match === true || elem.getAttribute("classid") !== match);',

        # test 57
        'var el = (elem ? elem.ownerDocument || elem : 0).documentElement;',

        # typeof
        'typeof second.length === "number";',
        ]

def make_test_function(input, expected):

    def test_func(self):
        parser = Parser()
        result = parser.parse(input).to_ecma()
        self.assertMultiLineEqual(result, expected)

    return test_func

for index, input in enumerate(ECMAVisitorTestCase.TEST_CASES):
    input = textwrap.dedent(input).strip()
    func = make_test_function(input, input)
    setattr(ECMAVisitorTestCase, 'test_case_%d' % index, func)


