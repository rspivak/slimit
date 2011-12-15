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


class ASTVisitor(object):
    """Base class for custom AST node visitors.

    Example:

    >>> from slimit.parser import Parser
    >>> from slimit.visitors.nodevisitor import ASTVisitor
    >>>
    >>> text = '''
    ... var x = {
    ...     "key1": "value1",
    ...     "key2": "value2"
    ... };
    ... '''
    >>>
    >>> class MyVisitor(ASTVisitor):
    ...     def visit_Object(self, node):
    ...         '''Visit object literal.'''
    ...         for prop in node:
    ...             left, right = prop.left, prop.right
    ...             print 'Property value: %s' % right.value
    ...             # visit all children in turn
    ...             self.visit(prop)
    ...
    >>>
    >>> parser = Parser()
    >>> tree = parser.parse(text)
    >>> visitor = MyVisitor()
    >>> visitor.visit(tree)
    Property value: "value1"
    Property value: "value2"

    """

    def visit(self, node):
        method = 'visit_%s' % node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        for child in node:
            self.visit(child)


class NodeVisitor(object):
    """Simple node visitor."""

    def visit(self, node):
        """Returns a generator that walks all children recursively."""
        for child in node:
            yield child
            for subchild in self.visit(child):
                yield subchild


def visit(node):
    visitor = NodeVisitor()
    for child in visitor.visit(node):
        yield child
