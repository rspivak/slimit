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
from slimit.mangler import mangle


class ManglerTestCase(unittest.TestCase):

    TEST_CASES = [
        # test nested function declaration
        # test that object properties ids are not changed
        ("""
        function test() {
          function is_false() {
            var xpos = 5;
            var point = {
              xpos: 17,
              ypos: 10
            };
            return true;
          }
        }
        """,
         """
         function a() {
           function a() {
             var a = 5;
             var b = {
               xpos: 17,
               ypos: 10
             };
             return true;
           }
         }
         """),

        # test that mangled names are not shadowed when we reference
        # original names from any sub-scope
        ("""
        var result = function() {
          var long_name = 'long name';
          var not_so_long = 'indeed', log = 5;
          global_x = 56;
          console.log(long_name + not_so_long);
          new_result = function(arg1, arg2) {
            var arg2 = 'qwerty';
            console.log(long_name + not_so_long + arg1 + arg2 + global_x);
          };
        };
        """,
         """
         var a = function() {
           var a = 'long name';
           var b = 'indeed', c = 5;
           global_x = 56;
           console.log(a + b);
           new_result = function(c, d) {
             var d = 'qwerty';
             console.log(a + b + c + d + global_x);
           };
         };
         """),

        # https://github.com/rspivak/slimit/issues/7
        ("""
        function a() {
          var $exc1 = null;
          try {
            lala();
          } catch($exc) {
            if ($exc.__name__ == 'hi') {
              return 'bam';
            }
          }
          return 'bum';
        }
        """,
         """
         function a() {
           var a = null;
           try {
             lala();
           } catch (b) {
             if (b.__name__ == 'hi') {
               return 'bam';
             }
           }
           return 'bum';
         }
         """),

        # Handle the case when function arguments are redefined;
        # in the example below statement arg = 9; doesn't create
        # a global variable -it changes the value of arguments[0].
        # The same is with statement var arg = 0;
        # http://spin.atomicobject.com/2011/04/10/javascript-don-t-reassign-your-function-arguments/
        ("""
        function a(arg) {
          arg = 9;
          var arg = 0;
          return arg;
        }
        """,
         """
         function a(a) {
           a = 9;
           var a = 0;
           return a;
         }
         """),
        ]


def make_test_function(input, expected):

    def test_func(self):
        parser = Parser()
        tree = parser.parse(input)
        mangle(tree)
        self.assertMultiLineEqual(
            textwrap.dedent(tree.to_ecma()).strip(),
            textwrap.dedent(expected).strip()
            )

    return test_func

for index, (input, expected) in enumerate(ManglerTestCase.TEST_CASES):
    func = make_test_function(input, expected)
    setattr(ManglerTestCase, 'test_case_%d' % index, func)
