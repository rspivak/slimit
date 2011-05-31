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


class SymbolTable(object):
    def __init__(self):
        self.globals = GlobalScope()


class Scope(object):

    def __init__(self, enclosing_scope=None):
        self.symbols = {}
        self.enclosing_scope = enclosing_scope
        self.name = ''

    def define(self, sym):
        self.symbols[sym.name] = sym
        # track scope for every symbol
        sym.scope = self

    def resolve(self, name):
        sym = self.symbols.get(name)
        if sym is not None:
            return sym
        elif self.enclosing_scope is not None:
            return enclosing_scope.resolve()

    def get_enclosing_scope(self):
        return self.enclosing_scope


class GlobalScope(Scope):
    pass


class LocalScope(Scope):
    pass


class Symbol(object):
    def __init__(self, name):
        self.name = name
        self.scope = None


class VarSymbol(Symbol):
    pass


class FuncSymbol(Symbol, Scope):
    """Function symbol is both a symbol and a scope for arguments."""

    def __init__(self, enclosing_scope):
        Symbol.__init__(self)
        Scope.__init__(self, enclosing_scope)


