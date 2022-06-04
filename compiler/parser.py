from rply import ParserGenerator
from llvmlite import ir
from .lang import *

class Parser():
    def __init__(self, builder, functions, token_names):
        self.pg = ParserGenerator(
            token_names,
            precedence = [
                # See https://www.tutorialspoint.com/cprogramming/c_operators_precedence.htm
                ("left", [","]),
                ("right", ["=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "&=", "|=", "^="]),
                ("right", ["?"]),
                ("left", ["OR"]),
                ("left", ["XOR"]), # (Custom)
                ("left", ["AND"]),
                ("left", ["NOR"]), # (Custom)
                ("left", ["XNOR"]), # (Custom)
                ("left", ["NAND"]), # (Custom)
                ("left", ["|"]),
                ("left", ["^"]),
                ("left", ["&"]),
                ("left", ["==", "!="]),
                ("left", ["<", "<=", ">", ">="]),
                ("left", ["<<", ">>"]),
                ("left", ["+", "-", "PERCENTAGE"]),
                ("left", ["*", "/"]),
                ("right", ["NOT", "~", "++", "--"])
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
        @self.pg.production("sequence : statement ;")
        def sequence(p):
            return Sequence(self.state, p[0])

        @self.pg.production("sequence : block sequence")
        def block(p):
            return p[1].add_statement(p[0])

        @self.pg.production("sequence : statement ; sequence")
        def statement(p):
            return p[2].add_statement(p[0])

        # Assignment
        @self.pg.production("statement : type IDENTIFIER")
        def variable_declaration(p):
            return Declaration(self.state, p[0], p[1].getstr())

        @self.pg.production("statement : variable = expression")
        @self.pg.production("statement : variable += expression")
        @self.pg.production("statement : variable -= expression")
        @self.pg.production("statement : variable *= expression")
        @self.pg.production("statement : variable /= expression")
        @self.pg.production("statement : variable ++")
        @self.pg.production("statement : variable --")
        def variable_assignment(p):
            if p[1].gettokentype() == "=":
                return Assignment(self.state, p[0], p[2])
            elif p[1].gettokentype() == "+=":
                return Assignment(self.state, p[0], Addition(self.state, p[0].copy(), p[2]))
            elif p[1].gettokentype() == "-=":
                return Assignment(self.state, p[0], Subtraction(self.state, p[0].copy(), p[2]))
            elif p[1].gettokentype() == "*=":
                return Assignment(self.state, p[0], Multiplication(self.state, p[0].copy(), p[2]))
            elif p[1].gettokentype() == "/=":
                return Assignment(self.state, p[0], Division(self.state, p[0].copy(), p[2]))
            elif p[1].gettokentype() == "++":
                return Assignment(self.state, p[0], Addition(self.state, p[0].copy(), Integer(self.state, 1)))
            elif p[1].gettokentype() == "--":
                return Assignment(self.state, p[0], Subtraction(self.state, p[0].copy(), Integer(self.state, 1)))
        
        @self.pg.production("statement : type IDENTIFIER = expression")
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
        @self.pg.production("block : IF ( expression ) { sequence }")
        def if_then(p):
            return BinarySelection(self.state, p[2], p[5])

        @self.pg.production("block : IF ( expression ) { sequence } ELSE nested_if")
        def if_nested(p):
            return BinarySelection(self.state, p[2], p[5], p[8])

        @self.pg.production("nested_if : IF ( expression ) { sequence } ELSE nested_if")
        def if_nested_chain(p):
            return Sequence(self.state, BinarySelection(self.state, p[2], p[5], p[8]))

        @self.pg.production("nested_if : IF ( expression ) { sequence }")
        def nested_if_then(p):
            return Sequence(self.state, BinarySelection(self.state, p[2], p[5]))

        @self.pg.production("nested_if : { sequence }")
        def nested_else(p):
            return p[1]

        # Multiway selection
        @self.pg.production("block : SWITCH ( expression ) { cases }")
        def switch(p):
            return p[5].set_expression(p[2])

        @self.pg.production("cases : DEFAULT : sequence")
        def default(p):
            return MultiwaySelection(self.state, p[2])

        @self.pg.production("cases : CASE expression : sequence")
        def no_default(p):
            return MultiwaySelection(self.state, None).add_case(expression)

        @self.pg.production("cases : CASE expression : sequence cases")
        def case(p):
            return p[4].add_case(p[1], p[3])

        ##############
        # Repetition #
        ##############

        # Pre-test repetition
        @self.pg.production("block : WHILE ( expression ) { sequence }")
        def pre_test(p):
            return PreTest(self.state, p[2], p[5])

        @self.pg.production("block : FOR ( statement ; statement ; statement ) { sequence }")
        def for_loop(p):
            return ForLoop(self.state, p[2], p[4], p[6], p[9])


        # Post-test repetition
        @self.pg.production("block : REPEAT { sequence } UNTIL ( expression ) ;")
        def post_test(p):
            return PostUntil(self.state, p[6], p[2])

        @self.pg.production("block : DO { sequence } WHILE ( expression ) ;")
        def post_test(p):
            return PostWhile(self.state, p[6], p[2])

        #######################
        # Variables and Types #
        #######################

        @self.pg.production("type : type *")
        def pointer_type(p):
            return p[0].as_pointer()
        
        @self.pg.production("type : type [ INT_VAL ]")
        def array_type(p):
            return get_array_type(p[0], p[2].value)

        @self.pg.production("type : INT")
        @self.pg.production("type : LONG")
        @self.pg.production("type : DOUBLE")
        @self.pg.production("type : BOOL")
        @self.pg.production("type : CHAR")
        def type(p):
            if p[0].gettokentype() == "INT":
                return Integer.TYPE
            elif p[0].gettokentype() == "LONG":
                return Long.TYPE
            elif p[0].gettokentype() == "DOUBLE":
                return Double.TYPE
            elif p[0].gettokentype() == "BOOL":
                return Boolean.TYPE
            elif p[0].gettokentype() == "CHAR":
                return Character.TYPE
        
        @self.pg.production("variable : IDENTIFIER")
        def variable(p):
            return Variable(self.state, p[0].getstr(), [], True)

        @self.pg.production("variable : & IDENTIFIER")
        def variable(p):
            return Variable(self.state, p[0].getstr(), [], False)

        @self.pg.production("variable : variable derefrence")
        def variable_derefrence(p):
            p[0].derefrence_at(p[1])
            return p[0]

        @self.pg.production("derefrence : [ expression ]")
        def derefrence(p):
            return p[1]

        ###############
        # Expressions #
        ###############

        # Function calls
        @self.pg.production("expression : PRINT ( argument )")
        @self.pg.production("expression : MALLOC ( argument )")
        @self.pg.production("expression : REALLOC ( argument )")
        def intrinsic_function(p):
            return Function(self.state, p[0].getstr(), p[2])

        @self.pg.production("argument : expression , argument")
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
                if int(p[0].value) > 2147483647 or int(p[0].value) < -2147483648:
                    return Long(self.state, p[0].value)
                else:
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
        @self.pg.production('expression : ( expression )')
        def expression_brackets(p):
            return p[1]

        @self.pg.production('expression : ( type ) expression')
        def casting(p):
            return Cast(self.state, p[3], p[1])

        @self.pg.production("expression : - expression")
        @self.pg.production("expression : * expression")
        @self.pg.production("expression : NOT expression")
        def unary_ops(p):
            return Operation(self.state, p[0], left=None, right=p[1])

        @self.pg.production("expression : expression * expression")
        @self.pg.production("expression : expression / expression")
        @self.pg.production("expression : expression + expression")
        @self.pg.production("expression : expression - expression")
        @self.pg.production("expression : expression PERCENTAGE expression")
        @self.pg.production("expression : expression == expression")
        @self.pg.production("expression : expression != expression")
        @self.pg.production("expression : expression < expression")
        @self.pg.production("expression : expression <= expression")
        @self.pg.production("expression : expression > expression")
        @self.pg.production("expression : expression >= expression")
        @self.pg.production("expression : expression << expression")
        @self.pg.production("expression : expression >> expression")
        @self.pg.production("expression : expression OR expression")
        @self.pg.production("expression : expression AND expression")
        @self.pg.production("expression : expression XOR expression")
        @self.pg.production("expression : expression NOR expression")
        @self.pg.production("expression : expression NAND expression")
        @self.pg.production("expression : expression XNOR expression")
        @self.pg.production("expression : expression | expression")
        @self.pg.production("expression : expression & expression")
        @self.pg.production("expression : expression ^ expression")
        def binary_ops(p):
            return Operation(self.state, p[1], p[0], p[2])

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