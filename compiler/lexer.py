from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # Ignore comments
        self.lexer.ignore(r"\/\/.*\n")
        self.lexer.ignore(r"\/\*(?:(?!\*\/)[\s\S])*\*\/")
        # Functions
        self.lexer.add("PRINT", r"printf")
        self.lexer.add("MALLOC", r"malloc")
        self.lexer.add("REALLOC", r"realloc")
        self.lexer.add("FREE", r"free")
        # Parenthesis
        self.lexer.add("OPEN_BRAC", r"\(")
        self.lexer.add("CLOSE_BRAC", r"\)")
        self.lexer.add("OPEN_CURL", r"\{")
        self.lexer.add("CLOSE_CURL", r"\}")
        self.lexer.add("OPEN_SQUARE", r"\[")
        self.lexer.add("CLOSE_SQUARE", r"\]")
        # Misc
        self.lexer.add("COMMA", r"\,")
        self.lexer.add("COLON", r"\:")
        self.lexer.add("SEMICOLON", r"\;")
        # Operators
        self.lexer.add("PLUS", r"\+")
        self.lexer.add("MINUS", r"\-")
        self.lexer.add("STAR", r"\*")
        self.lexer.add("SLASH", r"\/")
        self.lexer.add("AMPERSAND", r"\&")

        self.lexer.add("COMPARISON", r"\=\=|\!\=|\<|\>|\<\=|\>\=")

        self.lexer.add("EQUALS", r"\=")

        # Value literals
        self.lexer.add("INT_VAL", r"\d+")
        self.lexer.add("FLOAT_VAL", r"\d*\.\d+")
        self.lexer.add("BOOL_VAL", r"true|false")
        self.lexer.add("CHAR_VAL", r"\'\\?.\'")
        self.lexer.add("STRING_VAL", r"\".*\"")
        # Data types
        self.lexer.add("SHORT", r"short")
        self.lexer.add("INT", r"int")
        self.lexer.add("LONG", r"long")
        self.lexer.add("FLOAT", r"float")
        self.lexer.add("DOUBLE", r"double")
        self.lexer.add("BOOL", r"bool")
        self.lexer.add("CHAR", r"char")
        self.lexer.add("STRING", r"string")
        # Key words
        self.lexer.add("IF", r"if")
        self.lexer.add("ELSE", r"else")
        self.lexer.add("SWITCH", r"switch")
        self.lexer.add("CASE", r"case")
        self.lexer.add("DEFAULT", r"default")
        self.lexer.add("WHILE", r"while")
        self.lexer.add("DO", r"do")
        self.lexer.add("REPEAT", r"repeat")
        self.lexer.add("UNTIL", r"until")
        self.lexer.add("FOR", r"for")

        self.lexer.add("BREAK", r"break")
        self.lexer.add("CONTINUE", r"continue")
        self.lexer.add("RETURN", r"return")
        # Identifiers
        self.lexer.add("IDENTIFIER", r"\w+")
        # Ignore spaces
        self.lexer.ignore(r"\s+")

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()