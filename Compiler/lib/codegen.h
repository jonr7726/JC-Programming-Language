#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#include <llvm-c/Core.h>
#include <llvm-c/ExecutionEngine.h>
#include <llvm-c/Target.h>
#include <llvm-c/Analysis.h>
#include <llvm-c/BitWriter.h>

#include "ast_structure.h"

/* Creates LLVM module from file given first Statment in AST and name of file. */
LLVMModuleRef create_module(struct Statement* statements, char* file_name)

/* Creates a subroutine, given a LLVM module and a Statement of type SUBROUTINE. */
void create_subroutine(struct Subroutine* subroutine);