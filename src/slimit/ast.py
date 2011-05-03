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

    def __init__(self, token=None, children=None):
        self.token = token
        self.children = [] if children is None else children

    def children(self):
        pass

    def is_null(self):
        return self.token is None

    def to_string_tree(self):
        if not self.children:
            return str(self)

        result = []
        if not self.is_null():
            result.append('(')
            result.append(str(self))
            result.append(' ')

        for index, child in enumerate(self.children):
            if index > 0:
                result.append(' ')
            result.append(child.to_string_tree())

        if not self.is_null():
            result.append(')')

        return ''.join(result)

    def __str__(self):
        return str(self.token)


class BlockNode(Node):
    pass

