from rply import ParserGenerator
from compiler.language import *

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

                "SEMICOLON",

                "PLUS",
                "MINUS",
                "STAR",
                "SLASH",

                "EQUALS",

                "INT",
                "FLOAT",

                "IDENTIFIER",
                "INT_VAL",
                "FLOAT_VAL"
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
            return Program(p[0])

        @self.pg.production("program : statement program")
        def multi_statement(state, p):
            p[1].add_statement(p[0])
            return p[1]

        @self.pg.production("statement : INT IDENTIFIER EQUALS expression SEMICOLON")
        @self.pg.production("statement : FLOAT IDENTIFIER EQUALS expression SEMICOLON")
        def variable_declaration(state, p):
            return Assignment(self.builder, self.module, Variable(p[0].gettokentype(), p[1].getstr()), p[3])

        @self.pg.production("statement : IDENTIFIER EQUALS expression SEMICOLON")
        def variable_assignment(state, p):
            return Assignment(self.builder, self.module, Variable(None, p[0].getstr()), p[2])

        @self.pg.production("statement : PRINT OPEN_BRAC expression CLOSE_BRAC SEMICOLON")
        def print_function(state, p):
            return Print(self.builder, self.module, self.printf, p[2])

        @self.pg.production("expression : expression PLUS expression")
        @self.pg.production("expression : expression MINUS expression")
        def expression(state, p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if operator.gettokentype() == "PLUS":
                return Addition(self.builder, self.module, left, right)
            elif operator.gettokentype() == "MINUS":
                return Subtraction(self.builder, self.module, left, right)

        @self.pg.production("expression : INT_VAL")
        def number(state, p):
            return Integer(self.builder, self.module, p[0].value)

        @self.pg.production("expression : IDENTIFIER")
        def number(state, p):
            return Variable(None, p[0].getstr())

        @self.pg.error
        def error_handle(state, token):
            raise SyntaxError(f"Unexpected token '%s' at %d:%d" %
                (token.gettokentype(), token.source_pos.lineno, token.source_pos.colno))

    def get_parser(self):
        return self.pg.build()