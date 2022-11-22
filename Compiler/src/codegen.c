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
    SymbolTable globalScope = NULL;
    while (node != NULL) {

        switch (node->type) {
            case N_SUBROUTINE:
                // Create subroutine
                LLVMValueRef refrence = create_subroutine(globalScope,
                    module, builder, node->node.subroutine);
                
                // Add to symbol table
                SymbolTable symbol = (SymbolTable) malloc(sizeof(struct Symbol));
                symbol->identifier = node->node.subroutine.identifier;
                symbol->data_type = node->node.subroutine.data_type;
                symbol->refrence = refrence;
                symbol->next = NULL;
                add_symbol(&globalScope, symbol);
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
LLVMValueRef create_subroutine(SymbolTable globalScope, LLVMModuleRef mod,
    LLVMBuilderRef builder, struct Subroutine subroutine) {

    // Create subroutine label
    LLVMValueRef label = LLVMAddFunction(mod, subroutine.identifier,
        get_type(subroutine.data_type));

    // Create body block of subroutine
    LLVMBasicBlockRef entry = LLVMAppendBasicBlock(label, "entry");
    LLVMPositionBuilderAtEnd(builder, entry);

    // Create local scope with parameters
    SymbolTable localScope = NULL;
    for (int i = 0; i < subroutine.data_type->data_type.subroutine.param_size; i++) {
        SymbolTable symbol = (SymbolTable) malloc(sizeof(struct Symbol));
        symbol->identifier = subroutine.param_identifiers[i];
        symbol->data_type = subroutine.data_type->data_type.subroutine.param_data_types[i];
        symbol->refrence = LLVMGetParam(label, i);
        symbol->next = NULL;
        add_symbol(&localScope, symbol);
    }

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
                    LLVMValueRef ret = create_expression(builder,
                        globalScope, localScope, node->node.expression);
                    LLVMBuildRet(builder, ret);
                }
                returned = true;
                break;
            // TODO: Add local variable declarations/assignments
            // TODO: Add nested subroutines
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
LLVMValueRef create_expression(LLVMBuilderRef builder, SymbolTable globalScope,
    SymbolTable localScope, Expression* expression) {

    SymbolTable symbol;

    // Determine type of expression
    switch (expression->type) {
        case E_SUBROUTINE_CALL:
            // TODO: Add checking for invalid subroutine calls (with types)

            // Get subroutine symbol
            symbol = get_symbol(globalScope,
                expression->expression.subroutine_call.identifier);

            if (symbol == NULL) {
                printf("Error, could not find subroutine identifier\n");
                exit(1);
            }

            // Create argument expressions
            LLVMValueRef* args = (LLVMValueRef*) calloc(
                expression->expression.subroutine_call.param_size,
                sizeof(LLVMValueRef)
            );
            for (int i = 0; i < expression->expression.subroutine_call.param_size; i++) {
                args[i] = create_expression(builder, globalScope, localScope,
                    expression->expression.subroutine_call.params[i]);
            }

            // Create subroutine call
            return LLVMBuildCall2(
                builder,
                get_type(symbol->data_type),
                symbol->refrence,
                args,
                expression->expression.subroutine_call.param_size,
                expression->expression.subroutine_call.identifier
            );
        case E_OPERATION:
            // TODO: Add operations
            return NULL;
        case E_VARIABLE:
            // TODO: Add checks for variable types

            // Get variable symbol
            symbol = get_symbol(localScope,
                expression->expression.identifier);

            if (symbol == NULL) {
                printf("Error, could not find variable identifier\n");
                exit(1);
            }

            return symbol->refrence;
        case E_LITTERAL:
            // Determine type of litteral
            switch (expression->expression.litteral.type) {
                case P_LONG:
                    return LLVMConstIntOfString(LLVMInt64Type(),
                        expression->expression.litteral.value, 10);
                case P_INT:
                    return LLVMConstIntOfString(LLVMInt32Type(),
                        expression->expression.litteral.value, 10);
                case P_SHORT:
                    return LLVMConstIntOfString(LLVMInt16Type(),
                        expression->expression.litteral.value, 10);
                case P_DOUBLE:
                    return LLVMConstRealOfString(LLVMDoubleType(),
                        expression->expression.litteral.value);
                case P_FLOAT:
                    return LLVMConstRealOfString(LLVMFloatType(),
                        expression->expression.litteral.value);
                /*case P_BOOL:
                    return LLVMConstInt(LLVMInt1Type(),
                        expression->expression.litteral.value.l_long, 0);
                case P_CHAR:
                    return LLVMConstInt(LLVMInt8Type(),
                        (long) expression->expression.litteral.value.l_char, 0);*/
                // TODO: Add string, bool and char litterals
            }
    }
}

/*
 * Converts a DataType struct to a LLVM type.
 */
LLVMTypeRef get_type(DataType* data_type) {
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
            LLVMTypeRef* param_data_types = calloc(
                data_type->data_type.subroutine.param_size,
                sizeof(LLVMTypeRef)
            );
            for (int i = 0; i < data_type->data_type.subroutine.param_size; i++) {
                param_data_types[i] = get_type(
                    data_type->data_type.subroutine.param_data_types[i]);
            }

            // Create subroutine type
            return LLVMFunctionType(
                get_type(data_type->data_type.subroutine.return_type),
                param_data_types,
                data_type->data_type.subroutine.param_size,
                0
            );
    }
}

/*
 * Adds symbol to symbol table.
 */
void add_symbol(SymbolTable* scope, SymbolTable symbol) {
    if (*scope == NULL) {
        // Add to first element of symbol table
        *scope = symbol;
    } else {
        // Add to end of symbol table
        SymbolTable last = *scope;
        GET_LAST(last)->next = symbol;
    }
}

/*
 * Retrieves symbol from symbol table given it's identifier.
 * Returns NULL if not present
 */
SymbolTable get_symbol(SymbolTable scope, char* identifier) {
    while (scope != NULL) {
        // Attempt to match identifier
        if (!strcmp(scope->identifier, identifier)) return scope;
        scope = scope->next;
    }
    // Could not find symbol
    return NULL;
}