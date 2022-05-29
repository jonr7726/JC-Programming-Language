from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # Print
        self.lexer.add("PRINT", r"print")
        # Parenthesis
        self.lexer.add("OPEN_BRAC", r"\(")
        self.lexer.add("CLOSE_BRAC", r"\)")
        # Comma
        self.lexer.add("COMMA", r"\,")
        # Semi Colon
        self.lexer.add("SEMICOLON", r"\;")
        # Operators
        self.lexer.add("PLUS", r"\+")
        self.lexer.add("MINUS", r"\-")
        self.lexer.add("STAR", r"\*")
        self.lexer.add("SLASH", r"\/")

        self.lexer.add("EQUALS", r"\=")
        # Value literals
        self.lexer.add("FLOAT_VAL", r"\d*\.\d+")
        self.lexer.add("INT_VAL", r"\d+")
        self.lexer.add("STRING_VAL", r"\".*\"")
        # Data types
        self.lexer.add("INT", r"int")
        self.lexer.add("LONG", r"long")
        self.lexer.add("DOUBLE", r"double")
        self.lexer.add("FLOAT", r"float")
        # Identifiers
        self.lexer.add("IDENTIFIER", r"\w+")
        # Ignore spaces
        self.lexer.ignore(r"\s+")

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()