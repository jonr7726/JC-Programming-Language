TARGET = parser
YFLAGS = -Wcounterexamples

all: $(TARGET)

$(TARGET): lex.yy.c y.tab.c
	gcc lex.yy.c y.tab.c -o $(TARGET)

y.tab.c:
	yacc -d parser.y $(YFLAGS)

lex.yy.c:
	lex lexer.l