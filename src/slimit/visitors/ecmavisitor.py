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


class ECMAVisitor(object):

    def __init__(self):
        self.indent_level = 0

    def _make_indent(self):
        return ' ' * self.indent_level

    def visit(self, node):
        method = 'visit_%s' % node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        return 'GEN: %r' % node

    def visit_Program(self, node):
        return '\n'.join(self.visit(child) for child in node)

    def visit_Block(self, node):
        s = '{\n'
        self.indent_level += 2
        s += '\n'.join(
            self._make_indent() + self.visit(child) for child in node)
        self.indent_level -= 2
        s += '\n' + self._make_indent() + '}'
        return s

    def visit_VarStatement(self, node):
        s = 'var %s;' % ', '.join(self.visit(child) for child in node)
        return s

    def visit_VarDecl(self, node):
        output = []
        output.append(self.visit(node.identifier))
        if node.initializer is not None:
            output.append(' = %s' % self.visit(node.initializer))
        return ''.join(output)

    def visit_Identifier(self, node):
        return node.value

    def visit_Assign(self, node):
        if node.op == ':':
            template = '%s%s %s'
        else:
            template = '%s %s %s'
        if getattr(node, '_parens', False):
            template = '(%s)' % template
        return template % (
            self.visit(node.left), node.op, self.visit(node.right))

    def visit_GetPropAssign(self, node):
        template = 'get %s() {\n%s\n%s}'
        if getattr(node, '_parens', False):
            template = '(%s)' % template
        self.indent_level += 2
        body = '\n'.join(
            (self._make_indent() + self.visit(el))
            for el in node.elements
            )
        self.indent_level -= 2
        tail = self._make_indent()
        return template % (self.visit(node.prop_name), body, tail)

    def visit_SetPropAssign(self, node):
        template = 'set %s(%s) {\n%s\n%s}'
        if getattr(node, '_parens', False):
            template = '(%s)' % template
        if len(node.parameters) > 1:
            raise SyntaxError(
                'Setter functions must have one argument: %s' % node)
        params = ','.join(self.visit(param) for param in node.parameters)
        self.indent_level += 2
        body = '\n'.join(
            (self._make_indent() + self.visit(el))
            for el in node.elements
            )
        self.indent_level -= 2
        tail = self._make_indent()
        return template % (self.visit(node.prop_name), params, body, tail)

    def visit_Number(self, node):
        return node.value

    def visit_Comma(self, node):
        s = '%s, %s' % (self.visit(node.left), self.visit(node.right))
        if getattr(node, '_parens', False):
            s = '(' + s + ')'
        return s

    def visit_EmptyStatement(self, node):
        return node.value

    def visit_If(self, node):
        s = 'if ('
        if node.predicate is not None:
            s += self.visit(node.predicate)
        s += ') '
        s += self.visit(node.consequent)
        if node.alternative is not None:
            s += ' else '
            s += self.visit(node.alternative)
        return s

    def visit_Boolean(self, node):
        return node.value

    def visit_For(self, node):
        s = 'for ('
        if node.init is not None:
            s += self.visit(node.init)
        if node.init is None:
            s += ' ; '
        elif isinstance(node.init, (ast.Assign, ast.Comma, ast.FunctionCall,
                                    ast.UnaryOp, ast.Identifier, ast.BinOp,
                                    ast.Conditional, ast.Regex, ast.NewExpr)):
            s += '; '
        else:
            s += ' '
        if node.cond is not None:
            s += self.visit(node.cond)
        s += '; '
        if node.count is not None:
            s += self.visit(node.count)
        s += ') ' + self.visit(node.statement)
        return s

    def visit_ForIn(self, node):
        if isinstance(node.item, ast.VarDecl):
            template = 'for (var %s in %s) '
        else:
            template = 'for (%s in %s) '
        s = template % (self.visit(node.item), self.visit(node.iterable))
        s += self.visit(node.statement)
        return s

    def visit_BinOp(self, node):
        if getattr(node, '_parens', False):
            template = '(%s %s %s)'
        else:
            template = '%s %s %s'
        return template % (
            self.visit(node.left), node.op, self.visit(node.right))

    def visit_UnaryOp(self, node):
        s = self.visit(node.value)
        if node.postfix:
            s += node.op
        elif node.op in ('delete', 'void', 'typeof'):
            s = '%s %s' % (node.op, s)
        else:
            s = '%s%s' % (node.op, s)
        if getattr(node, '_parens', False):
            s = '(%s)' % s
        return s

    def visit_ExprStatement(self, node):
        return '%s;' % self.visit(node.expr)

    def visit_DoWhile(self, node):
        s = 'do '
        s += self.visit(node.statement)
        s += ' while (%s);' % self.visit(node.predicate)
        return s

    def visit_While(self, node):
        s = 'while (%s) ' % self.visit(node.predicate)
        s += self.visit(node.statement)
        return s

    def visit_Null(self, node):
        return 'null'

    def visit_String(self, node):
        return node.value

    def visit_Continue(self, node):
        if node.identifier is not None:
            s = 'continue %s;' % self.visit_Identifier(node.identifier)
        else:
            s = 'continue;'
        return s

    def visit_Break(self, node):
        if node.identifier is not None:
            s = 'break %s;' % self.visit_Identifier(node.identifier)
        else:
            s = 'break;'
        return s

    def visit_Return(self, node):
        if node.expr is None:
            return 'return;'
        else:
            return 'return %s;' % self.visit(node.expr)

    def visit_With(self, node):
        s = 'with (%s) ' % self.visit(node.expr)
        s += self.visit(node.statement)
        return s

    def visit_Label(self, node):
        s = '%s: %s' % (
            self.visit(node.identifier), self.visit(node.statement))
        return s

    def visit_Switch(self, node):
        s = 'switch (%s) {\n' % self.visit(node.expr)
        self.indent_level += 2
        for case in node.cases:
            s += self._make_indent() + self.visit_Case(case)
        if node.default is not None:
            s += self.visit_Default(node.default)
        self.indent_level -= 2
        s += self._make_indent() + '}'
        return s

    def visit_Case(self, node):
        s = 'case %s:\n' % self.visit(node.expr)
        self.indent_level += 2
        elements = '\n'.join(self._make_indent() + self.visit(element)
                             for element in node.elements)
        if elements:
            s += elements + '\n'
        self.indent_level -= 2
        return s

    def visit_Default(self, node):
        s = self._make_indent() + 'default:\n'
        self.indent_level += 2
        s += '\n'.join(self._make_indent() + self.visit(element)
                       for element in node.elements)
        if node.elements is not None:
            s += '\n'
        self.indent_level -= 2
        return s

    def visit_Throw(self, node):
        s = 'throw %s;' % self.visit(node.expr)
        return s

    def visit_Debugger(self, node):
        return '%s;' % node.value

    def visit_Try(self, node):
        s = 'try '
        s += self.visit(node.statements)
        if node.catch is not None:
            s += ' ' + self.visit(node.catch)
        if node.fin is not None:
            s += ' ' + self.visit(node.fin)
        return s

    def visit_Catch(self, node):
        s = 'catch (%s) %s' % (
            self.visit(node.identifier), self.visit(node.elements))
        return s

    def visit_Finally(self, node):
        s = 'finally %s' % self.visit(node.elements)
        return s

    def visit_FuncDecl(self, node):
        self.indent_level += 2
        elements = '\n'.join(self._make_indent() + self.visit(element)
                             for element in node.elements)
        self.indent_level -= 2

        s = 'function %s(%s) {\n%s' % (
            self.visit(node.identifier),
            ', '.join(self.visit(param) for param in node.parameters),
            elements,
            )
        s += '\n' + self._make_indent() + '}'
        return s

    def visit_FuncExpr(self, node):
        self.indent_level += 2
        elements = '\n'.join(self._make_indent() + self.visit(element)
                             for element in node.elements)
        self.indent_level -= 2

        ident = node.identifier
        ident = '' if ident is None else ' %s' % self.visit(ident)

        header = 'function%s(%s)'
        if getattr(node, '_parens', False):
            header = '(' + header
        s = (header + ' {\n%s') % (
            ident,
            ', '.join(self.visit(param) for param in node.parameters),
            elements,
            )
        s += '\n' + self._make_indent() + '}'
        if getattr(node, '_parens', False):
            s += ')'
        return s

    def visit_Conditional(self, node):
        if getattr(node, '_parens', False):
            template = '(%s ? %s : %s)'
        else:
            template = '%s ? %s : %s'

        s = template % (
            self.visit(node.predicate),
            self.visit(node.consequent), self.visit(node.alternative))
        return s

    def visit_Regex(self, node):
        if getattr(node, '_parens', False):
            return '(%s)' % node.value
        else:
            return node.value

    def visit_NewExpr(self, node):
        s = 'new %s(%s)' % (
            self.visit(node.identifier),
            ', '.join(self.visit(arg) for arg in node.args)
            )
        return s

    def visit_DotAccessor(self, node):
        if getattr(node, '_parens', False):
            template = '(%s.%s)'
        else:
            template = '%s.%s'
        s = template % (self.visit(node.node), self.visit(node.identifier))
        return s

    def visit_BracketAccessor(self, node):
        s = '%s[%s]' % (self.visit(node.node), self.visit(node.expr))
        return s

    def visit_FunctionCall(self, node):
        s = '%s(%s)' % (self.visit(node.identifier),
                        ', '.join(self.visit(arg) for arg in node.args))
        if getattr(node, '_parens', False):
            s = '(' + s + ')'
        return s

    def visit_Object(self, node):
        s = '{\n'
        self.indent_level += 2
        s += ',\n'.join(self._make_indent() + self.visit(prop)
                        for prop in node.properties)
        self.indent_level -= 2
        if node.properties:
            s += '\n'
        s += self._make_indent() + '}'
        return s

    def visit_Array(self, node):
        s = '['
        length = len(node.items) - 1
        for index, item in enumerate(node.items):
            if isinstance(item, ast.Elision):
                s += ','
            elif index != length:
                s += self.visit(item) + ','
            else:
                s += self.visit(item)
        s += ']'
        return s

    def visit_This(self, node):
        return 'this'

