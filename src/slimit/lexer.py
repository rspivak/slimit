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

from slimit.unicode_chars import (
    LETTER,
    DIGIT,
    COMBINING_MARK,
    CONNECTOR_PUNCTUATION,
    )

# See "Regular Expression Literals" at
# http://www.mozilla.org/js/language/js20-2002-04/rationale/syntax.html
TOKENS_THAT_IMPLY_DIVISON = frozenset([
    'ID',
    'NUMBER',
    'STRING',
    'REGEX',
    'TRUE',
    'FALSE',
    'NULL',
    'THIS',
    'PLUSPLUS',
    'MINUSMINUS',
    'RPAREN',
    'RBRACE',
    'RBRACKET',
    ])


class Lexer(object):
    """A JavaScript lexer.

    >>> from slimit.lexer import Lexer
    >>> lexer = Lexer()

    Lexer supports iteration:

    >>> lexer.input('a = 1;')
    >>> for token in lexer:
    ...     print token
    ...
    LexToken(ID,'a',1,0)
    LexToken(EQ,'=',1,2)
    LexToken(NUMBER,'1',1,4)
    LexToken(SEMI,';',1,5)

    Or call one token at a time with 'token' method:

    >>> lexer.input('a = 1;')
    >>> while True:
    ...     token = lexer.token()
    ...     if not token:
    ...         break
    ...     print token
    ...
    LexToken(ID,'a',1,0)
    LexToken(EQ,'=',1,2)
    LexToken(NUMBER,'1',1,4)
    LexToken(SEMI,';',1,5)

    >>> lexer.input('a = 1;')
    >>> token = lexer.token()
    >>> token.type, token.value, token.lineno, token.lexpos
    ('ID', 'a', 1, 0)

    For more information see:
    http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-262.pdf
    """
    def __init__(self):
        self.prev_token = None
        self.cur_token = None
        self.next_tokens = []
        self.build()

    def build(self, **kwargs):
        """Build the lexer."""
        self.lexer = ply.lex.lex(object=self, **kwargs)

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        if self.next_tokens:
            return self.next_tokens.pop()

        lexer = self.lexer
        while True:
            pos = lexer.lexpos
            try:
                char = lexer.lexdata[pos]
                while char in ' \t':
                    pos += 1
                    char = lexer.lexdata[pos]
                next_char = lexer.lexdata[pos + 1]
            except IndexError:
                tok = self._get_update_token()
                if tok is not None and tok.type == 'LINE_TERMINATOR':
                    continue
                else:
                    return tok

            if char != '/' or (char == '/' and next_char in ('/', '*')):
                tok = self._get_update_token()
                if tok.type in ('LINE_TERMINATOR',
                                'LINE_COMMENT', 'BLOCK_COMMENT'):
                    continue
                else:
                    return tok

            # current character is '/' which is either division or regex
            cur_token = self.cur_token
            is_division_allowed = (
                cur_token is not None and
                cur_token.type in TOKENS_THAT_IMPLY_DIVISON
                )
            if is_division_allowed:
                return self._get_update_token()
            else:
                self.prev_token = self.cur_token
                self.cur_token = self._read_regex()
                return self.cur_token

    def auto_semi(self, token):
        if (token is None or token.type == 'RBRACE'
            or self._is_prev_token_lt()
            ):
            if token:
                self.next_tokens.append(token)
            return self._create_semi_token(token)

    def _is_prev_token_lt(self):
        return self.prev_token and self.prev_token.type == 'LINE_TERMINATOR'

    def _read_regex(self):
        self.lexer.begin('regex')
        token = self.lexer.token()
        self.lexer.begin('INITIAL')
        return token

    def _get_update_token(self):
        self.prev_token = self.cur_token
        self.cur_token = self.lexer.token()
        # insert semicolon before restricted tokens
        # See section 7.9.1 ECMA262
        if (self.cur_token is not None
            and self.cur_token.type == 'LINE_TERMINATOR'
            and self.prev_token is not None
            and self.prev_token.type in ['BREAK', 'CONTINUE',
                                         'RETURN', 'THROW']
            ):
            return self._create_semi_token(self.cur_token)
        return self.cur_token

    def _create_semi_token(self, orig_token):
        token = ply.lex.LexToken()
        token.type = 'SEMI'
        token.value = ';'
        if orig_token is not None:
            token.lineno = orig_token.lineno
            token.lexpos = orig_token.lexpos
        else:
            token.lineno = 0
            token.lexpos = 0
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
        'TYPEOF', 'VAR', 'VOID', 'WHILE', 'WITH', 'NULL', 'TRUE', 'FALSE',
        # future reserved words - well, it's uncommented now to make
        # IE8 happy because it chokes up on minification:
        # obj["class"] -> obj.class
        'CLASS', 'CONST', 'ENUM', 'EXPORT', 'EXTENDS', 'IMPORT', 'SUPER',
        )
    keywords_dict = dict((key.lower(), key) for key in keywords)

    tokens = (
        # Punctuators
        'PERIOD', 'COMMA', 'SEMI', 'COLON',     # . , ; :
        'PLUS', 'MINUS', 'MULT', 'DIV', 'MOD',  # + - * / %
        'BAND', 'BOR', 'BXOR', 'BNOT',          # & | ^ ~
        'CONDOP',                               # conditional operator ?
        'NOT',                                  # !
        'LPAREN', 'RPAREN',                     # ( and )
        'LBRACE', 'RBRACE',                     # { and }
        'LBRACKET', 'RBRACKET',                 # [ and ]
        'EQ', 'EQEQ', 'NE',                     # = == !=
        'STREQ', 'STRNEQ',                      # === and !==
        'LT', 'GT',                             # < and >
        'LE', 'GE',                             # <= and >=
        'OR', 'AND',                            # || and &&
        'PLUSPLUS', 'MINUSMINUS',               # ++ and --
        'LSHIFT',                               # <<
        'RSHIFT', 'URSHIFT',                    # >> and >>>
        'PLUSEQUAL', 'MINUSEQUAL',              # += and -=
        'MULTEQUAL', 'DIVEQUAL',                # *= and /=
        'LSHIFTEQUAL',                          # <<=
        'RSHIFTEQUAL', 'URSHIFTEQUAL',          # >>= and >>>=
        'ANDEQUAL', 'MODEQUAL',                 # &= and %=
        'XOREQUAL', 'OREQUAL',                  # ^= and |=

        # Terminal types
        'NUMBER', 'STRING', 'ID', 'REGEX',

        # Properties
        'GETPROP', 'SETPROP',

        # Comments
        'LINE_COMMENT', 'BLOCK_COMMENT',

        'LINE_TERMINATOR',
        ) + keywords

    # adapted from https://bitbucket.org/ned/jslex
    t_regex_REGEX = r"""(?:
        /                       # opening slash
        # First character is..
        (?: [^*\\/[]            # anything but * \ / or [
        |   \\.                 # or an escape sequence
        |   \[                  # or a class, which has
                (?: [^\]\\]     # anything but \ or ]
                |   \\.         # or an escape sequence
                )*              # many times
            \]
        )
        # Following characters are same, except for excluding a star
        (?: [^\\/[]             # anything but \ / or [
        |   \\.                 # or an escape sequence
        |   \[                  # or a class, which has
                (?: [^\]\\]     # anything but \ or ]
                |   \\.         # or an escape sequence
                )*              # many times
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
    t_PERIOD        = r'\.'
    t_COMMA         = r','
    t_SEMI          = r';'
    t_COLON         = r':'
    t_PLUS          = r'\+'
    t_MINUS         = r'-'
    t_MULT          = r'\*'
    t_DIV           = r'/'
    t_MOD           = r'%'
    t_BAND          = r'&'
    t_BOR           = r'\|'
    t_BXOR          = r'\^'
    t_BNOT          = r'~'
    t_CONDOP        = r'\?'
    t_NOT           = r'!'
    t_LPAREN        = r'\('
    t_RPAREN        = r'\)'
    t_LBRACE        = r'{'
    t_RBRACE        = r'}'
    t_LBRACKET      = r'\['
    t_RBRACKET      = r'\]'
    t_EQ            = r'='
    t_EQEQ          = r'=='
    t_NE            = r'!='
    t_STREQ         = r'==='
    t_STRNEQ        = r'!=='
    t_LT            = r'<'
    t_GT            = r'>'
    t_LE            = r'<='
    t_GE            = r'>='
    t_OR            = r'\|\|'
    t_AND           = r'&&'
    t_PLUSPLUS      = r'\+\+'
    t_MINUSMINUS    = r'--'
    t_LSHIFT        = r'<<'
    t_RSHIFT        = r'>>'
    t_URSHIFT       = r'>>>'
    t_PLUSEQUAL     = r'\+='
    t_MINUSEQUAL    = r'-='
    t_MULTEQUAL     = r'\*='
    t_DIVEQUAL      = r'/='
    t_LSHIFTEQUAL   = r'<<='
    t_RSHIFTEQUAL   = r'>>='
    t_URSHIFTEQUAL  = r'>>>='
    t_ANDEQUAL      = r'&='
    t_MODEQUAL      = r'%='
    t_XOREQUAL      = r'\^='
    t_OREQUAL       = r'\|='

    t_LINE_COMMENT  = r'//[^\r\n]*'
    t_BLOCK_COMMENT = r'/\*[^*]*\*+([^/*][^*]*\*+)*/'

    t_LINE_TERMINATOR = r'[\n\r]+'

    t_ignore = ' \t'

    t_NUMBER = r"""
    (?:
        0[xX][0-9a-fA-F]+              # hex_integer_literal
     |  0[0-7]+                        # or octal_integer_literal (spec B.1.1)
     |  (?:                            # or decimal_literal
            (?:0|[1-9][0-9]*)          # decimal_integer_literal
            \.                         # dot
            [0-9]*                     # decimal_digits_opt
            (?:[eE][+-]?[0-9]+)?       # exponent_part_opt
         |
            \.                         # dot
            [0-9]+                     # decimal_digits
            (?:[eE][+-]?[0-9]+)?       # exponent_part_opt
         |
            (?:0|[1-9][0-9]*)          # decimal_integer_literal
            (?:[eE][+-]?[0-9]+)?       # exponent_part_opt
         )
    )
    """

    string = r"""
    (?:
        # double quoted string
        (?:"                               # opening double quote
            (?: [^"\\\n\r]                 # no \, line terminators or "
                | \\[a-zA-Z!-\/:-@\[-`{-~] # or escaped characters
                | \\x[0-9a-fA-F]{2}        # or hex_escape_sequence
                | \\u[0-9a-fA-F]{4}        # or unicode_escape_sequence
            )*?                            # zero or many times
            (?: \\\n                       # multiline ?
              (?:
                [^"\\\n\r]                 # no \, line terminators or "
                | \\[a-zA-Z!-\/:-@\[-`{-~] # or escaped characters
                | \\x[0-9a-fA-F]{2}        # or hex_escape_sequence
                | \\u[0-9a-fA-F]{4}        # or unicode_escape_sequence
              )*?                          # zero or many times
            )*
        ")                                 # closing double quote
        |
        # single quoted string
        (?:'                               # opening single quote
            (?: [^'\\\n\r]                 # no \, line terminators or '
                | \\[a-zA-Z!-\/:-@\[-`{-~] # or escaped characters
                | \\x[0-9a-fA-F]{2}        # or hex_escape_sequence
                | \\u[0-9a-fA-F]{4}        # or unicode_escape_sequence
            )*?                            # zero or many times
            (?: \\\n                       # multiline ?
              (?:
                [^'\\\n\r]                 # no \, line terminators or '
                | \\[a-zA-Z!-\/:-@\[-`{-~] # or escaped characters
                | \\x[0-9a-fA-F]{2}        # or hex_escape_sequence
                | \\u[0-9a-fA-F]{4}        # or unicode_escape_sequence
              )*?                          # zero or many times
            )*
        ')                                 # closing single quote
    )
    """  # "

    @ply.lex.TOKEN(string)
    def t_STRING(self, token):
        # remove escape + new line sequence used for strings
        # written across multiple lines of code
        token.value = token.value.replace('\\\n', '')
        return token

    # XXX: <ZWNJ> <ZWJ> ?
    identifier_start = r'(?:' + r'[a-zA-Z_$]' + r'|' + LETTER + r')+'
    identifier_part = (
        r'(?:' + COMBINING_MARK + r'|' + r'[0-9a-zA-Z_$]' + r'|' + DIGIT +
        r'|' + CONNECTOR_PUNCTUATION + r')*'
        )
    identifier = identifier_start + identifier_part

    getprop = r'get' + r'(?=\s' + identifier + r')'
    @ply.lex.TOKEN(getprop)
    def t_GETPROP(self, token):
        return token

    setprop = r'set' + r'(?=\s' + identifier + r')'
    @ply.lex.TOKEN(setprop)
    def t_SETPROP(self, token):
        return token

    @ply.lex.TOKEN(identifier)
    def t_ID(self, token):
        token.type = self.keywords_dict.get(token.value, 'ID')
        return token

    def t_error(self, token):
        print 'Illegal character %r at %s:%s after %s' % (
            token.value[0], token.lineno, token.lexpos, self.prev_token)
        token.lexer.skip(1)
