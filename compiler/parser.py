from rply import ParserGenerator
from llvmlite import ir
from .lang.literals import *
from .lang.variables import *
from .lang.unops import *
from .lang.binops import *
from .lang.functions import *
from .lang.structure import *

class Parser():
    def __init__(self, module, builder, functions):
        self.pg = ParserGenerator(
            [
                # A list of all token names accepted by the parser.
                "PRINT",
                "MALLOC",
                "REALLOC",

                "OPEN_BRAC",
                "CLOSE_BRAC",
                "OPEN_SQUARE",
                "CLOSE_SQUARE",

                "COMMA",

                "SEMICOLON",

                "PLUS",
                "MINUS",
                "STAR",
                "SLASH",
                "AMPERSAND",

                "EQUALS",

                "INT",
                "DOUBLE",
                "BOOL",
                "CHAR",

                "INT_VAL",
                "FLOAT_VAL",
                "BOOL_VAL",
                "CHAR_VAL",
                "STRING_VAL",

                "IDENTIFIER",
            ],

            precedence=[ # (multiply and divide before plus or minus)
                ("left", ["PLUS", "MINUS"]),
                ("left", ["STAR", "SLASH"])
            ]
        )
        self.state = self.ParserState(module, builder, functions)

    class ParserState(object):
        def __init__(self, module, builder, functions, variables={}):
            self.module = module
            self.builder = builder
            self.functions = functions
            self.variables = variables

    def parse(self):
        @self.pg.production("program : statement SEMICOLON")
        def single_statement(p):
            return Program(self.state, p[0])

        @self.pg.production("program : statement SEMICOLON program")
        def multi_statement(p):
            p[2].add_statement(p[0])
            return p[2]

        @self.pg.production("statement : type IDENTIFIER")
        def variable_declaration(p):
            return Declaration(self.state, p[0], p[1].getstr())

        @self.pg.production("statement : variable EQUALS expression")
        def variable_assignment(p):
            return Assignment(self.state, p[0], p[2])
        
        @self.pg.production("statement : type IDENTIFIER EQUALS expression")
        def variable_declaration_assignment(p):
            return Assignment(self.state, Declaration(self.state, p[0], p[1].getstr()), p[3])
        
        @self.pg.production("statement : expression")
        def expression(p):
            return p[0]

        @self.pg.production("argument : expression COMMA argument")
        def arguments(p):
            p[2].add_argument(p[0])
            return p[2]

        @self.pg.production("argument : expression")
        def argument(p):
            return Arguments(self.state, p[0])

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

        @self.pg.production("expression : PRINT OPEN_BRAC argument CLOSE_BRAC")
        @self.pg.production("expression : MALLOC OPEN_BRAC argument CLOSE_BRAC")
        @self.pg.production("expression : REALLOC OPEN_BRAC argument CLOSE_BRAC")
        def intrinsic_function(p):
            return Function(self.state, p[0].getstr(), p[2])

        @self.pg.production('expression : OPEN_BRAC type CLOSE_BRAC expression')
        def casting(p):
            return Cast(self.state, p[3], p[1])

        @self.pg.production('expression : OPEN_BRAC expression CLOSE_BRAC')
        def expression_brackets(p):
            return p[1]
        
        @self.pg.production("expression : expression STAR expression")
        @self.pg.production("expression : expression SLASH expression")
        @self.pg.production("expression : expression PLUS expression")
        @self.pg.production("expression : expression MINUS expression")
        def binops(p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if p[1].gettokentype() == "STAR":
                return Multiplication(self.state, p[0], p[2])
            elif p[1].gettokentype() == "SLASH":
                return Division(self.state, p[0], p[2])
            elif p[1].gettokentype() == "PLUS":
                return Addition(self.state, p[0], p[2])
            elif p[1].gettokentype() == "MINUS":
                return Subtraction(self.state, p[0], p[2])

        @self.pg.production("expression : MINUS expression")
        @self.pg.production("expression : STAR expression")
        def unops(p):
            if p[0].gettokentype() == "MINUS":
                return Negative(self.state, p[1])
            elif p[0].gettokentype() == "STAR":
                return Derefrence(self.state, p[1])

        @self.pg.production("expression : INT_VAL")
        @self.pg.production("expression : FLOAT_VAL")
        @self.pg.production("expression : BOOL_VAL")
        @self.pg.production("expression : CHAR_VAL")
        @self.pg.production("expression : STRING_VAL")
        def number(p):
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

        @self.pg.production("expression : variable")
        def number(p):
            return p[0]

        @self.pg.error
        def error_handle(token):
            if token.source_pos == None:
                raise SyntaxError("Unexpected token '%s'" % token.gettokentype())
            else:
                raise SyntaxError("Unexpected token '%s' at %d:%d" %
                    (token.gettokentype(), token.source_pos.lineno, token.source_pos.colno))

    def get_parser(self):
        return self.pg.build()