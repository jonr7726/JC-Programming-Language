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
 * Generates machine code output from file given first Statment in AST, name of source file and output file.
 */
void code_gen(struct Statement* statements, char* source_name, char* out_name);

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
LLVMValueRef create_expression(struct Expression expression);

/*
 * Converts a DataType struct to a LLVM type.
 */
LLVMTypeRef get_type(struct DataType* type);