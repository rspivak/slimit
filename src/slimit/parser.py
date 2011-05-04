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


class Parser(object):
    """JavaScript parser(ECMA-262 5th edition grammar).

    The '*noin' variants are needed to avoid confusing the `in` operator in
    a relational expression with the `in` operator in a `for` statement.

    '*nobf' stands for 'no brace or function'
    """

    def __init__(self, lex_optimize=True, lextab='lextab',
                 yacc_optimize=True, yacctab='yacctab', yacc_debug=False):
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

    precedence = (
        ('nonassoc', 'IF_WITHOUT_ELSE'),
        ('nonassoc', 'ELSE'),
        )

    def p_program(self, p):
        """program : source_elements"""
        p[0] = p[1]

    def p_source_elements(self, p):
        """source_elements : empty
                           | source_element_list
        """
        pass

    def p_source_element_list(self, p):
        """source_element_list : source_element
                               | source_element_list source_element
        """
        pass

    def p_source_element(self, p):
        """source_element : statement
                          | function_declaration
        """
        pass

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
        """
        pass


    def p_statement_list(self, p):
        """statement_list : statement
                          | statement_list statement
        """
        pass

    def p_literal(self, p):
        """literal : null_literal
                   | boolean_literal
                   | numeric_literal
                   | string_literal
        """
        pass

    def p_boolean_literal(self, p):
        """boolean_literal : TRUE
                           | FALSE
        """
        pass

    def p_null_literal(self, p):
        """null_literal : NULL"""
        pass

    def p_numeric_literal(self, p):
        """numeric_literal : NUMBER"""
        pass

    def p_string_literal(self, p):
        """string_literal : STRING"""
        pass

    def p_property(self, p):
        """property : ID ':' assignment_expr
                    | STRING ':' assignment_expr
                    | NUMBER ':' assignment_expr
                    | ID ID '(' ')' '{' function_body '}'
                    | ID ID '(' formal_parameter_list ')' '{' function_body '}'
        """
        pass

    def p_property_list(self, p):
        """property_list : property
                         | property_list ',' property
        """
        pass

    def p_primary_expr(self, p):
        """primary_expr : primary_expr_no_brace
                        | '{' '}'
                        | '{' property_list '}'
                        | '{' property_list ',' '}'
        """
        pass

    def p_primary_expr_no_brace(self, p):
        """primary_expr_no_brace : THIS
                                 | ID
                                 | literal
                                 | array_literal
                                 | '(' expr ')'
        """
        pass

    def p_array_literal(self, p):
        """array_literal : '[' elision_opt ']'
                         | '[' element_list ']'
                         | '[' element_list ',' elision_opt ']'
        """
        pass

    def p_element_list(self, p):
        """element_list : elision_opt assignment_expr
                        | element_list ',' elision_opt assignment_expr
        """
        pass

    def p_elision_opt(self, p):
        """elision_opt : empty
                       | elision
        """
        pass

    def p_elision(self, p):
        """elision : ','
                   | elision ','
        """
        pass

    def p_member_expr(self, p):
        """member_expr : primary_expr
                       | function_expr
                       | member_expr '[' expr ']'
                       | member_expr '.' ID
                       | NEW member_expr arguments
        """
        pass

    def p_member_expr_nobf(self, p):
        """member_expr_nobf : primary_expr_no_brace
                            | member_expr_nobf '[' expr ']'
                            | member_expr_nobf '.' ID
                            | NEW member_expr arguments
        """
        pass

    def p_new_expr(self, p):
        """new_expr : member_expr
                    | NEW new_expr
        """
        pass

    def p_new_expr_nobf(self, p):
        """new_expr_nobf : member_expr_nobf
                         | NEW new_expr_nobf
        """
        pass

    def p_call_expr(self, p):
        """call_expr : member_expr arguments
                     | call_expr arguments
                     | call_expr '[' expr ']'
                     | call_expr '.' ID
        """
        pass

    def p_call_expr_nobf(self, p):
        """call_expr_nobf : member_expr_nobf arguments
                          | call_expr_nobf arguments
                          | call_expr_nobf '[' expr ']'
                          | call_expr_nobf '.' ID
        """
        pass

    def p_arguments(self, p):
        """arguments : '(' ')'
                     | '(' argument_list ')'
        """
        pass

    def p_argument_list(self, p):
        """argument_list : assignment_expr
                         | argument_list ',' assignment_expr
        """
        pass

    def p_lef_hand_side_expr(self, p):
        """left_hand_side_expr : new_expr
                               | call_expr
        """
        pass

    def p_lef_hand_side_expr_nobf(self, p):
        """left_hand_side_expr_nobf : new_expr_nobf
                                    | call_expr_nobf
        """
        pass

    def p_postfix_expr(self, p):
        """postfix_expr : left_hand_side_expr
                        | left_hand_side_expr PLUSPLUS
                        | left_hand_side_expr MINUSMINUS
        """
        pass

    def p_postfix_expr_nobf(self, p):
        """postfix_expr_nobf : left_hand_side_expr_nobf
                             | left_hand_side_expr_nobf PLUSPLUS
                             | left_hand_side_expr_nobf MINUSMINUS
        """
        pass

    def p_unary_expr_common(self, p):
        """unary_expr_common : DELETE unary_expr
                             | VOID unary_expr
                             | TYPEOF unary_expr
                             | PLUSPLUS unary_expr
                             | MINUSMINUS unary_expr
                             | '+' unary_expr
                             | '-' unary_expr
                             | '~' unary_expr
                             | '!' unary_expr
        """
        pass

    def p_unary_expr(self, p):
        """unary_expr : postfix_expr
                      | unary_expr_common
        """
        pass

    def p_unary_expr_nobf(self, p):
        """unary_expr_nobf : postfix_expr_nobf
                           | unary_expr_common
        """
        pass

    def p_multiplicative_expr(self, p):
        """multiplicative_expr : unary_expr
                               | multiplicative_expr '*' unary_expr
                               | multiplicative_expr '/' unary_expr
                               | multiplicative_expr '%' unary_expr
        """
        pass

    def p_multiplicative_expr_nobf(self, p):
        """multiplicative_expr_nobf : unary_expr_nobf
                                    | multiplicative_expr_nobf '*' unary_expr
                                    | multiplicative_expr_nobf '/' unary_expr
                                    | multiplicative_expr_nobf '%' unary_expr
        """
        pass

    def p_additive_expr(self, p):
        """additive_expr : multiplicative_expr
                         | additive_expr '+' multiplicative_expr
                         | additive_expr '-' multiplicative_expr
        """
        pass

    def p_additive_expr_nobf(self, p):
        """additive_expr_nobf : multiplicative_expr_nobf
                              | additive_expr_nobf '+' multiplicative_expr
                              | additive_expr_nobf '-' multiplicative_expr
        """
        pass

    def p_shift_expr(self, p):
        """shift_expr : additive_expr
                      | shift_expr LSHIFT additive_expr
                      | shift_expr RSHIFT additive_expr
                      | shift_expr URSHIFT additive_expr
        """
        pass

    def p_shift_expr_nobf(self, p):
        """shift_expr_nobf : additive_expr_nobf
                           | shift_expr_nobf LSHIFT additive_expr
                           | shift_expr_nobf RSHIFT additive_expr
                           | shift_expr_nobf URSHIFT additive_expr
        """
        pass

    def p_relational_expr(self, p):
        """relational_expr : shift_expr
                           | relational_expr LT shift_expr
                           | relational_expr GT shift_expr
                           | relational_expr LE shift_expr
                           | relational_expr GE shift_expr
                           | relational_expr INSTANCEOF shift_expr
                           | relational_expr IN shift_expr
        """
        pass

    def p_relational_expr_noin(self, p):
        """relational_expr_noin : shift_expr
                                | relational_expr_noin LT shift_expr
                                | relational_expr_noin GT shift_expr
                                | relational_expr_noin LE shift_expr
                                | relational_expr_noin GE shift_expr
                                | relational_expr_noin INSTANCEOF shift_expr
        """
        pass

    def p_relational_expr_nobf(self, p):
        """relational_expr_nobf : shift_expr_nobf
                                | relational_expr_nobf LT shift_expr
                                | relational_expr_nobf GT shift_expr
                                | relational_expr_nobf LE shift_expr
                                | relational_expr_nobf GE shift_expr
                                | relational_expr_nobf INSTANCEOF shift_expr
                                | relational_expr_nobf IN shift_expr
        """
        pass

    def p_equality_expr(self, p):
        """equality_expr : relational_expr
                         | equality_expr EQEQ relational_expr
                         | equality_expr NE relational_expr
                         | equality_expr STREQ relational_expr
                         | equality_expr STRNEQ relational_expr
        """
        pass

    def p_equality_expr_noin(self, p):
        """equality_expr_noin : relational_expr_noin
                              | equality_expr_noin EQEQ relational_expr
                              | equality_expr_noin NE relational_expr
                              | equality_expr_noin STREQ relational_expr
                              | equality_expr_noin STRNEQ relational_expr
        """
        pass

    def p_equality_expr_nobf(self, p):
        """equality_expr_nobf : relational_expr_nobf
                              | equality_expr_nobf EQEQ relational_expr
                              | equality_expr_nobf NE relational_expr
                              | equality_expr_nobf STREQ relational_expr
                              | equality_expr_nobf STRNEQ relational_expr
        """
        pass

    def p_bitwise_and_expr(self, p):
        """bitwise_and_expr : equality_expr
                            | bitwise_and_expr '&' equality_expr
        """
        pass

    def p_bitwise_and_expr_noin(self, p):
        """bitwise_and_expr_noin : equality_expr_noin
                                 | bitwise_and_expr_noin '&' equality_expr_noin
        """
        pass

    def p_bitwise_and_expr_nobf(self, p):
        """bitwise_and_expr_nobf : equality_expr_nobf
                                 | bitwise_and_expr_nobf '&' equality_expr_nobf
        """
        pass

    def p_bitwise_xor_expr(self, p):
        """bitwise_xor_expr : bitwise_and_expr
                            | bitwise_xor_expr '^' bitwise_and_expr
        """
        pass

    def p_bitwise_xor_expr_noin(self, p):
        """
        bitwise_xor_expr_noin \
            : bitwise_and_expr_noin
            | bitwise_xor_expr_noin '^' bitwise_and_expr_noin
        """
        pass

    def p_bitwise_xor_expr_nobf(self, p):
        """
        bitwise_xor_expr_nobf \
            : bitwise_and_expr_nobf
            | bitwise_xor_expr_nobf '^' bitwise_and_expr_nobf
        """
        pass

    def p_bitwise_or_expr(self, p):
        """bitwise_or_expr : bitwise_xor_expr
                           | bitwise_or_expr '|' bitwise_xor_expr
        """
        pass

    def p_bitwise_or_expr_noin(self, p):
        """bitwise_or_expr_noin : bitwise_xor_expr_noin
                                | bitwise_or_expr_noin '|' bitwise_xor_expr_noin
        """
        pass

    def p_bitwise_or_expr_nobf(self, p):
        """bitwise_or_expr_nobf : bitwise_xor_expr_nobf
                                | bitwise_or_expr_nobf '|' bitwise_xor_expr_nobf
        """
        pass

    def p_logical_and_expr(self, p):
        """logical_and_expr : bitwise_or_expr
                            | logical_and_expr AND bitwise_or_expr
        """
        pass

    def p_logical_and_expr_noin(self, p):
        """
        logical_and_expr_noin : bitwise_or_expr_noin
                              | logical_and_expr_noin AND bitwise_or_expr_noin
        """
        pass

    def p_logical_and_expr_nobf(self, p):
        """
        logical_and_expr_nobf : bitwise_or_expr_nobf
                              | logical_and_expr_nobf AND bitwise_or_expr_nobf
        """
        pass

    def p_logical_or_expr(self, p):
        """logical_or_expr : logical_and_expr
                           | logical_or_expr OR logical_and_expr
        """
        pass

    def p_logical_or_expr_noin(self, p):
        """logical_or_expr_noin : logical_and_expr_noin
                                | logical_or_expr_noin OR logical_and_expr_noin
        """
        pass

    def p_logical_or_expr_nobf(self, p):
        """logical_or_expr_nobf : logical_and_expr_nobf
                                | logical_or_expr_nobf OR logical_and_expr_nobf
        """
        pass

    def p_conditional_expr(self, p):
        """
        conditional_expr \
            : logical_or_expr
            | logical_or_expr '?' assignment_expr ':' assignment_expr
        """
        pass

    def p_conditional_expr_noin(self, p):
        """
        conditional_expr_noin \
            : logical_or_expr_noin
            | logical_or_expr_noin '?' assignment_expr_noin ':' \
                  assignment_expr_noin
        """
        pass

    def p_conditional_expr_nobf(self, p):
        """
        conditional_expr_nobf \
            : logical_or_expr_nobf
            | logical_or_expr_nobf '?' assignment_expr ':' assignment_expr
        """
        pass

    def p_assignment_expr(self, p):
        """
        assignment_expr \
            : conditional_expr
            | left_hand_side_expr assignment_operator assignment_expr
        """
        pass

    def p_assignment_expr_noin(self, p):
        """
        assignment_expr_noin \
            : conditional_expr_noin
            | left_hand_side_expr assignment_operator assignment_expr_noin
        """
        pass

    def p_assignment_expr_nobf(self, p):
        """
        assignment_expr_nobf \
            : conditional_expr_nobf
            | left_hand_side_expr_nobf assignment_operator assignment_expr
        """
        pass

    def p_assignment_operator(self, p):
        """assignment_operator : '='
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
        pass

    def p_expr(self, p):
        """expr : assignment_expr
                | expr ',' assignment_expr
        """
        pass

    def p_expr_noin(self, p):
        """expr_noin : assignment_expr_noin
                     | expr_noin ',' assignment_expr_noin
        """
        pass

    def p_expr_nobf(self, p):
        """expr_nobf : assignment_expr_nobf
                     | expr_nobf ',' assignment_expr
        """
        pass

    def p_block(self, p):
        """block : '{' source_elements '}'"""
        pass

    def p_variable_statement(self, p):
        """variable_statement : VAR variable_declaration_list ';'
                              | VAR variable_declaration_list error
        """
        pass

    def p_variable_declaration_list(self, p):
        """
        variable_declaration_list \
            : variable_declaration
            | variable_declaration_list ',' variable_declaration
        """
        pass

    def p_variable_declaration_list_noin(self, p):
        """
        variable_declaration_list_noin \
            : variable_declaration_noin
            | variable_declaration_list_noin ',' variable_declaration_noin
        """
        pass

    def p_variable_declaration(self, p):
        """variable_declaration : ID
                                | ID initializer
        """
        pass

    def p_variable_declaration_noin(self, p):
        """variable_declaration_noin : ID
                                     | ID initializer_noin
        """
        pass

    def p_initializer(self, p):
        """initializer : '=' assignment_expr"""
        pass

    def p_initializer_noin(self, p):
        """initializer_noin : '=' assignment_expr_noin"""
        pass

    def p_empty_statement(self, p):
        """empty_statement : ';'"""
        pass

    def p_expr_statement(self, p):
        """expr_statement : expr_nobf ';'
                          | expr_nobf error
        """
        pass

    def p_if_statement(self, p):
        """if_statement : IF '(' expr ')' statement %prec IF_WITHOUT_ELSE
                        | IF '(' expr ')' statement ELSE statement
        """
        pass

    def p_iteration_statement(self, p):
        """
        iteration_statement \
            : DO statement WHILE '(' expr ')' ';'
            | DO statement WHILE '(' expr ')' error
            | WHILE '(' expr ')' statement
            | FOR '(' expr_noin_opt ';' expr_opt ';' expr_opt ')' statement
            | FOR '(' VAR variable_declaration_list_noin ';' expr_opt ';' \
                  expr_opt ')' statement
            | FOR '(' left_hand_side_expr IN expr ')' statement
            | FOR '(' VAR ID IN expr ')' statement
            | FOR '(' VAR ID initializer_noin IN expr ')' statement
        """
        pass

    def p_expr_opt(self, p):
        """expr_opt : empty
                    | expr
        """
        pass

    def p_expr_noin_opt(self, p):
        """expr_noin_opt : empty
                         | expr_noin
        """
        pass

    def p_continue_statement(self, p):
        """continue_statement : CONTINUE ';'
                              | CONTINUE error
                              | CONTINUE ID ';'
                              | CONTINUE ID error
        """
        pass

    def p_break_statement(self, p):
        """break_statement : BREAK ';'
                           | BREAK error
                           | BREAK ID ';'
                           | BREAK ID error
        """
        pass

    def p_return_statement(self, p):
        """return_statement : RETURN ';'
                            | RETURN error
                            | RETURN expr ';'
                            | RETURN expr error
        """
        pass

    def p_with_statement(self, p):
        """with_statement : WITH '(' expr ')' statement"""
        pass

    def p_switch_statement(self, p):
        """switch_statement : SWITCH '(' expr ')' case_block"""
        pass

    def p_case_block(self, p):
        """
        case_block \
            : '{' case_clauses_opt '}'
            | '{' case_clauses_opt default_clause case_clauses_opt '}'
        """
        pass

    def p_case_clauses_opt(self, p):
        """case_clauses_opt : empty
                            | case_clauses
        """

    def p_case_clauses(self, p):
        """case_clauses : case_clause
                        | case_clauses case_clause
        """
        pass

    def p_case_clause(self, p):
        """case_clause : CASE expr ':' source_elements"""
        pass

    def p_default_clause(self, p):
        """default_clause : DEFAULT ':' source_elements
        """
        pass

    def p_labelled_statement(self, p):
        """labelled_statement : ID ':' statement"""
        pass

    def p_throw_statement(self, p):
        """throw_statement : THROW expr ';'
                           | THROW expr error
        """
        pass

    def p_try_statement(self, p):
        """try_statement : TRY block FINALLY block
                         | TRY block CATCH '(' ID ')' block
                         | TRY block CATCH '(' ID ')' block FINALLY block
        """
        pass

    def p_debugger_statement(self, p):
        """debugger_statement : DEBUGGER ';'
                              | DEBUGGER error
        """
        pass

    def p_function_declaration(self, p):
        """
        function_declaration \
            : FUNCTION ID '(' ')' '{' function_body '}'
            | FUNCTION ID '(' formal_parameter_list ')' '{' function_body '}'
        """
        pass

    def p_function_expr(self, p):
        """
        function_expr \
            : FUNCTION '(' ')' '{' function_body '}'
            | FUNCTION '(' formal_parameter_list ')' '{' function_body '}'
            | FUNCTION ID '(' ')' '{' function_body '}'
            | FUNCTION ID '(' formal_parameter_list ')' '{' function_body '}'
        """
        pass

    def p_formal_parameter_list(self, p):
        """formal_parameter_list : ID
                                 | formal_parameter_list ',' ID
        """
        pass

    def p_function_body(self, p):
        """function_body : source_elements"""
        pass

    # Denotes an empty production according to PLY documentation
    def p_empty(self, p):
        """empty :"""
        pass

    def p_error(self, p):
        pass

