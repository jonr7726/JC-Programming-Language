from rply import ParserGenerator
from .lang.literals import *
from .lang.variables import *
from .lang.unops import *
from .lang.binops import *
from .lang.functions import *
from .lang.structure import *

class ParserState(object):
    def __init__(self):
        self.variables = {}

class Parser():
    def __init__(self, module, builder, printf):
        self.pg = ParserGenerator(
            [
                # A list of all token names accepted by the parser.
                "PRINT",

                "OPEN_BRAC",
                "CLOSE_BRAC",

                "COMMA",

                "SEMICOLON",

                "PLUS",
                "MINUS",
                "STAR",
                "SLASH",

                "EQUALS",

                "INT",
                "DOUBLE",

                "IDENTIFIER",
                "INT_VAL",
                "FLOAT_VAL",
                "STRING_VAL",
            ],

            precedence=[ # (multiply and divide before plus or minus)
                ("left", ["PLUS", "MINUS"]),
                ("left", ["STAR", "SLASH"])
            ]
        )
        self.module = module
        self.builder = builder
        self.printf = printf
        self.variables = {}

    def parse(self):
        @self.pg.production("program : statement")
        def single_statement(state, p):
            return Program(self.builder, self.module, p[0])

        @self.pg.production("program : statement program")
        def multi_statement(state, p):
            p[1].add_statement(p[0])
            return p[1]

        @self.pg.production("statement : INT IDENTIFIER SEMICOLON")
        @self.pg.production("statement : DOUBLE IDENTIFIER SEMICOLON")
        def variable_declaration(state, p):
            return Declaration(self.builder, self.module, p[0].gettokentype(), p[1].getstr())

        @self.pg.production("statement : IDENTIFIER EQUALS expression SEMICOLON")
        def variable_assignment(state, p):
            return Assignment(self.builder, self.module, Variable(self.builder, self.module, p[0].getstr()), p[2])

        @self.pg.production("statement : INT IDENTIFIER EQUALS expression SEMICOLON")
        @self.pg.production("statement : DOUBLE IDENTIFIER EQUALS expression SEMICOLON")
        def variable_declaration_assignment(state, p):
            return Assignment(self.builder, self.module, Declaration(self.builder, self.module, p[0].gettokentype(), p[1].getstr()), p[3])

        @self.pg.production("statement : PRINT OPEN_BRAC argument CLOSE_BRAC SEMICOLON")
        def print_function(state, p):
            return Print(self.builder, self.module, self.printf, p[2])

        @self.pg.production("argument : expression COMMA argument")
        def arguments(state, p):
            p[2].add_argument(p[0])
            return p[2]

        @self.pg.production("argument : expression")
        def argument(state, p):
            return Arguments(self.builder, self.module, p[0])

        @self.pg.production('expression : OPEN_BRAC INT CLOSE_BRAC expression')
        @self.pg.production('expression : OPEN_BRAC DOUBLE CLOSE_BRAC expression')
        def casting(state, p):
            if p[1].gettokentype() == "INT":
                return IntegerCast(self.builder, self.module, p[3])
            elif p[1].gettokentype() == "DOUBLE":
                return DoubleCast(self.builder, self.module, p[3])

        @self.pg.production('expression : OPEN_BRAC expression CLOSE_BRAC')
        def expression_bracets(state, p):
            return p[1]

        @self.pg.production("expression : expression STAR expression")
        @self.pg.production("expression : expression SLASH expression")
        @self.pg.production("expression : expression PLUS expression")
        @self.pg.production("expression : expression MINUS expression")
        def binops(state, p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if p[1].gettokentype() == "STAR":
                return Multiplication(self.builder, self.module, p[0], p[2])
            elif p[1].gettokentype() == "SLASH":
                return Division(self.builder, self.module, p[0], p[2])
            elif p[1].gettokentype() == "PLUS":
                return Addition(self.builder, self.module, p[0], p[2])
            elif p[1].gettokentype() == "MINUS":
                return Subtraction(self.builder, self.module, p[0], p[2])

        @self.pg.production("expression : MINUS expression")
        def unops(state, p):
            if p[0].gettokentype() == "MINUS":
                return Negative(self.builder, self.module, p[1])

        @self.pg.production("expression : FLOAT_VAL")
        def number(state, p):
            return Double(self.builder, self.module, p[0].value)

        @self.pg.production("expression : INT_VAL")
        def number(state, p):
            return Integer(self.builder, self.module, p[0].value)

        @self.pg.production("expression : STRING_VAL")
        def number(state, p):
            return String(self.builder, self.module, p[0].getstr())

        @self.pg.production("expression : IDENTIFIER")
        def number(state, p):
            return Variable(self.builder, self.module, p[0].getstr())

        @self.pg.error
        def error_handle(state, token):
            if token.source_pos == None:
                raise SyntaxError("Unexpected token '%s'" % token.gettokentype())
            else:
                raise SyntaxError("Unexpected token '%s' at %d:%d" %
                    (token.gettokentype(), token.source_pos.lineno, token.source_pos.colno))

    def get_parser(self):
        return self.pg.build()