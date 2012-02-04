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

import re

from slimit import ast
from slimit.lexer import Lexer

_HAS_ID_MATCH = re.compile('^%s$' % Lexer.identifier).match

def _is_identifier(value):
    return _HAS_ID_MATCH(value) and value not in Lexer.keywords_dict


class ECMAMinifier(object):

    def __init__(self):
        self.in_block = 0
        self.ifelse_stack = []

    def visit(self, node):
        method = 'visit_%s' % node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        return 'GEN: %r' % node

    def visit_Program(self, node):
        return ''.join(self.visit(child) for child in node)

    def visit_Block(self, node):
        children = [self.visit(child) for child in node]
        if len(children) == 1:
            return children[0]
        else:
            return '{%s}' % ''.join(children)

    def visit_VarStatement(self, node):
        s = 'var %s;' % ','.join(self.visit(child) for child in node)
        return s

    def visit_VarDecl(self, node):
        output = []
        output.append(self.visit(node.identifier))
        if node.initializer is not None:
            output.append('=%s' % self.visit(node.initializer))
        return ''.join(output)

    def visit_Identifier(self, node):
        return node.value

    def visit_Assign(self, node):
        template = '%s%s%s'
        if getattr(node, '_parens', False):
            template = '(%s)' % template
        return template % (
            self.visit(node.left), node.op, self.visit(node.right))

    def visit_Number(self, node):
        return node.value

    def visit_Comma(self, node):
        template = '%s,%s'
        if getattr(node, '_parens', False):
            template = '(%s)' % template
        return template % (self.visit(node.left), self.visit(node.right))

    def visit_EmptyStatement(self, node):
        return node.value

    def visit_If(self, node):
        has_alternative = node.alternative is not None

        def _is_singleline_block(n):
            return isinstance(n, ast.Block) and (len(n.children()) == 1)

        s = 'if('
        if node.predicate is not None:
            s += self.visit(node.predicate)
        s += ')'

        # if we are an 'if..else' statement and 'if' part contains only
        # one statement
        if has_alternative and _is_singleline_block(node.consequent):
            self.ifelse_stack.append({'if_in_ifelse': False})
            consequent = self.visit(node.consequent)
            record = self.ifelse_stack.pop()
            if record['if_in_ifelse']:
                s += '{%s}' % consequent
            else:
                s += consequent
        elif has_alternative:
            # we are an 'if..else' statement and 'if' part contains
            # myltiple statements
            s += self.visit(node.consequent)
        else:
            # 'if' without alternative - mark it so that an enclosing
            # 'if..else' can act on it and add braces around 'if' part
            if self.ifelse_stack:
                self.ifelse_stack[-1]['if_in_ifelse'] = True
            s += self.visit(node.consequent)

        if has_alternative:
            alternative = self.visit(node.alternative)
            if alternative.startswith(('(', '{')):
                s += 'else%s' % alternative
            else:
                s += 'else %s' % alternative
        return s

    def visit_Boolean(self, node):
        return node.value

    def visit_For(self, node):
        s = 'for('
        if node.init is not None:
            s += self.visit(node.init)
        if node.init is None:
            s += ';'
        elif isinstance(node.init, (ast.Assign, ast.Comma)):
            s += ';'
        else:
            s += ''
        if node.cond is not None:
            s += self.visit(node.cond)
        s += ';'
        if node.count is not None:
            s += self.visit(node.count)
        s += ')' + self.visit(node.statement)
        return s

    def visit_ForIn(self, node):
        if isinstance(node.item, ast.VarDecl):
            template = 'for(var %s in %s)'
        else:
            template = 'for(%s in %s)'
        s = template % (self.visit(node.item), self.visit(node.iterable))
        s += self.visit(node.statement)
        return s

    def visit_BinOp(self, node):
        if node.op in ('instanceof', 'in'):
            template = '%s %s %s'
        else:
            template = '%s%s%s'
        if getattr(node, '_parens', False):
            template = '(%s)' % template
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
        statement = self.visit(node.statement)
        if statement.startswith(('{', '(')):
            s = 'do%s' % statement
        else:
            s = 'do %s' % statement
        s += 'while(%s);' % self.visit(node.predicate)
        return s

    def visit_While(self, node):
        s = 'while(%s)' % self.visit(node.predicate)
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

        expr_text = self.visit(node.expr)
        if expr_text.startswith(('(', '{')):
            return 'return%s;' % expr_text
        else:
            return 'return %s;' % expr_text

    def visit_With(self, node):
        s = 'with(%s)' % self.visit(node.expr)
        s += self.visit(node.statement)
        return s

    def visit_Label(self, node):
        s = '%s:%s' % (
            self.visit(node.identifier), self.visit(node.statement))
        return s

    def visit_Switch(self, node):
        s = 'switch(%s){' % self.visit(node.expr)
        for case in node.cases:
            s += self.visit_Case(case)
        if node.default is not None:
            s += self.visit_Default(node.default)
        s += '}'
        return s

    def visit_Case(self, node):
        s = 'case %s:' % self.visit(node.expr)
        elements = ''.join(self.visit(element) for element in node.elements)
        if elements:
            s += elements
        return s

    def visit_Default(self, node):
        s = 'default:'
        s += ''.join(self.visit(element) for element in node.elements)
        if node.elements is not None:
            s += ''
        return s

    def visit_Throw(self, node):
        s = 'throw %s;' % self.visit(node.expr)
        return s

    def visit_Debugger(self, node):
        return '%s;' % node.value

    def visit_Try(self, node):
        result = self.visit(node.statements)
        if result.startswith('{'):
            s = 'try%s' % result
        else:
            s = 'try{%s}' % result
        if node.catch is not None:
            s += self.visit(node.catch)
        if node.fin is not None:
            s += self.visit(node.fin)
        return s

    def visit_Catch(self, node):
        ident = self.visit(node.identifier)
        result = self.visit(node.elements)
        if result.startswith('{'):
            s = 'catch(%s)%s' % (ident, result)
        else:
            s = 'catch(%s){%s}' % (ident, result)
        return s

    def visit_Finally(self, node):
        result = self.visit(node.elements)
        if result.startswith('{'):
            s = 'finally%s' % result
        else:
            s = 'finally{%s}' % result
        return s

    def visit_FuncDecl(self, node):
        elements = ''.join(self.visit(element) for element in node.elements)
        s = 'function %s(%s){%s' % (
            self.visit(node.identifier),
            ','.join(self.visit(param) for param in node.parameters),
            elements,
            )
        s += '}'
        return s

    def visit_FuncExpr(self, node):
        elements = ''.join(self.visit(element) for element in node.elements)

        ident = node.identifier
        ident = '' if ident is None else ' %s' % self.visit(ident)

        header = 'function%s(%s)'
        if getattr(node, '_parens', False):
            header = '(' + header
        s = (header + '{%s') % (
            ident,
            ','.join(self.visit(param) for param in node.parameters),
            elements,
            )
        s += '}'
        if getattr(node, '_parens', False):
            s += ')'
        return s

    def visit_Conditional(self, node):
        if getattr(node, '_parens', False):
            template = '(%s?%s:%s)'
        else:
            template = '%s?%s:%s'

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
            ','.join(self.visit(arg) for arg in node.args)
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
        if isinstance(node.expr, ast.String):
            value = node.expr.value
            # remove single or double quotes around the value, but not both
            if value.startswith("'"):
                value = value.strip("'")
            elif value.startswith('"'):
                value = value.strip('"')
            if _is_identifier(value):
                s = '%s.%s' % (self.visit(node.node), value)
                return s

        s = '%s[%s]' % (self.visit(node.node), self.visit(node.expr))
        return s

    def visit_FunctionCall(self, node):
        s = '%s(%s)' % (self.visit(node.identifier),
                        ','.join(self.visit(arg) for arg in node.args))
        return s

    def visit_Object(self, node):
        s = '{%s}' % ','.join(self.visit(prop) for prop in node.properties)
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

