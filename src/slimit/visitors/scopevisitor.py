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

from slimit import ast
from slimit.scope import VarSymbol, FuncSymbol, LocalScope, SymbolTable


class Visitor(object):
    def visit(self, node):
        method = 'visit_%s' % node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        if node is None:
            return
        if isinstance(node, list):
            for child in node:
                self.visit(child)
        else:
            for child in node.children():
                self.visit(child)


class ScopeTreeVisitor(Visitor):
    """Builds scope tree."""

    def __init__(self, sym_table):
        self.sym_table = sym_table
        self.current_scope = sym_table.globals

    def visit_Assign(self, node):
        # property_assignment
        # skip identifier
        if node.op == ':' and isinstance(node.left, ast.Identifier):
            self.visit(node.right)
        else:
            self.visit(node.left)
            self.visit(node.right)

    def visit_VarDecl(self, node):
        ident = node.identifier
        symbol = VarSymbol(name=ident.value)
        self.current_scope.define(symbol)
        ident.scope = self.current_scope
        self.visit(node.initializer)

    def visit_Identifier(self, node):
        node.scope = self.current_scope

    def visit_FuncDecl(self, node):
        if node.identifier is not None:
            name = node.identifier.value
            self.visit_Identifier(node.identifier)
        else:
            name = None

        func_sym = FuncSymbol(
            name=name, enclosing_scope=self.current_scope)
        if name is not None:
            self.current_scope.define(func_sym)
            node.scope = self.current_scope

        # push function scope
        self.current_scope = func_sym
        for ident in node.parameters:
            self.current_scope.define(VarSymbol(ident.value))
            ident.scope = self.current_scope

        # push local scope
        self.current_scope = LocalScope(self.current_scope)

        for element in node.elements:
            self.visit(element)

        # pop the local scope
        self.current_scope = self.current_scope.get_enclosing_scope()
        # pop the function scope
        self.current_scope = self.current_scope.get_enclosing_scope()

    # alias
    visit_FuncExpr = visit_FuncDecl


class RefVisitor(Visitor):
    """Fill 'ref' attribute in scopes."""

    def visit_VarDecl(self, node):
        # we skip Identifier node because it's not part of an expression
        self.visit(node.initializer)

    def visit_FuncDecl(self, node):
        # we skip all Identifier nodes because they are not part of expressions
        for element in node.elements:
            self.visit(element)
    # alias
    visit_FuncExpr = visit_FuncDecl

    def visit_DotAccessor(self, node):
        # we skip identifier
        self.visit(node.node)

    def visit_Identifier(self, node):
        if getattr(node, 'scope', None) is not None:
            self._fill_scope_refs(node.value, node.scope)

    def _fill_scope_refs(self, name, scope):
        """Put referenced name in 'ref' dictionary of a scope.

        Walks up the scope tree and adds the name to 'ref' of every scope
        up in the tree until a scope that defines referenced name is reached.
        """
        symbol = scope.resolve(name)
        if symbol is None:
            return

        orig_scope = symbol.scope
        scope.refs[name] = orig_scope
        while scope is not orig_scope:
            scope = scope.get_enclosing_scope()
            scope.refs[name] = orig_scope


def mangle_scope_tree(root):
    """Walk over a scope tree and mangle symbol names."""
    def mangle(scope):
        for name in scope.symbols:
            mangled_name = scope.get_next_mangled_name()
            scope.mangled[name] = mangled_name
            scope.rev_mangled[mangled_name] = name

    def visit(node):
        mangle(node)
        for child in node.children:
            visit(child)

    visit(root)


def fill_scope_references(tree):
    """Fill 'ref' scope attribute with values."""
    visitor = RefVisitor()
    visitor.visit(tree)


class NameManglerVisitor(Visitor):
    """Mangles names.

    Walks over a parsed tree and changes ID values to corresponding
    mangled names.
    """

    def visit_VarDecl(self, node):
        self.visit(node.identifier)
        self.visit(node.initializer)

    def visit_FuncDecl(self, node):
        if node.identifier is not None:
            self.visit(node.identifier)

        for param in node.parameters:
            self.visit(param)

        for element in node.elements:
            self.visit(element)

    visit_FuncExpr = visit_FuncDecl

    def visit_Assign(self, node):
        # property_assignment
        # skip identifier
        if node.op == ':' and isinstance(node.left, ast.Identifier):
            self.visit(node.right)
        else:
            self.visit(node.left)
            self.visit(node.right)

    def visit_DotAccessor(self, node):
        self.visit(node.node)

    def visit_Identifier(self, node):
        """Mangle names."""
        if getattr(node, 'scope', None) is None:
            return
        name = node.value
        symbol = node.scope.resolve(node.value)
        if symbol is None:
            return
        mangled = symbol.scope.mangled.get(name)
        if mangled is not None:
            node.value = mangled
