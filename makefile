TARGET = parser
YFLAGS = -Wcounterexamples

all: $(TARGET)

$(TARGET): lex.yy.c y.tab.c
	gcc lex.yy.c y.tab