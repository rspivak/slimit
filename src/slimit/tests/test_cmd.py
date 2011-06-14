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

import os
import sys
import StringIO
import tempfile
import unittest

from contextlib import contextmanager


@contextmanager
def redirected_input_output(input=''):
    old_inp, old_out = sys.stdin, sys.stdout
    inp, out = StringIO.StringIO(input), StringIO.StringIO()
    sys.stdin, sys.stdout = inp, out
    try:
        yield out
    finally:
        sys.stdin, sys.stdout = old_inp, old_out


@contextmanager
def redirected_sys_argv(argv):
    old = sys.argv
    sys.argv = argv
    try:
        yield argv
    finally:
        sys.argv = old


class CmdTestCase(unittest.TestCase):

    def setUp(self):
        fd, path = tempfile.mkstemp()
        self.path = path
        with os.fdopen(fd, 'w') as fout:
            fout.write('var global = 5;')

    def tearDown(self):
        os.remove(self.path)

    def test_main_dash_m_with_input_file(self):
        from slimit.minifier import main
        out = StringIO.StringIO()
        main(['-m', self.path], out=out)
        self.assertEqual('var a=5;', out.getvalue())

    def test_main_dash_dash_mangle_with_input_file(self):
        from slimit.minifier import main
        out = StringIO.StringIO()
        main(['--mangle', self.path], out=out)
        self.assertEqual('var a=5;', out.getvalue())

    def test_main_dash_m_with_mock_stdin(self):
        from slimit.minifier import main
        out = StringIO.StringIO()
        inp = StringIO.StringIO('var global = 5;')
        main(['-m'], inp=inp, out=out)
        self.assertEqual('var a=5;', out.getvalue())

    def test_main_stdin_stdout(self):
        # slimit.minifier should be deleted from sys.modules in order
        # to have a proper reference to sys.stdin and sys.stdou when
        # 'main' definition is evaluated during module import
        try:
            del sys.modules['slimit.minifier']
        except KeyError:
            pass

        with redirected_input_output(input='var global = 5;') as out:
            from slimit.minifier import main
            main(['-m'])

        self.assertEqual('var a=5;', out.getvalue())

    def test_main_sys_argv(self):
        out = StringIO.StringIO()
        inp = StringIO.StringIO('var global = 5;')
        with redirected_sys_argv(['slimit', '-m']):
            from slimit.minifier import main
            main(inp=inp, out=out)

        self.assertEqual('var a=5;', out.getvalue())

