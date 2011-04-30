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

import ply.lex

from slimit.unicode import (
    LETTER,
    DIGIT,
    COMBINING_MARK,
    CONNECTOR_PUNCTUATION,
    )


class Lexer(object):

    def build(self, **kwargs):
        """Build the lexer."""
        self.lexer = ply.lex.lex(object=self, **kwargs)

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        return self.lexer.token()

    # Iterator protocol
    def __iter__(self):
        return self

    def next(self):
        token = self.token()
        if not token:
            raise StopIteration

        return token

    keywords = (
        'BREAK', 'CASE', 'CATCH', 'CONTINUE', 'DEBUGGER', 'DEFAULT', 'DELETE',
        'DO', 'ELSE', 'FINALLY', 'FOR', 'FUNCTION', 'IF', 'IN',
        'INSTANCEOF', 'NEW', 'RETURN', 'SWITCH', 'THIS', 'THROW', 'TRY',
        'TYPEOF', 'VAR', 'VOID', 'WHILE', 'WITH',
        # future reserved words
        'CLASS', 'CONST', 'ENUM', 'EXPORT', 'EXTENDS', 'IMPORT', 'SUPER',
        )
    keywords_dict = dict((key.lower(), key) for key in keywords)

    tokens = (
        # Literals
        'NULL', 'TRUE', 'FALSE',

        # Punctuators
        'EQEQ', 'NE',                     # == and !=
        'STREQ', 'STRNEQ',                # === and !==
        'LT', 'GT',                       # < and >
        'LE', 'GE',                       # <= and >=
        'OR', 'AND',                      # || and &&
        'PLUSPLUS', 'MINUSMINUS',         # ++ and --
        'LSHIFT',                         # <<
        'RSHIFT', 'URSHIFT',              # >> and >>>
        'PLUSEQUAL', 'MINUSEQUAL',        # += and -=
        'MULTEQUAL', 'DIVEQUAL',          # *= and /=
        'LSHIFTEQUAL',                    # <<=
        'RSHIFTEQUAL', 'URSHIFTEQUAL',    # >>= and >>>=
        'ANDEQUAL', 'MODEQUAL',           # &= and %=
        'XOREQUAL', 'OREQUAL',            # ^= and |=

        # Terminal types
        'NUMBER', 'STRING', 'ID', 'REGEXP',

        # Automatically inserted semicolon
        # 'AUTOPLUSPLUS', 'AUTOMINUSMINUS', 'IF_WITHOUT_ELSE',
        ) + keywords

    # Punctuators
    literals = (
        ',', '.', ';', ':',
        '&', '|', '^', '~',
        '+', '-', '*', '/', '%',
        '[', ']', '{', '}', '(', ')',
        '?', '!', '=',
        )

    # Punctuators
    t_EQEQ = '=='
    t_NE = '!='
    t_STREQ = '==='
    t_STRNEQ = '!=='
    t_LT = '<'
    t_GT = '>'
    t_LE = '<='
    t_GE = '>='
    t_OR = '\|\|'
    t_AND = '&&'
    t_PLUSPLUS = '\+\+'
    t_MINUSMINUS = '--'
    t_LSHIFT = '<<'
    t_RSHIFT = '>>'
    t_URSHIFT = '>>>'
    t_PLUSEQUAL = '\+='
    t_MINUSEQUAL = '-='
    t_MULTEQUAL = '\*='
    t_DIVEQUAL = '/='
    t_LSHIFTEQUAL = '<<='
    t_RSHIFTEQUAL = '>>='
    t_URSHIFTEQUAL = '>>>='
    t_ANDEQUAL = '&='
    t_MODEQUAL = '%='
    t_XOREQUAL = '\^='
    t_OREQUAL = '\|='

    t_ignore = ' \t'

    t_NUMBER = r"""
    (?:
        0[xX][0-9a-fA-F]+       # hex_integer_literal
        |
        0[0-7]+                 # octal_integer_literal (See section B.1.1)
        |
        # decimal_literal
        (?:0|[1-9][0-9]*)       # decimal_integer_literal
        \.                      # dot
        [0-9]*                  # decimal_digits_opt
        (?:[eE][+-]?[0-9]+)?    # exponent_part_opt
        |
        \.                      #
        [0-9]+                  # decimal_digits
        (?:[eE][+-]?[0-9]+)?    # exponent_part_opt
        |
        (?:0|[1-9][0-9]*)       # decimal_integer_literal
        (?:[eE][+-]?[0-9]+)?    # exponent_part_opt
    )
    """

    t_STRING = r"""
    (?:
        (?:" # double quoted string
            (?:
                [^"\\\n\r]             # no escape chars, line terminators or "
                |
                \\[a-zA-Z\\\'"?]       # escaped characters
                |
                \\x[0-9a-fA-F]{2}      # hex_escape_sequence
                |
                \\u[0-9a-fA-F]{4}      # unicode_escape_sequence
            )*?
        ")
        |
        (?:' # single quoted string
            (?:
                [^"\\\n\r]             # no escape chars, line terminators or "
                |
                \\[a-zA-Z\\'"?]        # escaped characters
                |
                \\x[0-9a-fA-F]{2}      # hex_escape_sequence
                |
                \\u[0-9a-fA-F]{4}      # unicode_escape_sequence
            )*?
        ')
    )
    """

    # Literals
    def t_NULL(self, token):
        r'null'
        return token

    def t_TRUE(self, token):
        r'true'
        return token

    def t_FALSE(self, token):
        r'false'
        return token

    # XXX: <ZWNJ> <ZWJ> ?
    identifier_start = r'(?:' + r'[a-zA-Z_$]' + r'|' + LETTER + r')+'
    identifier_part = (
        r'(?:' + COMBINING_MARK + r'|' + DIGIT +
        r'|' + CONNECTOR_PUNCTUATION + r')*'
        )
    identifier = identifier_start + identifier_part

    @ply.lex.TOKEN(identifier)
    def t_ID(self, token):
        token.type = self.keywords_dict.get(token.value, 'ID')
        return token

    def t_error(self, token):
        print "Illegal character '%s'" % token.value[0]
        token.lexer.skip(1)
