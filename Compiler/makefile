# https://medium.com/codex/building-a-c-compiler-using-lex-and-yacc-446262056aaa
# 	https://github.com/AnjaneyaTripathi/c-compiler/blob/master/Part%206%20-%20Intermediate%20Code%20Generation/parser5.y
# https://mukulrathi.com/create-your-own-programming-language/llvm-ir-cpp-api-tutorial/
# https://gnuu.org/2009/09/18/writing-your-own-toy-compiler/

# TODO: Add scope to identifiers

TARGET = main
YFLAGS = -Wcounterexamples

# Directory structure
SRC_DIR = src
BUILD_DIR = build
LIBS = lib

all: $(TARGET)

# Create parser from Bison/Lex output code
$(TARGET): $(BUILD_DIR)/lex.yy.c $(BUILD_DIR)/y.tab.c
	gcc -I$(LIBS) $(BUILD_DIR)/lex.yy.c $(BUILD_DIR)/y.tab.c -o $@

# Create Bison output code
$(BUILD_DIR)/y.tab.c: $(BUILD_DIR)
	yacc -d $(SRC_DIR)/parser.y -o $@ $(YFLAGS)

# Create Lex output code
$(BUILD_DIR)/lex.yy.c: $(BUILD_DIR)
	lex -o $@ $(SRC_DIR)/lexer.l

# Create build directory (if not already present)
$(BUILD_DIR):
	mkdir $@

# Remove build files and compiled target file
.PHONY: clean
clean:
	rm -rf ${BUILD_DIR}$/*
	rm $(TARGET)