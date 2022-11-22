#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#include <llvm-c/Core.h>
#include <llvm-c/DataTypes.h>
#include <llvm-c/ExecutionEngine.h>
#include <llvm-c/Target.h>
#include <llvm-c/Analysis.h>
#include <llvm-c/BitWriter.h>

#include "ast_structure.h"

typedef struct Symbol* SymbolTable;

/*
 * Linked list of symbol table within any given scope
 */
struct Symbol {
    char* identifier;
    DataType* data_type;
    LLVMValueRef refrence;
    SymbolTable next; // Next in linked list, or NULL
};

/*
 * Generates machine code output from file given first Statment in AST, name of source file and output file.
 */
void code_gen(Node* first, char* source_name, char* out_name);

/*
 * Creates a subroutine, given a LLVM module and the Subroutine.
 * Returns refrence to label of subroutine.
 */
LLVMValueRef create_subroutine(SymbolTable globalScope, LLVMModuleRef mod,
    LLVMBuilderRef builder, struct Subroutine subroutine);

/*
 * Converts expression to LLVM value.
 * (Beware of case when expression pointer points to NULL).
 */
LLVMValueRef create_expression(LLVMBuilderRef builder, SymbolTable globalScope,
    SymbolTable localScope, SymbolTable parameters, Expression* expression);

/*
 * Converts a DataType struct to a LLVM type.
 */
LLVMTypeRef get_type(DataType* data_type);

/*
 * Adds symbol to symbol table.
 */
void add_symbol(SymbolTable* scope, SymbolTable symbol);

/*
 * Retrieves symbol from symbol table given it's identifier.
 * Returns NULL if not present
 */
SymbolTable get_symbol(SymbolTable scope, char* identifier);