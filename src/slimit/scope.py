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

import itertools

try:
    from collections import OrderedDict
except ImportError:
    from odict import odict as OrderedDict

from slimit.lexer import Lexer


ID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def powerset(iterable):
    """powerset('abc') -> a b c ab ac bc abc"""
    s = list(iterable)
    for chars in itertools.chain.from_iterable(
        itertools.combinations(s, r) for r in range(1, len(s)+1)
        ):
        yield ''.join(chars)


class SymbolTable(object):
    def __init__(self):
        self.globals = GlobalScope()


class Scope(object):

    def __init__(self, enclosing_scope=None):
        self.symbols = OrderedDict()
        # {symbol.name: mangled_name}
        self.mangled = {}
        # {mangled_name: symbol.name}
        self.rev_mangled = {}
        # names referenced from this scope and all sub-scopes
        # {name: scope} key is the name, value is the scope that
        # contains referenced name
        self.refs = {}
        # set to True if this scope or any subscope contains 'eval'
        self.has_eval = False
        # set to True if this scope or any subscope contains 'wit
        self.has_with = False
        self.enclosing_scope = enclosing_scope
        # sub-scopes
        self.children = []
        # add ourselves as a child to the enclosing scope
        if enclosing_scope is not None:
            self.enclosing_scope.add_child(self)
        self.base54 = powerset(ID_CHARS)

    def __contains__(self, sym):
        return sym.name in self.symbols

    def add_child(self, scope):
        self.children.append(scope)

    def define(self, sym):
        self.symbols[sym.name] = sym
        # track scope for every symbol
        sym.scope = self

    def resolve(self, name):
        sym = self.symbols.get(name)
        if sym is not None:
            return sym
        elif self.enclosing_scope is not None:
            return self.enclosing_scope.resolve(name)

    def get_enclosing_scope(self):
        return self.enclosing_scope

    def _get_scope_with_mangled(self, name):
        """Return a scope containing passed mangled name."""
        scope = self
        while True:
            parent = scope.get_enclosing_scope()
            if parent is None:
                return

            if name in parent.rev_mangled:
                return parent

            scope = parent

    def _get_scope_with_symbol(self, name):
        """Return a scope containing passed name as a symbol name."""
        scope = self
        while True:
            parent = scope.get_enclosing_scope()
            if parent is None:
                return

            if name in parent.symbols:
                return parent

            scope = parent

    def get_next_mangled_name(self):
        """
        1. Do not shadow a mangled name from a parent scope
           if we reference the original name from that scope
           in this scope or any sub-scope.

        2. Do not shadow an original name from a parent scope
           if it's not mangled and we reference it in this scope
           or any sub-scope.

        """
        while True:
            mangled = self.base54.next()

            # case 1
            ancestor = self._get_scope_with_mangled(mangled)
            if (ancestor is not None
                and self.refs.get(ancestor.rev_mangled[mangled]) is ancestor
                ):
                continue

            # case 2
            ancestor = self._get_scope_with_symbol(mangled)
            if (ancestor is not None
                and self.refs.get(mangled) is ancestor
                and mangled not in ancestor.mangled
                ):
                continue

            # make sure a new mangled name is not a reserved word
            if mangled.upper() in Lexer.keywords:
                continue

            return mangled


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

    def __init__(self, name, enclosing_scope):
        Symbol.__init__(self, name)
        Scope.__init__(self, enclosing_scope)


