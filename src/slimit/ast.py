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
        self._children_list = [] if children is None else children

    def __iter__(self):
        for child in self.children():
            if child is not None:
                yield child

    def children(self):
        return self._children_list

    def to_ecma(self):
        # Can't import at module level as ecmavisitor depends
        # on ast module...
        from slimit.visitors.ecmavisitor import ECMAVisitor
        visitor = ECMAVisitor()
        return visitor.visit(self)

class Program(Node):
    pass

class Block(Node):
    pass

class Boolean(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Null(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Number(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Identifier(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class String(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Regex(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class Array(Node):
    def __init__(self, items):
        self.items = items

    def children(self):
        return self.items

class Object(Node):
    def __init__(self, properties=None):
        self.properties = [] if properties is None else properties

    def children(self):
        return self.properties

class NewExpr(Node):
    def __init__(self, identifier, args=None):
        self.identifier = identifier
        self.args = [] if args is None else args

    def children(self):
        return [self.identifier, self.args]

class FunctionCall(Node):
    def __init__(self, identifier, args=None):
        self.identifier = identifier
        self.args = [] if args is None else args

    def children(self):
        return [self.identifier] + self.args

class BracketAccessor(Node):
    def __init__(self, node, expr):
        self.node = node
        self.expr = expr

    def children(self):
        return [self.node, self.expr]

class DotAccessor(Node):
    def __init__(self, node, identifier):
        self.node = node
        self.identifier = identifier

    def children(self):
        return [self.node, self.identifier]

class Assign(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

class GetPropAssign(Node):
    def __init__(self, prop_name, elements):
        """elements - function body"""
        self.prop_name = prop_name
        self.elements = elements

    def children(self):
        return [self.prop_name] + self.elements

class SetPropAssign(Node):
    def __init__(self, prop_name, parameters, elements):
        """elements - function body"""
        self.prop_name = prop_name
        self.parameters = parameters
        self.elements = elements

    def children(self):
        return [self.prop_name] + self.parameters + self.elements

class VarStatement(Node):
    pass

class VarDecl(Node):
    def __init__(self, identifier, initializer=None):
        self.identifier = identifier
        self.identifier._mangle_candidate = True
        self.initializer = initializer

    def children(self):
        return [self.identifier, self.initializer]

class UnaryOp(Node):
    def __init__(self, op, value, postfix=False):
        self.op = op
        self.value = value
        self.postfix = postfix

    def children(self):
        return [self.value]

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

class Conditional(Node):
    """Conditional Operator ( ? : )"""
    def __init__(self, predicate, consequent, alternative):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative

    def children(self):
        return [self.predicate, self.consequent, self.alternative]

class If(Node):
    def __init__(self, predicate, consequent, alternative=None):
        self.predicate = predicate
        self.consequent = consequent
        self.alternative = alternative

    def children(self):
        return [self.predicate, self.consequent, self.alternative]

class DoWhile(Node):
    def __init__(self, predicate, statement):
        self.predicate = predicate
        self.statement = statement

    def children(self):
        return [self.predicate, self.statement]

class While(Node):
    def __init__(self, predicate, statement):
        self.predicate = predicate
        self.statement = statement

    def children(self):
        return [self.predicate, self.statement]

class For(Node):
    def __init__(self, init, cond, count, statement):
        self.init = init
        self.cond = cond
        self.count = count
        self.statement = statement

    def children(self):
        return [self.init, self.cond, self.count, self.statement]

class ForIn(Node):
    def __init__(self, item, iterable, statement):
        self.item = item
        self.iterable = iterable
        self.statement = statement

    def children(self):
        return [self.item, self.iterable, self.statement]

class Continue(Node):
    def __init__(self, identifier=None):
        self.identifier = identifier

    def children(self):
        return [self.identifier]

class Break(Node):
    def __init__(self, identifier=None):
        self.identifier = identifier

    def children(self):
        return [self.identifier]

class Return(Node):
    def __init__(self, expr=None):
        self.expr = expr

    def children(self):
        return [self.expr]

class With(Node):
    def __init__(self, expr, statement):
        self.expr = expr
        self.statement = statement

    def children(self):
        return [self.expr, self.statement]

class Switch(Node):
    def __init__(self, expr, cases, default=None):
        self.expr = expr
        self.cases = cases
        self.default = default

    def children(self):
        return [self.expr] + self.cases + [self.default]

class Case(Node):
    def __init__(self, expr, elements):
        self.expr = expr
        self.elements = elements if elements is not None else []

    def children(self):
        return [self.expr] + self.elements

class Default(Node):
    def __init__(self, elements):
        self.elements = elements if elements is not None else []

    def children(self):
        return self.elements

class Label(Node):
    def __init__(self, identifier, statement):
        self.identifier = identifier
        self.statement = statement

    def children(self):
        return [self.identifier, self.statement]

class Throw(Node):
    def __init__(self, expr):
        self.expr = expr

    def children(self):
        return [self.expr]

class Try(Node):
    def __init__(self, statements, catch=None, fin=None):
        self.statements = statements
        self.catch = catch
        self.fin = fin

    def children(self):
        return [self.statements] + [self.catch, self.fin]

class Catch(Node):
    def __init__(self, identifier, elements):
        self.identifier = identifier
        # CATCH identifiers are subject to name mangling. we need to mark them.
        self.identifier._mangle_candidate = True
        self.elements = elements

    def children(self):
        return [self.identifier, self.elements]

class Finally(Node):
    def __init__(self, elements):
        self.elements = elements

    def children(self):
        return self.elements

class Debugger(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []


class FuncBase(Node):
    def __init__(self, identifier, parameters, elements):
        self.identifier = identifier
        self.parameters = parameters if parameters is not None else []
        self.elements = elements if elements is not None else []
        self._init_ids()

    def _init_ids(self):
        # function declaration/expression name and parameters are identifiers
        # and therefore are subject to name mangling. we need to mark them.
        if self.identifier is not None:
            self.identifier._mangle_candidate = True
        for param in self.parameters:
            param._mangle_candidate = True

    def children(self):
        return [self.identifier] + self.parameters + self.elements

class FuncDecl(FuncBase):
    pass

# The only difference is that function expression might not have an identifier
class FuncExpr(FuncBase):
    pass


class Comma(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def children(self):
        return [self.left, self.right]

class EmptyStatement(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class ExprStatement(Node):
    def __init__(self, expr):
        self.expr = expr

    def children(self):
        return [self.expr]

class Elision(Node):
    def __init__(self, value):
        self.value = value

    def children(self):
        return []

class This(Node):
    def __init__(self):
        pass

    def children(self):
        return []
