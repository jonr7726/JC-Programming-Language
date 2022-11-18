# https://medium.com/codex/building-a-c-compiler-using-lex-and-yacc-446262056aaa
# 	https://github.com/AnjaneyaTripathi/c-compiler/blob/master/Part%206%20-%20Intermediate%20Code%20Generation/parser5.y
# https://gnuu.org/2009/09/18/writing-your-own-toy-compiler/

# https://mukulrathi.com/create-your-own-programming-language/llvm-ir-cpp-api-tutorial/
# https://www.pauladamsmith.com/blog/2015/01/how-to-get-started-with-llvm-c-api.html
# 	https://github.com/paulsmith/getting-started-llvm-c-api/blob/master/sum.c
# https://github.com/benbjohnson/llvm-c-kaleidoscope/tree/master/src

# TODO: Fix AST: use Malloc and only pointers to structs -remove all tables of AST nodes, conduct semantic checking at code generation
# TODO: Pass around a scope hash map (of Identifier (not a pointer) -> LLVMValueRef)

CC = gcc
CXX = clang++
CFLAGS = #-g -Wall -Wextra -Wno-self-assign -std=c99
YFLAGS = #-Wcounterexamples
LLVM_CC_FLAGS = `llvm-config --cflags`
LLVM_LINK_FLAGS = `llvm-config --libs --cflags --ldflags core analysis executionengine interpreter native bitwriter --system-libs`

TARGET = main

# Directory structure
SRC_DIR = src
BUILD_DIR = build
LIBS = lib

# Get all object and source files
SOURCES = $(wildcard $(SRC_DIR)/*.c)
OBJECTS = $(subst $(SRC_DIR),$(BUILD_DIR),$(SOURCES:.c=.o))

all: $(TARGET)

# Makes excecutable with object files
$(TARGET): $(BUILD_DIR)/parser.o $(BUILD_DIR)/lexer.o $(OBJECTS)
	$(CXX) $(LLVM_LINK_FLAGS) $^ -o $@

# Makes object file with source file, and build directory
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c $(BUILD_DIR)
	$(CC) $(LLVM_CC_FLAGS) $(CFLAGS) -I$(LIBS) $< -c -o $@

# Create Lex output code
$(SRC_DIR)/lexer.c: $(BUILD_DIR) $(SRC_DIR)/parser.c
	lex -o $@ $(SRC_DIR)/lexer.l

# Create Bison output code
$(SRC_DIR)/parser.c: $(BUILD_DIR)
	yacc -d $(SRC_DIR)/parser.y -o $@ $(YFLAGS)

# Create build directory (if not already present)
$(BUILD_DIR):
	mkdir $@

# Remove build files and compiled target file
.PHONY: clean
clean:
	rm -rf ${BUILD_DIR}/*
	rm -f $(SRC_DIR)/parser.h
	rm -f $(SRC_DIR)/parser.c
	#rm -f $(SRC_DIR)/lexer.h
	rm -f $(SRC_DIR)/lexer.c
	rm $(TARGET)