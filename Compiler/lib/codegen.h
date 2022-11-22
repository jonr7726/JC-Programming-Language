#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include <llvm-c/Core.h>
#include <llvm-c/DataTypes.h>
#include <llvm-c/ExecutionEngine.h>
#include <llvm-c/Target.h>
#include <llvm-c/Analysis.h>
#include <llvm-c/BitWriter.h>

#include "ast_structure.h"

/*
 * Linked list of symbol table within any given scope
 */
struct Identifier {
    enum IdentifierType {
        I_GLOBAL,
        I_LOCAL,
        I_PARAM
    } type;
    char* identifier;
    DataType* data_type;
    LLVMValueRef refrence;
    struct Identifier* next;
};

/*
 * Generates machine code output from file given first Statment in AST, name of source file and output file.
 */
void code_gen(Node* first, char* source_name, char* out_name);

/*
 * Creates a subroutine, given a LLVM module and the Subroutine.
 * Returns refrence to label of subroutine.
 */
LLVMValueRef create_subroutine(LLVMModuleRef mod, LLVMBuilderRef builder,
    struct Subroutine subroutine);

/*
 * Converts expression to LLVM value.
 * (Beware of case when expression pointer points to NULL).
 */
LLVMValueRef create_expression(/*struct Identifier* scope, */Expression expression);

/*
 * Converts a DataType struct to a LLVM type.
 */
LLVMTypeRef get_type(/*struct Identifier* scope, */DataType* data_type);