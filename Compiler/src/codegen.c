#include "codegen.h"

/*
 * Generates machine code output from file given first Statment in AST, name of source file and output file.
 */
void code_gen(struct Statement* statements, char* source_name, char* out_name) {
    // Initilize LLVM objects
    LLVMModuleRef module = LLVMModuleCreateWithName(source_name);
    LLVMBuilderRef builder = LLVMCreateBuilder();
    LLVMExecutionEngineRef engine;
    
    LLVMInitializeNativeAsmPrinter();
    LLVMInitializeNativeAsmParser();
    LLVMInitializeNativeTarget();
    LLVMLinkInMCJIT();

    // Create execution engine.
    char* error;
    if(LLVMCreateExecutionEngineForModule(&engine, module, &error) == 1) {
        fprintf(stderr, "%s\n", error);
        LLVMDisposeMessage(error);
        exit(1);
    }

    // Build all statements in module
    struct Statement* statement = statements;
    LLVMValueRef main;
    while (statement != NULL) {

        switch (statement->type) {
            case SUBROUTINE:
                // Create subroutine
                main = create_subroutine(module, builder, statement->statement.subroutine);
                break;
            // TODO: Add global variable declarations/assignments
            default:
                // Error

        }

        statement = statement->next;
    }

    // Write machine code to file
    if (LLVMWriteBitcodeToFile(module, out_name) != 0) {
        fprintf(stderr, "Error writing machine code to file, skipping.\n");
    }

    // Print LLVM code to output
    LLVMDumpModule(module);
    
    // Dispose
    LLVMDisposeModule(module);
    LLVMDisposeBuilder(builder);
}

/*
 * Creates a subroutine, given a LLVM module and the Subroutine.
 * Returns refrence to label of subroutine.
 */
LLVMValueRef create_subroutine(LLVMModuleRef mod, LLVMBuilderRef builder,
    struct Subroutine subroutine) {

    // Create subroutine label
    LLVMValueRef label = LLVMAddFunction(mod, subroutine.identifier->name,
        get_type(subroutine.identifier->type));

    // Create body block of subroutine
    LLVMBasicBlockRef entry = LLVMAppendBasicBlock(label, "entry");
    LLVMPositionBuilderAtEnd(builder, entry);

    // Build subroutine body
    struct Statement* statement = subroutine.body;
    bool returned = false;
    while (statement != NULL) {

        switch (statement->type) {
            case SUBROUTINE_RETURN:
                // TODO: Add checking for returning expression of inappropriate type
                if (statement->statement.expression == NULL) {
                    // Return from void subroutine
                    LLVMBuildRetVoid(builder);
                } else {
                    // Return value from subroutine
                    LLVMBuildRet(builder, create_expression(*statement->statement.expression));
                }
                returned = true;
                break;
            // TODO: Add nested subroutines
            // TODO: Add local variable declarations/assignments
        }

        statement = statement->next;
    }

    // Add default return if no return
    if (!returned) {
        LLVMBuildRetVoid(builder);
    }

    return label;
}

/*
 * Converts expression to LLVM value.
 * (Beware of case when expression pointer points to NULL).
 */
LLVMValueRef create_expression(struct Expression expression) {
    // Determine type of expression
    switch (expression.type) {
        case SUBROUTINE_CALL:
            // TODO: Add subroutine call
            return NULL;
        case BINARY_OPERATION:
            // TODO: Add binary operations
            return NULL;
        case UNARY_OPERATION:
            // TODO: Add unary operation
            return NULL;
        case VARIABLE:
            // TODO: Add variable
            return NULL;
        case LITTERAL:
            // Determine type of litteral
            switch (expression.expression.litteral->type) {
                case P_LONG:
                    return LLVMConstInt(LLVMInt64Type(), expression.expression.litteral->value.l_long, 1);
                case P_INT:
                    return LLVMConstInt(LLVMInt32Type(), expression.expression.litteral->value.l_long, 1);
                case P_SHORT:
                    return LLVMConstInt(LLVMInt16Type(), expression.expression.litteral->value.l_long, 1);
                case P_DOUBLE:
                    return LLVMConstReal(LLVMDoubleType(), expression.expression.litteral->value.l_double);
                case P_FLOAT:
                    return LLVMConstReal(LLVMFloatType(), expression.expression.litteral->value.l_double);
                case P_BOOL:
                    return LLVMConstInt(LLVMInt1Type(), expression.expression.litteral->value.l_long, 0);
                case P_CHAR:
                    return LLVMConstInt(LLVMInt8Type(), (long) expression.expression.litteral->value.l_char, 0);
                // TODO: Add string litteral
            }
    }
}

/*
 * Converts a DataType struct to a LLVM type.
 */
LLVMTypeRef get_type(struct DataType* type) {
    // Handle NULL type
    if (type == NULL) return LLVMVoidType();

    switch (type->type) {
        // Handle primitive types
        case PRIMITIVE:
            switch (type->data_type.primitive) {
                case P_LONG:
                    return LLVMInt64Type();
                    break;
                case P_INT:
                    return LLVMInt32Type();
                    break;
                case P_SHORT:
                    return LLVMInt16Type();
                    break;
                case P_DOUBLE:
                    return LLVMDoubleType();
                    break;
                case P_FLOAT:
                    return LLVMFloatType();
                    break;
                case P_BOOL:
                    return LLVMInt1Type();
                    break;
                case P_CHAR:
                    return LLVMInt8Type();
                /* TODO: Add P_STRING */
            }
        case SUBROUTINE_TYPE:
            // Get parameter types
            LLVMTypeRef param_types[MAX_PARAMS];
            for (int i = 0; i < type->data_type.subroutine.parameter_size; i++) {
                param_types[i] = get_type(
                    type->data_type.subroutine.parameters[i]->type);
            }

            // Create subroutine type
            return LLVMFunctionType(get_type(type->data_type.subroutine.return_type),
                param_types, type->data_type.subroutine.parameter_size, 0);
    }
}