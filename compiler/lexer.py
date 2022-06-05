from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # Ignore comments
        self.lexer.ignore(r"\/\/.*\n")
        self.lexer.ignore(r"\/\*(?:(?!\*\/)[\s\S])*\*\/")

        # Parenthesis
        self.lexer.add("(", r"\(")
        self.lexer.add(")", r"\)")
        self.lexer.add("{", r"\{")
        self.lexer.add("}", r"\}")
        self.lexer.add("[", r"\[")
        self.lexer.add("]", r"\]")

        # Misc
        self.lexer.add(",", r"\,")
        self.lexer.add(":", r"\:")
        self.lexer.add(";", r"\;")
        self.lexer.add("->", r"\-\>")

        # Assignment operators
        self.lexer.add("+=", r"\+\=")
        self.lexer.add("-=", r"\-\=")
        self.lexer.add("*=", r"\*\=")
        self.lexer.add("/=", r"\/\=")
        self.lexer.add("%=", r"\%\=")
        self.lexer.add("<<=", r"\<\<\=")
        self.lexer.add(">>=", r"\>\>\=")
        self.lexer.add("&=", r"\&\=")
        self.lexer.add("|=", r"\|\=")
        self.lexer.add("^=", r"\^\=")

        # Incrementor operators
        self.lexer.add("++", r"\+\+")
        self.lexer.add("--", r"\-\-")

        # Value literals
        self.lexer.add("INT_VAL", r"-?\d+")
        self.lexer.add("FLOAT_VAL", r"-?\d*\.\d+")
        self.lexer.add("BOOL_VAL", r"true|false")
        self.lexer.add("CHAR_VAL", r"\'\\?.\'")
        self.lexer.add("STRING_VAL", r"\".*\"")

        # Arithmetic operators
        self.lexer.add("+", r"\+")
        self.lexer.add("-", r"\-")
        self.lexer.add("*", r"\*")
        self.lexer.add("/", r"\/")
        self.lexer.add("PERCENTAGE", r"\%")

        # Boolean logic operators
        self.lexer.add("NOT", r"\!|not")
        self.lexer.add("NAND", r"nand")
        self.lexer.add("AND", r"\&\&|and")
        self.lexer.add("XNOR", r"xnor")
        self.lexer.add("XOR", r"\^\^|xor")
        self.lexer.add("NOR", r"nor")
        self.lexer.add("OR", r"\|\||or")

        # Bitwise logic operators
        self.lexer.add("&", r"\&")
        self.lexer.add("|", r"\|")
        self.lexer.add("^", r"\^")

        # Other operators
        self.lexer.add("~", r"\~")
        self.lexer.add("?", r"\?")
        self.lexer.add("<<", r"\<\<")
        self.lexer.add(">>", r"\>\>")

        # Comparison operators
        self.lexer.add("==", r"\=\=")
        self.lexer.add("!=", r"\!\=|\<\>")
        self.lexer.add("<=", r"\<\=")
        self.lexer.add(">=", r"\>\=")
        self.lexer.add("<", r"\<")
        self.lexer.add(">", r"\>")

        # (Cant be grouped with other assignment operators due to regex precedence)
        self.lexer.add("=", r"\=")

        # Data types
        self.lexer.add("VOID", r"void")
        self.lexer.add("BOOL", r"bool")
        self.lexer.add("CHAR", r"char")
        self.lexer.add("SHORT", r"short")
        self.lexer.add("INT", r"int")
        self.lexer.add("LONG", r"long")
        self.lexer.add("HALF", r"half")
        self.lexer.add("FLOAT", r"float")
        self.lexer.add("DOUBLE", r"double")

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