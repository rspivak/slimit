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

TOKENS_THAT_IMPLY_DIVISON = frozenset([
    'ID',
    'NUMBER',
    'STRING',
    'REGEX'
    'TRUE',
    'FALSE',
    'NULL',
    ])

TOKEN_VALUES_THAT_IMPLY_DIVISON = frozenset([
    '++',
    '--',
    ')',
    '}',
    ']',
    ])


class Lexer(object):
    """A JavaScript lexer.


    http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-262.pdf
    """

    def __init__(self):
        self.prev_token = None
        self.cur_token = None

    def build(self, **kwargs):
        """Build the lexer."""
        self.lexer = ply.lex.lex(object=self, **kwargs)

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        lexer = self.lexer
        pos = lexer.lexpos
        try:
            char = lexer.lexdata[pos]
            while char.isspace():
                pos += 1
                char = lexer.lexdata[pos]
            next_char = lexer.lexdata[pos + 1]
        except IndexError:
            self.prev_token = self.cur_token
            self.cur_token = lexer.token()
            return self.cur_token

        if char != '/' or (char == '/' and next_char in ('/', '*')):
            self.prev_token = self.cur_token
            self.cur_token = lexer.token()
            return self.cur_token

        # current character is / which is either division or regex
        cur_token = self.cur_token
        is_division_allowed = (
            cur_token is not None and
            (cur_token.type in TOKENS_THAT_IMPLY_DIVISON or
             cur_token.value in TOKEN_VALUES_THAT_IMPLY_DIVISON)
            )
        if is_division_allowed:
            self.prev_token = self.cur_token
            self.cur_token = lexer.token()
            return self.cur_token
        else:
            self.prev_token = self.cur_token
            self.cur_token = self._read_regex()
            return self.cur_token

    def _read_regex(self):
        self.lexer.begin('regex')
        token = self.lexer.token()
        self.lexer.begin('INITIAL')
        return token

    # iterator protocol
    def __iter__(self):
        return self

    def next(self):
        token = self.token()
        if not token:
            raise StopIteration

        return token

    states = (
        ('regex', 'exclusive'),
        )

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
        'NUMBER', 'STRING', 'ID', 'REGEX',

        # Comments
        'LINE_COMMENT', 'BLOCK_COMMENT',

        # Automatically inserted semicolon
        # 'AUTOPLUSPLUS', 'AUTOMINUSMINUS', 'IF_WITHOUT_ELSE',
        ) + keywords

    # taken from jslex
    t_regex_REGEX = r"""(?:
        /                       # opening slash
        # First character is..
        (?: [^*\\/[]            # anything but * \ / or [
        |   \\.                 # or an escape sequence
        |   \[                  # or a class, which has
                (   [^\]\\]     #   anything but \ or ]
                |   \\.         #   or an escape sequence
                )*              #   many times
            \]
        )
        # Following characters are same, except for excluding a star
        (?: [^\\/[]             # anything but \ / or [
        |   \\.                 # or an escape sequence
        |   \[                  # or a class, which has
                (   [^\]\\]     #   anything but \ or ]
                |   \\.         #   or an escape sequence
                )*              #   many times
            \]
        )*                      # many times
        /                       # closing slash
        [a-zA-Z0-9]*            # trailing flags
        )
        """
    t_regex_ignore = ' \t'
    def t_regex_error(self, token):
        raise TypeError(
            "Error parsing regular expression '%s' at %s" % (
                token.value, token.lineno)
            )

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

    t_LINE_COMMENT = r'//.*?$'
    t_BLOCK_COMMENT = r'/\*(.|\n|\r)*?\*/'

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
                [^'\\\n\r]             # no escape chars, line terminators or '
                |
                \\[a-zA-Z\\'"?]        # escaped characters
                |
                \\x[0-9a-fA-F]{2}      # hex_escape_sequence
                |
                \\u[0-9a-fA-F]{4}      # unicode_escape_sequence
            )*?
        ')
    )
    """ # "

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
