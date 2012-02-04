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

import ply.yacc

from slimit import ast
from slimit.lexer import Lexer

try:
    from slimit import lextab, yacctab
except ImportError:
    lextab, yacctab = 'lextab', 'yacctab'


class Parser(object):
    """JavaScript parser(ECMA-262 5th edition grammar).

    The '*noin' variants are needed to avoid confusing the `in` operator in
    a relational expression with the `in` operator in a `for` statement.

    '*nobf' stands for 'no brace or function'
    """

    def __init__(self, lex_optimize=True, lextab=lextab,
                 yacc_optimize=True, yacctab=yacctab, yacc_debug=False):
        self.lex_optimize = lex_optimize
        self.lextab = lextab
        self.yacc_optimize = yacc_optimize
        self.yacctab = yacctab
        self.yacc_debug = yacc_debug

        self.lexer = Lexer()
        self.lexer.build(optimize=lex_optimize, lextab=lextab)
        self.tokens = self.lexer.tokens

        self.parser = ply.yacc.yacc(
            module=self, optimize=yacc_optimize,
            debug=yacc_debug, tabmodule=yacctab, start='program')

    def parse(self, text, debug=False):
        return self.parser.parse(text, lexer=self.lexer, debug=debug)

    def p_empty(self, p):
        """empty :"""
        pass

    def p_auto_semi(self, p):
        """auto_semi : error"""
        pass

    def p_error(self, token):
        if token is None or token.type != 'SEMI':
            next_token = self.lexer.auto_semi(token)
            if next_token is not None:
                self.parser.errok()
                return next_token

        raise SyntaxError(
            'Unexpected token (%s, %r) at %s:%s between %s and %s' % (
                token.type, token.value, token.lineno, token.lexpos,
                self.lexer.prev_token, self.lexer.token())
            )

    # Comment rules
    # def p_single_line_comment(self, p):
    #     """single_line_comment : LINE_COMMENT"""
    #     pass

    # def p_multi_line_comment(self, p):
    #     """multi_line_comment : BLOCK_COMMENT"""
    #     pass

    # Main rules

    def p_program(self, p):
        """program : source_elements"""
        p[0] = ast.Program(p[1])

    def p_source_elements(self, p):
        """source_elements : empty
                           | source_element_list
        """
        p[0] = p[1]

    def p_source_element_list(self, p):
        """source_element_list : source_element
                               | source_element_list source_element
        """
        if len(p) == 2: # single source element
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_source_element(self, p):
        """source_element : statement
                          | function_declaration
        """
        p[0] = p[1]

    def p_statement(self, p):
        """statement : block
                     | variable_statement
                     | empty_statement
                     | expr_statement
                     | if_statement
                     | iteration_statement
                     | continue_statement
                     | break_statement
                     | return_statement
                     | with_statement
                     | switch_statement
                     | labelled_statement
                     | throw_statement
                     | try_statement
                     | debugger_statement
                     | function_declaration
        """
        p[0] = p[1]

    # By having source_elements in the production we support
    # also function_declaration inside blocks
    def p_block(self, p):
        """block : LBRACE source_elements RBRACE"""
        p[0] = ast.Block(p[2])

    def p_literal(self, p):
        """literal : null_literal
                   | boolean_literal
                   | numeric_literal
                   | string_literal
                   | regex_literal
        """
        p[0] = p[1]

    def p_boolean_literal(self, p):
        """boolean_literal : TRUE
                           | FALSE
        """
        p[0] = ast.Boolean(p[1])

    def p_null_literal(self, p):
        """null_literal : NULL"""
        p[0] = ast.Null(p[1])

    def p_numeric_literal(self, p):
        """numeric_literal : NUMBER"""
        p[0] = ast.Number(p[1])

    def p_string_literal(self, p):
        """string_literal : STRING"""
        p[0] = ast.String(p[1])

    def p_regex_literal(self, p):
        """regex_literal : REGEX"""
        p[0] = ast.Regex(p[1])

    def p_identifier(self, p):
        """identifier : ID"""
        p[0] = ast.Identifier(p[1])

    ###########################################
    # Expressions
    ###########################################
    def p_primary_expr(self, p):
        """primary_expr : primary_expr_no_brace
                        | object_literal
        """
        p[0] = p[1]

    def p_primary_expr_no_brace_1(self, p):
        """primary_expr_no_brace : identifier"""
        p[1]._mangle_candidate = True
        p[1]._in_expression = True
        p[0] = p[1]

    def p_primary_expr_no_brace_2(self, p):
        """primary_expr_no_brace : THIS"""
        p[0] = ast.This()

    def p_primary_expr_no_brace_3(self, p):
        """primary_expr_no_brace : literal
                                 | array_literal
        """
        p[0] = p[1]

    def p_primary_expr_no_brace_4(self, p):
        """primary_expr_no_brace : LPAREN expr RPAREN"""
        p[2]._parens = True
        p[0] = p[2]

    def p_array_literal_1(self, p):
        """array_literal : LBRACKET elision_opt RBRACKET"""
        p[0] = ast.Array(items=p[2])

    def p_array_literal_2(self, p):
        """array_literal : LBRACKET element_list RBRACKET
                         | LBRACKET element_list COMMA elision_opt RBRACKET
        """
        items = p[2]
        if len(p) == 6:
            items.extend(p[4])
        p[0] = ast.Array(items=items)


    def p_element_list(self, p):
        """element_list : elision_opt assignment_expr
                        | element_list COMMA elision_opt assignment_expr
        """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[1].extend(p[3])
            p[1].append(p[4])
            p[0] = p[1]

    def p_elision_opt_1(self, p):
        """elision_opt : empty"""
        p[0] = []

    def p_elision_opt_2(self, p):
        """elision_opt : elision"""
        p[0] = p[1]

    def p_elision(self, p):
        """elision : COMMA
                   | elision COMMA
        """
        if len(p) == 2:
            p[0] = [ast.Elision(p[1])]
        else:
            p[1].append(ast.Elision(p[2]))
            p[0] = p[1]

    def p_object_literal(self, p):
        """object_literal : LBRACE RBRACE
                          | LBRACE property_list RBRACE
                          | LBRACE property_list COMMA RBRACE
        """
        if len(p) == 3:
            p[0] = ast.Object()
        else:
            p[0] = ast.Object(properties=p[2])

    def p_property_list(self, p):
        """property_list : property_assignment
                         | property_list COMMA property_assignment
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    # XXX: GET / SET
    def p_property_assignment(self, p):
        """property_assignment : property_name COLON assignment_expr"""
        if len(p) == 4:
            p[0] = ast.Assign(left=p[1], op=p[2], right=p[3])

    def p_property_name(self, p):
        """property_name : identifier
                         | string_literal
                         | numeric_literal
        """
        p[0] = p[1]

    # 11.2 Left-Hand-Side Expressions
    def p_member_expr(self, p):
        """member_expr : primary_expr
                       | function_expr
                       | member_expr LBRACKET expr RBRACKET
                       | member_expr PERIOD identifier
                       | NEW member_expr arguments
        """
        if len(p) == 2:
            p[0] = p[1]
        elif p[1] == 'new':
            p[0] = ast.NewExpr(p[2], p[3])
        elif p[2] == '.':
            p[0] = ast.DotAccessor(p[1], p[3])
        else:
            p[0] = ast.BracketAccessor(p[1], p[3])

    def p_member_expr_nobf(self, p):
        """member_expr_nobf : primary_expr_no_brace
                            | function_expr
                            | member_expr_nobf LBRACKET expr RBRACKET
                            | member_expr_nobf PERIOD identifier
                            | NEW member_expr arguments
        """
        if len(p) == 2:
            p[0] = p[1]
        elif p[1] == 'new':
            p[0] = ast.NewExpr(p[2], p[3])
        elif p[2] == '.':
            p[0] = ast.DotAccessor(p[1], p[3])
        else:
            p[0] = ast.BracketAccessor(p[1], p[3])

    def p_new_expr(self, p):
        """new_expr : member_expr
                    | NEW new_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.NewExpr(p[2])

    def p_new_expr_nobf(self, p):
        """new_expr_nobf : member_expr_nobf
                         | NEW new_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.NewExpr(p[2])

    def p_call_expr(self, p):
        """call_expr : member_expr arguments
                     | call_expr arguments
                     | call_expr LBRACKET expr RBRACKET
                     | call_expr PERIOD identifier
        """
        if len(p) == 3:
            p[0] = ast.FunctionCall(p[1], p[2])
        elif len(p) == 4:
            p[0] = ast.DotAccessor(p[1], p[3])
        else:
            p[0] = ast.BracketAccessor(p[1], p[3])

    def p_call_expr_nobf(self, p):
        """call_expr_nobf : member_expr_nobf arguments
                          | call_expr_nobf arguments
                          | call_expr_nobf LBRACKET expr RBRACKET
                          | call_expr_nobf PERIOD identifier
        """
        if len(p) == 3:
            p[0] = ast.FunctionCall(p[1], p[2])
        elif len(p) == 4:
            p[0] = ast.DotAccessor(p[1], p[3])
        else:
            p[0] = ast.BracketAccessor(p[1], p[3])

    def p_arguments(self, p):
        """arguments : LPAREN RPAREN
                     | LPAREN argument_list RPAREN
        """
        if len(p) == 4:
            p[0] = p[2]

    def p_argument_list(self, p):
        """argument_list : assignment_expr
                         | argument_list COMMA assignment_expr
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_lef_hand_side_expr(self, p):
        """left_hand_side_expr : new_expr
                               | call_expr
        """
        p[0] = p[1]

    def p_lef_hand_side_expr_nobf(self, p):
        """left_hand_side_expr_nobf : new_expr_nobf
                                    | call_expr_nobf
        """
        p[0] = p[1]

    # 11.3 Postfix Expressions
    def p_postfix_expr(self, p):
        """postfix_expr : left_hand_side_expr
                        | left_hand_side_expr PLUSPLUS
                        | left_hand_side_expr MINUSMINUS
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.UnaryOp(op=p[2], value=p[1], postfix=True)

    def p_postfix_expr_nobf(self, p):
        """postfix_expr_nobf : left_hand_side_expr_nobf
                             | left_hand_side_expr_nobf PLUSPLUS
                             | left_hand_side_expr_nobf MINUSMINUS
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.UnaryOp(op=p[2], value=p[1], postfix=True)

    # 11.4 Unary Operators
    def p_unary_expr(self, p):
        """unary_expr : postfix_expr
                      | unary_expr_common
        """
        p[0] = p[1]

    def p_unary_expr_nobf(self, p):
        """unary_expr_nobf : postfix_expr_nobf
                           | unary_expr_common
        """
        p[0] = p[1]

    def p_unary_expr_common(self, p):
        """unary_expr_common : DELETE unary_expr
                             | VOID unary_expr
                             | TYPEOF unary_expr
                             | PLUSPLUS unary_expr
                             | MINUSMINUS unary_expr
                             | PLUS unary_expr
                             | MINUS unary_expr
                             | BNOT unary_expr
                             | NOT unary_expr
        """
        p[0] = ast.UnaryOp(p[1], p[2])

    # 11.5 Multiplicative Operators
    def p_multiplicative_expr(self, p):
        """multiplicative_expr : unary_expr
                               | multiplicative_expr MULT unary_expr
                               | multiplicative_expr DIV unary_expr
                               | multiplicative_expr MOD unary_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_multiplicative_expr_nobf(self, p):
        """multiplicative_expr_nobf : unary_expr_nobf
                                    | multiplicative_expr_nobf MULT unary_expr
                                    | multiplicative_expr_nobf DIV unary_expr
                                    | multiplicative_expr_nobf MOD unary_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    # 11.6 Additive Operators
    def p_additive_expr(self, p):
        """additive_expr : multiplicative_expr
                         | additive_expr PLUS multiplicative_expr
                         | additive_expr MINUS multiplicative_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_additive_expr_nobf(self, p):
        """additive_expr_nobf : multiplicative_expr_nobf
                              | additive_expr_nobf PLUS multiplicative_expr
                              | additive_expr_nobf MINUS multiplicative_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    # 11.7 Bitwise Shift Operators
    def p_shift_expr(self, p):
        """shift_expr : additive_expr
                      | shift_expr LSHIFT additive_expr
                      | shift_expr RSHIFT additive_expr
                      | shift_expr URSHIFT additive_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_shift_expr_nobf(self, p):
        """shift_expr_nobf : additive_expr_nobf
                           | shift_expr_nobf LSHIFT additive_expr
                           | shift_expr_nobf RSHIFT additive_expr
                           | shift_expr_nobf URSHIFT additive_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])


    # 11.8 Relational Operators
    def p_relational_expr(self, p):
        """relational_expr : shift_expr
                           | relational_expr LT shift_expr
                           | relational_expr GT shift_expr
                           | relational_expr LE shift_expr
                           | relational_expr GE shift_expr
                           | relational_expr INSTANCEOF shift_expr
                           | relational_expr IN shift_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_relational_expr_noin(self, p):
        """relational_expr_noin : shift_expr
                                | relational_expr_noin LT shift_expr
                                | relational_expr_noin GT shift_expr
                                | relational_expr_noin LE shift_expr
                                | relational_expr_noin GE shift_expr
                                | relational_expr_noin INSTANCEOF shift_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_relational_expr_nobf(self, p):
        """relational_expr_nobf : shift_expr_nobf
                                | relational_expr_nobf LT shift_expr
                                | relational_expr_nobf GT shift_expr
                                | relational_expr_nobf LE shift_expr
                                | relational_expr_nobf GE shift_expr
                                | relational_expr_nobf INSTANCEOF shift_expr
                                | relational_expr_nobf IN shift_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    # 11.9 Equality Operators
    def p_equality_expr(self, p):
        """equality_expr : relational_expr
                         | equality_expr EQEQ relational_expr
                         | equality_expr NE relational_expr
                         | equality_expr STREQ relational_expr
                         | equality_expr STRNEQ relational_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_equality_expr_noin(self, p):
        """equality_expr_noin : relational_expr_noin
                              | equality_expr_noin EQEQ relational_expr
                              | equality_expr_noin NE relational_expr
                              | equality_expr_noin STREQ relational_expr
                              | equality_expr_noin STRNEQ relational_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_equality_expr_nobf(self, p):
        """equality_expr_nobf : relational_expr_nobf
                              | equality_expr_nobf EQEQ relational_expr
                              | equality_expr_nobf NE relational_expr
                              | equality_expr_nobf STREQ relational_expr
                              | equality_expr_nobf STRNEQ relational_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    # 11.10 Binary Bitwise Operators
    def p_bitwise_and_expr(self, p):
        """bitwise_and_expr : equality_expr
                            | bitwise_and_expr BAND equality_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_and_expr_noin(self, p):
        """bitwise_and_expr_noin \
            : equality_expr_noin
            | bitwise_and_expr_noin BAND equality_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_and_expr_nobf(self, p):
        """bitwise_and_expr_nobf \
            : equality_expr_nobf
            | bitwise_and_expr_nobf BAND equality_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_xor_expr(self, p):
        """bitwise_xor_expr : bitwise_and_expr
                            | bitwise_xor_expr BXOR bitwise_and_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_xor_expr_noin(self, p):
        """
        bitwise_xor_expr_noin \
            : bitwise_and_expr_noin
            | bitwise_xor_expr_noin BXOR bitwise_and_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_xor_expr_nobf(self, p):
        """
        bitwise_xor_expr_nobf \
            : bitwise_and_expr_nobf
            | bitwise_xor_expr_nobf BXOR bitwise_and_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_or_expr(self, p):
        """bitwise_or_expr : bitwise_xor_expr
                           | bitwise_or_expr BOR bitwise_xor_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_or_expr_noin(self, p):
        """
        bitwise_or_expr_noin \
            : bitwise_xor_expr_noin
            | bitwise_or_expr_noin BOR bitwise_xor_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_bitwise_or_expr_nobf(self, p):
        """
        bitwise_or_expr_nobf \
            : bitwise_xor_expr_nobf
            | bitwise_or_expr_nobf BOR bitwise_xor_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    # 11.11 Binary Logical Operators
    def p_logical_and_expr(self, p):
        """logical_and_expr : bitwise_or_expr
                            | logical_and_expr AND bitwise_or_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_and_expr_noin(self, p):
        """
        logical_and_expr_noin : bitwise_or_expr_noin
                              | logical_and_expr_noin AND bitwise_or_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_and_expr_nobf(self, p):
        """
        logical_and_expr_nobf : bitwise_or_expr_nobf
                              | logical_and_expr_nobf AND bitwise_or_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_or_expr(self, p):
        """logical_or_expr : logical_and_expr
                           | logical_or_expr OR logical_and_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_or_expr_noin(self, p):
        """logical_or_expr_noin : logical_and_expr_noin
                                | logical_or_expr_noin OR logical_and_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    def p_logical_or_expr_nobf(self, p):
        """logical_or_expr_nobf : logical_and_expr_nobf
                                | logical_or_expr_nobf OR logical_and_expr_nobf
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.BinOp(op=p[2], left=p[1], right=p[3])

    # 11.12 Conditional Operator ( ? : )
    def p_conditional_expr(self, p):
        """
        conditional_expr \
            : logical_or_expr
            | logical_or_expr CONDOP assignment_expr COLON assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Conditional(
                predicate=p[1], consequent=p[3], alternative=p[5])

    def p_conditional_expr_noin(self, p):
        """
        conditional_expr_noin \
            : logical_or_expr_noin
            | logical_or_expr_noin CONDOP assignment_expr_noin COLON \
                  assignment_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Conditional(
                predicate=p[1], consequent=p[3], alternative=p[5])

    def p_conditional_expr_nobf(self, p):
        """
        conditional_expr_nobf \
            : logical_or_expr_nobf
            | logical_or_expr_nobf CONDOP assignment_expr COLON assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Conditional(
                predicate=p[1], consequent=p[3], alternative=p[5])

    # 11.13 Assignment Operators
    def p_assignment_expr(self, p):
        """
        assignment_expr \
            : conditional_expr
            | left_hand_side_expr assignment_operator assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assign(left=p[1], op=p[2], right=p[3])

    def p_assignment_expr_noin(self, p):
        """
        assignment_expr_noin \
            : conditional_expr_noin
            | left_hand_side_expr assignment_operator assignment_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assign(left=p[1], op=p[2], right=p[3])

    def p_assignment_expr_nobf(self, p):
        """
        assignment_expr_nobf \
            : conditional_expr_nobf
            | left_hand_side_expr_nobf assignment_operator assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Assign(left=p[1], op=p[2], right=p[3])

    def p_assignment_operator(self, p):
        """assignment_operator : EQ
                               | MULTEQUAL
                               | DIVEQUAL
                               | MODEQUAL
                               | PLUSEQUAL
                               | MINUSEQUAL
                               | LSHIFTEQUAL
                               | RSHIFTEQUAL
                               | URSHIFTEQUAL
                               | ANDEQUAL
                               | XOREQUAL
                               | OREQUAL
        """
        p[0] = p[1]

    # 11.4 Comma Operator
    def p_expr(self, p):
        """expr : assignment_expr
                | expr COMMA assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Comma(left=p[1], right=p[3])

    def p_expr_noin(self, p):
        """expr_noin : assignment_expr_noin
                     | expr_noin COMMA assignment_expr_noin
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Comma(left=p[1], right=p[3])

    def p_expr_nobf(self, p):
        """expr_nobf : assignment_expr_nobf
                     | expr_nobf COMMA assignment_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ast.Comma(left=p[1], right=p[3])

    # 12.2 Variable Statement
    def p_variable_statement(self, p):
        """variable_statement : VAR variable_declaration_list SEMI
                              | VAR variable_declaration_list auto_semi
        """
        p[0] = ast.VarStatement(p[2])

    def p_variable_declaration_list(self, p):
        """
        variable_declaration_list \
            : variable_declaration
            | variable_declaration_list COMMA variable_declaration
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_variable_declaration_list_noin(self, p):
        """
        variable_declaration_list_noin \
            : variable_declaration_noin
            | variable_declaration_list_noin COMMA variable_declaration_noin
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_variable_declaration(self, p):
        """variable_declaration : identifier
                                | identifier initializer
        """
        if len(p) == 2:
            p[0] = ast.VarDecl(p[1])
        else:
            p[0] = ast.VarDecl(p[1], p[2])

    def p_variable_declaration_noin(self, p):
        """variable_declaration_noin : identifier
                                     | identifier initializer_noin
        """
        if len(p) == 2:
            p[0] = ast.VarDecl(p[1])
        else:
            p[0] = ast.VarDecl(p[1], p[2])

    def p_initializer(self, p):
        """initializer : EQ assignment_expr"""
        p[0] = p[2]

    def p_initializer_noin(self, p):
        """initializer_noin : EQ assignment_expr_noin"""
        p[0] = p[2]

    # 12.3 Empty Statement
    def p_empty_statement(self, p):
        """empty_statement : SEMI"""
        p[0] = ast.EmptyStatement(p[1])

    # 12.4 Expression Statement
    def p_expr_statement(self, p):
        """expr_statement : expr_nobf SEMI
                          | expr_nobf auto_semi
        """
        p[0] = ast.ExprStatement(p[1])

    # 12.5 The if Statement
    def p_if_statement_1(self, p):
        """if_statement : IF LPAREN expr RPAREN statement"""
        p[0] = ast.If(predicate=p[3], consequent=p[5])

    def p_if_statement_2(self, p):
        """if_statement : IF LPAREN expr RPAREN statement ELSE statement"""
        p[0] = ast.If(predicate=p[3], consequent=p[5], alternative=p[7])

    # 12.6 Iteration Statements
    def p_iteration_statement_1(self, p):
        """
        iteration_statement \
            : DO statement WHILE LPAREN expr RPAREN SEMI
            | DO statement WHILE LPAREN expr RPAREN auto_semi
        """
        p[0] = ast.DoWhile(predicate=p[5], statement=p[2])

    def p_iteration_statement_2(self, p):
        """iteration_statement : WHILE LPAREN expr RPAREN statement"""
        p[0] = ast.While(predicate=p[3], statement=p[5])

    def p_iteration_statement_3(self, p):
        """
        iteration_statement \
            : FOR LPAREN expr_noin_opt SEMI expr_opt SEMI expr_opt RPAREN \
                  statement
            | FOR LPAREN VAR variable_declaration_list_noin SEMI expr_opt SEMI\
                  expr_opt RPAREN statement
        """
        if len(p) == 10:
            p[0] = ast.For(init=p[3], cond=p[5], count=p[7], statement=p[9])
        else:
            init = ast.VarStatement(p[4])
            p[0] = ast.For(init=init, cond=p[6], count=p[8], statement=p[10])

    def p_iteration_statement_4(self, p):
        """
        iteration_statement \
            : FOR LPAREN left_hand_side_expr IN expr RPAREN statement
        """
        p[0] = ast.ForIn(item=p[3], iterable=p[5], statement=p[7])

    def p_iteration_statement_5(self, p):
        """
        iteration_statement : \
            FOR LPAREN VAR identifier IN expr RPAREN statement
        """
        p[0] = ast.ForIn(item=ast.VarDecl(p[4]), iterable=p[6], statement=p[8])

    def p_iteration_statement_6(self, p):
        """
        iteration_statement \
          : FOR LPAREN VAR identifier initializer_noin IN expr RPAREN statement
        """
        p[0] = ast.ForIn(item=ast.VarDecl(identifier=p[4], initializer=p[5]),
                         iterable=p[7], statement=p[9])

    def p_expr_opt(self, p):
        """expr_opt : empty
                    | expr
        """
        p[0] = p[1]

    def p_expr_noin_opt(self, p):
        """expr_noin_opt : empty
                         | expr_noin
        """
        p[0] = p[1]

    # 12.7 The continue Statement
    def p_continue_statement_1(self, p):
        """continue_statement : CONTINUE SEMI
                              | CONTINUE auto_semi
        """
        p[0] = ast.Continue()

    def p_continue_statement_2(self, p):
        """continue_statement : CONTINUE identifier SEMI
                              | CONTINUE identifier auto_semi
        """
        p[0] = ast.Continue(p[2])

    # 12.8 The break Statement
    def p_break_statement_1(self, p):
        """break_statement : BREAK SEMI
                           | BREAK auto_semi
        """
        p[0] = ast.Break()

    def p_break_statement_2(self, p):
        """break_statement : BREAK identifier SEMI
                           | BREAK identifier auto_semi
        """
        p[0] = ast.Break(p[2])


    # 12.9 The return Statement
    def p_return_statement_1(self, p):
        """return_statement : RETURN SEMI
                            | RETURN auto_semi
        """
        p[0] = ast.Return()

    def p_return_statement_2(self, p):
        """return_statement : RETURN expr SEMI
                            | RETURN expr auto_semi
        """
        p[0] = ast.Return(expr=p[2])

    # 12.10 The with Statement
    def p_with_statement(self, p):
        """with_statement : WITH LPAREN expr RPAREN statement"""
        p[0] = ast.With(expr=p[3], statement=p[5])

    # 12.11 The switch Statement
    def p_switch_statement(self, p):
        """switch_statement : SWITCH LPAREN expr RPAREN case_block"""
        cases = []
        default = None
        # iterate over return values from case_block
        for item in p[5]:
            if isinstance(item, ast.Default):
                default = item
            elif isinstance(item, list):
                cases.extend(item)

        p[0] = ast.Switch(expr=p[3], cases=cases, default=default)

    def p_case_block(self, p):
        """
        case_block \
            : LBRACE case_clauses_opt RBRACE
            | LBRACE case_clauses_opt default_clause case_clauses_opt RBRACE
        """
        p[0] = p[2:-1]

    def p_case_clauses_opt(self, p):
        """case_clauses_opt : empty
                            | case_clauses
        """
        p[0] = p[1]

    def p_case_clauses(self, p):
        """case_clauses : case_clause
                        | case_clauses case_clause
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    def p_case_clause(self, p):
        """case_clause : CASE expr COLON source_elements"""
        p[0] = ast.Case(expr=p[2], elements=p[4])

    def p_default_clause(self, p):
        """default_clause : DEFAULT COLON source_elements"""
        p[0] = ast.Default(elements=p[3])

    # 12.12 Labelled Statements
    def p_labelled_statement(self, p):
        """labelled_statement : identifier COLON statement"""
        p[0] = ast.Label(identifier=p[1], statement=p[3])

    # 12.13 The throw Statement
    def p_throw_statement(self, p):
        """throw_statement : THROW expr SEMI
                           | THROW expr auto_semi
        """
        p[0] = ast.Throw(expr=p[2])

    # 12.14 The try Statement
    def p_try_statement_1(self, p):
        """try_statement : TRY block catch"""
        p[0] = ast.Try(statements=p[2], catch=p[3])

    def p_try_statement_2(self, p):
        """try_statement : TRY block finally"""
        p[0] = ast.Try(statements=p[2], fin=p[3])

    def p_try_statement_3(self, p):
        """try_statement : TRY block catch finally"""
        p[0] = ast.Try(statements=p[2], catch=p[3], fin=p[4])

    def p_catch(self, p):
        """catch : CATCH LPAREN identifier RPAREN block"""
        p[0] = ast.Catch(identifier=p[3], elements=p[5])

    def p_finally(self, p):
        """finally : FINALLY block"""
        p[0] = ast.Finally(elements=p[2])

    # 12.15 The debugger statement
    def p_debugger_statement(self, p):
        """debugger_statement : DEBUGGER SEMI
                              | DEBUGGER auto_semi
        """
        p[0] = ast.Debugger(p[1])

    # 13 Function Definition
    def p_function_declaration(self, p):
        """
        function_declaration \
            : FUNCTION identifier LPAREN RPAREN LBRACE function_body RBRACE
            | FUNCTION identifier LPAREN formal_parameter_list RPAREN LBRACE \
                 function_body RBRACE
        """
        if len(p) == 8:
            p[0] = ast.FuncDecl(
                identifier=p[2], parameters=None, elements=p[6])
        else:
            p[0] = ast.FuncDecl(
                identifier=p[2], parameters=p[4], elements=p[7])

    def p_function_expr_1(self, p):
        """
        function_expr \
            : FUNCTION LPAREN RPAREN LBRACE function_body RBRACE
            | FUNCTION LPAREN formal_parameter_list RPAREN \
                LBRACE function_body RBRACE
        """
        if len(p) == 7:
            p[0] = ast.FuncExpr(
                identifier=None, parameters=None, elements=p[5])
        else:
            p[0] = ast.FuncExpr(
                identifier=None, parameters=p[3], elements=p[6])

    def p_function_expr_2(self, p):
        """
        function_expr \
            : FUNCTION identifier LPAREN RPAREN LBRACE function_body RBRACE
            | FUNCTION identifier LPAREN formal_parameter_list RPAREN \
                LBRACE function_body RBRACE
        """
        if len(p) == 8:
            p[0] = ast.FuncExpr(
                identifier=p[2], parameters=None, elements=p[6])
        else:
            p[0] = ast.FuncExpr(
                identifier=p[2], parameters=p[4], elements=p[7])


    def p_formal_parameter_list(self, p):
        """formal_parameter_list : identifier
                                 | formal_parameter_list COMMA identifier
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    def p_function_body(self, p):
        """function_body : source_elements"""
        p[0] = p[1]
