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


class Node(object):
    def __init__(self, children=None):
        self.children = [] if children is None else children

    # def to_ecma(self):
    #     visitor = ECMAVisitor()
    #     return visitor.visit(self)

class Program(Node):
    pass

class Block(Node):
    pass

class Boolean(Node):
    def __init__(self, value):
        self.value = value

class Null(Node):
    pass

class Number(Node):
    def __init__(self, value):
        self.value = value

class Identifier(Node):
    def __init__(self, value):
        self.value = value

class String(Node):
    def __init__(self, value):
        self.value = value

class Regex(Node):
    def __init__(self, value):
        self.value = value

class Array(Node):
    pass

class Object(Node):
    def __init__(self, properties=None):
        self.properties = [] if properties is None else properties

class NewExpr(Node):
    def __init__(self, identifier, args=None):
        self.identifier = identifier
        self.args = [] if args is None else args

class FunctionCall(Node):
    def __init__(self, identifier, args=None):
        self.identifier = identifier
        self.args = [] if args is None else args

class BracketAccessor(Node):
    def __init__(self, node, el):
        self.node = node
        self.el = el

class DotAccessor(Node):
    def __init__(self, node, el):
        self.node = node
        self.el = el

class Assign(Node):
    def __init__(self, left, op, right):
        self.op = op
        self.left = left
        self.right = right

class VarStatement(Node):
    pass

class VarDecl(Node):
    def __init__(self, identifier, initializer=None):
        self.identifier = identifier
        self.initializer = initializer

class UnaryOp(Node):
    def __init__(self, op, value, postfix=False):
        self.op = op
        self.value = value
        self.postfix = postfix

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class Conditional(Node):
    """Conditional Operator ( ? : )"""
    def __init__(self, predicate, consequent, alternative):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative

class If(Node):
    def __init__(self, predicate, consequent, alternative=None):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative

class DoWhile(Node):
    def __init__(self, predicate, statement):
        self.predicate = predicate
        self.statement = statement

class While(Node):
    def __init__(self, predicate, statement):
        self.predicate = predicate
        self.statement = statement

class For(Node):
    def __init__(self, init, cond, count, statement):
        self.init = init
        self.cond = cond
        self.count = count
        self.statement = statement

class ForIn(Node):
    def __init__(self, item, iterable, statement):
        self.item = item
        self.iterable = iterable
        self.statement = statement

class Continue(Node):
    def __init__(self, identifier=None):
        self.identifier = identifier

class Break(Node):
    def __init__(self, identifier=None):
        self.identifier = identifier

class Return(Node):
    def __init__(self, expr=None):
        self.expr = expr

class With(Node):
    def __init__(self, expr, statement):
        self.expr = expr
        self.statement = statement

class Switch(Node):
    def __init__(self, expr, cases, default=None):
        self.expr = expr
        self.cases = cases
        self.default = default

class Case(Node):
    def __init__(self, expr, elements):
        self.expr = expr
        self.elements = elements

class Default(Node):
    def __init__(self, elements):
        self.elements = elements

class Label(Node):
    def __init__(self, identifier, statement):
        self.identifier = identifier
        self.statement = statement

class Throw(Node):
    def __init__(self, expr):
        self.expr = expr

class Try(Node):
    def __init__(self, statements, catch=None, fin=None):
        self.statements = statements
        self.catch = catch
        self.fin = fin

class Catch(Node):
    def __init__(self, identifier, elements):
        self.identifier = identifier
        self.elements = elements

class Finally(Node):
    def __init__(self, elements):
        self.elements = elements

class Debugger(Node):
    def __init__(self, value):
        self.value = value

class FuncDecl(Node):
    def __init__(self, identifier, parameters, elements):
        self.identifier = identifier
        self.parameters = parameters
        self.elements = elements

class FuncExpr(Node):
    def __init__(self, identifier, parameters, elements):
        self.identifier = identifier
        self.parameters = parameters
        self.elements = elements

class Comma(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class EmptyStatement(Node):
    def __init__(self, value):
        self.value = value

class ExprStatement(Node):
    def __init__(self, expr):
        self.expr = expr

