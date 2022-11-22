#include "codegen.h"

/*
 * Generates machine code output from file given first Statment in AST, name of source file and output file.
 */
void code_gen(Node* node, char* source_name, char* out_name) {
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
    LLVMValueRef main;
    while (node != NULL) {

        switch (node->type) {
            case N_SUBROUTINE:
                // Create subroutine
                main = create_subroutine(module, builder, node->node.subroutine);
                break;
            // TODO: Add global variable declarations/assignments
            default:
                printf("ERROR, NOT IMPLEMENTED\n");

        }

        // Deallocate memory to node
        Node* next = node->next;
        free_node(node);
        node = next;
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
    LLVMValueRef label = LLVMAddFunction(mod, subroutine.identifier,
        get_type(subroutine.data_type));

    // Create body block of subroutine
    LLVMBasicBlockRef entry = LLVMAppendBasicBlock(label, "entry");
    LLVMPositionBuilderAtEnd(builder, entry);

    // Build subroutine body
    Node* node = subroutine.body;
    bool returned = false;
    while (node != NULL) {

        switch (node->type) {
            case N_RETURN:
                // TODO: Add checking for returning expression of inappropriate type
                if (node->node.expression == NULL) {
                    // Return from void subroutine
                    LLVMBuildRetVoid(builder);
                } else {
                    // Return value from subroutine
                    LLVMBuildRet(builder, create_expression(*node->node.expression));
                }
                returned = true;
                break;
            // TODO: Add nested subroutines
            // TODO: Add local variable declarations/assignments
        }

        // Deallocate memory to node
        Node* next = node->next;
        free_node(node);
        node = next;
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
LLVMValueRef create_expression(/*struct Identifier* scope, */Expression expression) {
    // Determine type of expression
    switch (expression.type) {
        case E_SUBROUTINE_CALL:
            // TODO: Add subroutine call
            return NULL;
        case E_OPERATION:
            // TODO: Add operations
            return NULL;
        case E_VARIABLE:
            // TODO: Add variable
            return NULL;
        case E_LITTERAL:
            // Determine type of litteral
            switch (expression.expression.litteral.type) {
                case P_LONG:
                    return LLVMConstIntOfString(LLVMInt64Type(), expression.expression.litteral.value, 10);
                case P_INT:
                    return LLVMConstIntOfString(LLVMInt32Type(), expression.expression.litteral.value, 10);
                case P_SHORT:
                    return LLVMConstIntOfString(LLVMInt16Type(), expression.expression.litteral.value, 10);
                case P_DOUBLE:
                    return LLVMConstRealOfString(LLVMDoubleType(), expression.expression.litteral.value);
                case P_FLOAT:
                    return LLVMConstRealOfString(LLVMFloatType(), expression.expression.litteral.value);
                /*case P_BOOL:
                    return LLVMConstInt(LLVMInt1Type(), expression.expression.litteral.value.l_long, 0);
                case P_CHAR:
                    return LLVMConstInt(LLVMInt8Type(), (long) expression.expression.litteral.value.l_char, 0);*/
                // TODO: Add string, bool and char litterals
            }
    }
}

/*
 * Converts a DataType struct to a LLVM type.
 */
LLVMTypeRef get_type(/*struct Identifier* scope, */DataType* data_type) {
    // Handle NULL type
    if (data_type == NULL) return LLVMVoidType();

    switch (data_type->type) {
        // Handle primitive types
        case T_PRIMITIVE:
            switch (data_type->data_type.primitive) {
                case P_LONG:
                    return LLVMInt64Type();
                case P_INT:
                    return LLVMInt32Type();
                case P_SHORT:
                    return LLVMInt16Type();
                case P_DOUBLE:
                    return LLVMDoubleType();
                case P_FLOAT:
                    return LLVMFloatType();
                case P_BOOL:
                    return LLVMInt1Type();
                case P_CHAR:
                    return LLVMInt8Type();
                /* TODO: Add P_STRING */
            }
        case T_SUBROUTINE:
            // Get parameter types
            LLVMTypeRef* param_data_types = calloc(data_type->data_type.subroutine.param_size, sizeof(LLVMTypeRef));
            for (int i = 0; i < data_type->data_type.subroutine.param_size; i++) {
                param_data_types[i] = get_type(
                    data_type->data_type.subroutine.param_data_types[i]);
            }

            // Create subroutine type
            return LLVMFunctionType(get_type(data_type->data_type.subroutine.return_type),
                param_data_types, data_type->data_type.subroutine.param_size, 0);
    }
}