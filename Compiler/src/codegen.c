#include "codegen.h"

/*
 * Creates LLVM module from file given first Statment in AST and name of file.
 * Returns refrence to module.
 */
LLVMModuleRef create_module(struct Statement* statements, char* file_name) {
    // Create module
    LLVMModuleRef mod = LLVMModuleCreateWithName("module");

    // Build all statements in module
    struct Statement* statement = statements;
    while (statement != NULL) {

        switch (statement->type) {
            case SUBROUTINE:
                // Create subroutine
                create_subroutine(mod, statement->statement.subroutine)
                break;
            // TODO: Add global variable declarations/assignments
            default:
                // Error

        }

        statement = statement->next;
    }
}

/*
 * Creates a subroutine, given a LLVM module and the Subroutine.
 * Returns refrence to label of subroutine.
 */
LLVMValueRef create_subroutine(LLVMModuleRef mod, struct Subroutine subroutine) {
    // Create subroutine label
    LLVMValueRef label = LLVMAddFunction(mod, subroutine.identifier->name,
        get_type(subroutine.identifier->type));

    // Create body block of subroutine
    LLVMBasicBlockRef entry = LLVMAppendBasicBlock(label, "entry");

    // Set builder to body
    LLVMBuilderRef builder = LLVMCreateBuilder();
    LLVMPositionBuilderAtEnd(builder, entry);

    // Build subroutine body

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

int main(int argc, char const *argv[]) {
    // Create module
    LLVMModuleRef mod = LLVMModuleCreateWithName("module");

    // Create function
    LLVMBasicBlockRef entry = LLVMAppendBasicBlock(sum, "entry");

    // Create builder
    LLVMBuilderRef builder = LLVMCreateBuilder();
    LLVMPositionBuilderAtEnd(builder, entry);

    LLVMTypeRef param_types[] = { LLVMInt32Type(), LLVMInt32Type() };
    LLVMTypeRef ret_type = LLVMFunctionType(LLVMInt32Type(), param_types, 2, 0);
    LLVMValueRef sum = LLVMAddFunction(mod, "sum", ret_type);

    LLVMBasicBlockRef entry = LLVMAppendBasicBlock(sum, "entry");

    LLVMBuilderRef builder = LLVMCreateBuilder();
    LLVMPositionBuilderAtEnd(builder, entry);
    LLVMValueRef tmp = LLVMBuildAdd(builder, LLVMGetParam(sum, 0), LLVMGetParam(sum, 1), "tmp");
    LLVMBuildRet(builder, tmp);

    char *error = NULL;
    LLVMVerifyModule(mod, LLVMAbortProcessAction, &error);
    LLVMDisposeMessage(error);

    LLVMExecutionEngineRef engine;
    error = NULL;
    LLVMLinkInJIT();
    LLVMInitializeNativeTarget();
    if (LLVMCreateExecutionEngineForModule(&engine, mod, &error) != 0) {
        fprintf(stderr, "failed to create execution engine\n");
        abort();
    }
    if (error) {
        fprintf(stderr, "error: %s\n", error);
        LLVMDisposeMessage(error);
        exit(EXIT_FAILURE);
    }

    if (argc < 3) {
        fprintf(stderr, "usage: %s x y\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    long long x = strtoll(argv[1], NULL, 10);
    long long y = strtoll(argv[2], NULL, 10);

    LLVMGenericValueRef args[] = {
        LLVMCreateGenericValueOfInt(LLVMInt32Type(), x, 0),
        LLVMCreateGenericValueOfInt(LLVMInt32Type(), y, 0)
    };
    LLVMGenericValueRef res = LLVMRunFunction(engine, sum, 2, args);
    printf("%d\n", (int)LLVMGenericValueToInt(res, 0));

    // Write out bitcode to file
    if (LLVMWriteBitcodeToFile(mod, "sum.bc") != 0) {
        fprintf(stderr, "error writing bitcode to file, skipping\n");
    }

    LLVMDisposeBuilder(builder);
    LLVMDisposeExecutionEngine(engine);
}