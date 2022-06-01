from rply import ParserGenerator
from llvmlite import ir
from .lang import *

class Parser():
    def __init__(self, builder, functions, token_names):
        self.pg = ParserGenerator(
            token_names,
            precedence = [
                # (multiply and divide before plus or minus)
                ("left", ["PLUS", "MINUS"]),
                ("left", ["STAR", "SLASH"]),
                ("left", ["COMPARISON"]),
            ]
        )
        self.state = self.ParserState(builder, functions)

    class ParserState(object):
        def __init__(self, builder, functions, variables={}):
            self.module = builder.module
            self.builder = builder
            self.functions = functions
            self.variables = variables
            self.control = self.Control()

        class Control(object):
            def __init__(self):
                self.end = None
                self.loop_body = None
                self.loop_incrementor = None

    def parse(self):

        ############
        # Sequence #
        ############

        @self.pg.production("sequence : block")
        @self.pg.production("sequence : statement SEMICOLON")
        def sequence(p):
            return Sequence(self.state, p[0])

        @self.pg.production("sequence : block sequence")
        def block(p):
            return p[1].add_statement(p[0])

        @self.pg.production("sequence : statement SEMICOLON sequence")
        def statement(p):
            return p[2].add_statement(p[0])

        # Assignment
        @self.pg.production("statement : type IDENTIFIER")
        def variable_declaration(p):
            return Declaration(self.state, p[0], p[1].getstr())

        @self.pg.production("statement : variable EQUALS expression")
        def variable_assignment(p):
            return Assignment(self.state, p[0], p[2])
        
        @self.pg.production("statement : type IDENTIFIER EQUALS expression")
        def variable_declaration_assignment(p):
            return Assignment(self.state, Declaration(self.state, p[0], p[1].getstr()), p[3])
        
        # Control flow keywords
        @self.pg.production("statement : BREAK")
        @self.pg.production("statement : CONTINUE")
        @self.pg.production("statement : RETURN")
        def control_flow(p):
            if p[0].gettokentype() == "BREAK":
                return Break(self.state)
            elif p[0].gettokentype() == "CONTINUE":
                return Continue(self.state)

        # Expression (for function calls, etc.)
        @self.pg.production("statement : expression")
        def expression(p):
            return p[0]

        # Ensures a semicolon by itself is a valid statement
        # (This is useful for 'for loops')
        @self.pg.production("statement : ")
        def expression(p):
            return Pass()

        #############
        # Selection #
        #############

        # Binary selection
        @self.pg.production("block : IF OPEN_BRAC expression CLOSE_BRAC OPEN_CURL sequence CLOSE_CURL")
        def if_then(p):
            return BinarySelection(self.state, p[2], p[5])

        @self.pg.production("block : IF OPEN_BRAC expression CLOSE_BRAC OPEN_CURL sequence CLOSE_CURL ELSE nested_if")
        def if_nested(p):
            return BinarySelection(self.state, p[2], p[5], p[8])

        @self.pg.production("nested_if : IF OPEN_BRAC expression CLOSE_BRAC OPEN_CURL sequence CLOSE_CURL ELSE nested_if")
        def if_nested_chain(p):
            return Sequence(self.state, BinarySelection(self.state, p[2], p[5], p[8]))

        @self.pg.production("nested_if : IF OPEN_BRAC expression CLOSE_BRAC OPEN_CURL sequence CLOSE_CURL")
        def nested_if_then(p):
            return Sequence(self.state, BinarySelection(self.state, p[2], p[5]))

        @self.pg.production("nested_if : OPEN_CURL sequence CLOSE_CURL")
        def nested_else(p):
            return p[1]

        # Multiway selection
        @self.pg.production("block : SWITCH OPEN_BRAC expression CLOSE_BRAC OPEN_CURL cases CLOSE_CURL")
        def switch(p):
            return p[5].set_expression(p[2])

        @self.pg.production("cases : DEFAULT COLON sequence")
        def default(p):
            return MultiwaySelection(self.state, p[2])

        @self.pg.production("cases : CASE expression COLON sequence")
        def no_default(p):
            return MultiwaySelection(self.state, None).add_case(expression)

        @self.pg.production("cases : CASE expression COLON sequence cases")
        def case(p):
            return p[4].add_case(p[1], p[3])

        ##############
        # Repetition #
        ##############

        # Pre-test repetition
        @self.pg.production("block : WHILE OPEN_BRAC expression CLOSE_BRAC OPEN_CURL sequence CLOSE_CURL")
        def pre_test(p):
            return PreTest(self.state, p[2], p[5])

        @self.pg.production("block : FOR OPEN_BRAC statement SEMICOLON statement SEMICOLON statement CLOSE_BRAC OPEN_CURL sequence CLOSE_CURL")
        def for_loop(p):
            return ForLoop(self.state, p[2], p[4], p[6], p[9])


        # Post-test repetition
        @self.pg.production("block : REPEAT OPEN_CURL sequence CLOSE_CURL UNTIL OPEN_BRAC expression CLOSE_BRAC SEMICOLON")
        def post_test(p):
            return PostUntil(self.state, p[6], p[2])

        @self.pg.production("block : DO OPEN_CURL sequence CLOSE_CURL WHILE OPEN_BRAC expression CLOSE_BRAC SEMICOLON")
        def post_test(p):
            return PostWhile(self.state, p[6], p[2])

        #######################
        # Variables and Types #
        #######################

        @self.pg.production("type : type STAR")
        def pointer_type(p):
            return p[0].as_pointer()
        
        @self.pg.production("type : type OPEN_SQUARE INT_VAL CLOSE_SQUARE")
        def array_type(p):
            return get_array_type(p[0], p[2].value)

        @self.pg.production("type : INT")
        @self.pg.production("type : DOUBLE")
        @self.pg.production("type : BOOL")
        @self.pg.production("type : CHAR")
        def type(p):
            if p[0].gettokentype() == "INT":
                return Integer.TYPE
            elif p[0].gettokentype() == "DOUBLE":
                return Double.TYPE
            elif p[0].gettokentype() == "BOOL":
                return Boolean.TYPE
            elif p[0].gettokentype() == "CHAR":
                return Character.TYPE
        
        @self.pg.production("variable : IDENTIFIER")
        def variable(p):
            return Variable(self.state, p[0].getstr(), [], True)

        @self.pg.production("variable : AMPERSAND IDENTIFIER")
        def variable(p):
            return Variable(self.state, p[0].getstr(), [], False)

        @self.pg.production("variable : variable derefrence")
        def variable_derefrence(p):
            p[0].derefrence_at(p[1])
            return p[0]

        @self.pg.production("derefrence : OPEN_SQUARE expression CLOSE_SQUARE")
        def derefrence(p):
            return p[1]

        ###############
        # Expressions #
        ###############

        # Function calls
        @self.pg.production("expression : PRINT OPEN_BRAC argument CLOSE_BRAC")
        @self.pg.production("expression : MALLOC OPEN_BRAC argument CLOSE_BRAC")
        @self.pg.production("expression : REALLOC OPEN_BRAC argument CLOSE_BRAC")
        def intrinsic_function(p):
            return Function(self.state, p[0].getstr(), p[2])

        @self.pg.production("argument : expression COMMA argument")
        def arguments(p):
            p[2].add_argument(p[0])
            return p[2]

        @self.pg.production("argument : expression")
        def argument(p):
            return Arguments(self.state, p[0])

        # Variables and literals
        @self.pg.production("expression : variable")
        def variable(p):
            return p[0]

        @self.pg.production("expression : INT_VAL")
        @self.pg.production("expression : FLOAT_VAL")
        @self.pg.production("expression : BOOL_VAL")
        @self.pg.production("expression : CHAR_VAL")
        @self.pg.production("expression : STRING_VAL")
        def literal(p):
            if p[0].gettokentype() == "INT_VAL":
                return Integer(self.state, p[0].value)
            elif p[0].gettokentype() == "FLOAT_VAL":
                return Double(self.state, p[0].value)
            elif p[0].gettokentype() == "BOOL_VAL":
                return Boolean(self.state, p[0].getstr())
            elif p[0].gettokentype() == "CHAR_VAL":
                return Character(self.state, p[0].getstr())
            elif p[0].gettokentype() == "STRING_VAL":
                return String(self.state, p[0].getstr())
        
        # Operations
        @self.pg.production('expression : OPEN_BRAC expression CLOSE_BRAC')
        def expression_brackets(p):
            return p[1]

        @self.pg.production('expression : OPEN_BRAC type CLOSE_BRAC expression')
        def casting(p):
            return Cast(self.state, p[3], p[1])

        @self.pg.production("expression : MINUS expression")
        @self.pg.production("expression : STAR expression")
        def unary_ops(p):
            if p[0].gettokentype() == "MINUS":
                return Negative(self.state, p[1])
            elif p[0].gettokentype() == "STAR":
                return Derefrence(self.state, p[1])

        @self.pg.production("expression : expression STAR expression")
        @self.pg.production("expression : expression SLASH expression")
        @self.pg.production("expression : expression PLUS expression")
        @self.pg.production("expression : expression MINUS expression")
        @self.pg.production("expression : expression COMPARISON expression")
        def binary_ops(p):
            if p[1].gettokentype() == "STAR":
                return Multiplication(self.state, p[0], p[2])
            elif p[1].gettokentype() == "SLASH":
                return Division(self.state, p[0], p[2])
            elif p[1].gettokentype() == "PLUS":
                return Addition(self.state, p[0], p[2])
            elif p[1].gettokentype() == "MINUS":
                return Subtraction(self.state, p[0], p[2])
            elif p[1].gettokentype() == "COMPARISON":
                return Comparison(self.state, p[1].getstr(), p[0], p[2])

        #################
        # Miscellaneous #
        #################

        @self.pg.error
        def error_handle(token):
            if token.source_pos == None:
                raise SyntaxError("Unexpected token '%s'" % token.gettokentype())
            else:
                raise SyntaxError("Unexpected token '%s' at %d:%d" %
                    (token.gettokentype(), token.source_pos.lineno, token.source_pos.colno))

    def get_parser(self):
        return self.pg.build()