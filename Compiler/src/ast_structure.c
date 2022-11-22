#include "ast_structure.h"

/*
 * Creates a new node in dynamic memory and returns pointer to it.
 */
Node* create_declaration_node(char* identifier, DataType* data_type) {
    Node* node = (Node*) malloc(sizeof(Node));
    node->type = N_DECLARATION;
    node->node.declaration.identifier = identifier;
    node->node.declaration.data_type = data_type;
    node->next = NULL;
    return node;
}

/*
 * Creates a new node in dynamic memory and returns pointer to it.
 */
Node* create_assignment_node(char* identifier, Expression* expression) {
    Node* node = (Node*) malloc(sizeof(Node));
    node->type = N_ASSIGNMENT;
    node->node.assignment.identifier = identifier;
    node->node.assignment.expression = expression;
    node->next = NULL;
    return node;
}

/*
 * Creates a new node in dynamic memory and returns pointer to it.
 */
Node* create_expression_node(Expression* expression) {
    Node* node = (Node*) malloc(sizeof(Node));
    node->type = N_EXPRESSION;
    node->node.expression = expression;
    node->next = NULL;
    return node;
}

/*
 * Creates a new node in dynamic memory and returns pointer to it.
 */
Node* create_subroutine_node(char* identifier, char** param_identifiers,
    DataType* data_type, Node* body) {

    Node* node = (Node*) malloc(sizeof(Node));
    node->type = N_SUBROUTINE;
    node->node.subroutine.identifier = identifier;
    node->node.subroutine.param_identifiers = param_identifiers;
    node->node.subroutine.data_type = data_type;
    node->node.subroutine.body = body;
    node->next = NULL;
    return node;
}

/*
 * Creates a new node in dynamic memory and returns pointer to it.
 */
Node* create_return_node(Expression* expression) {
    Node* node = (Node*) malloc(sizeof(Node));
    node->type = N_RETURN;
    node->node.expression = expression;
    node->next = NULL;
    return node;
}

/*
 * Creates a new expression in dynamic memory and returns pointer to it.
 */
Expression* create_subroutine_call(char* identifier, Expression** params, int param_size) {
    Expression* expression = (Expression*) malloc(sizeof(Expression));
    expression->type = E_SUBROUTINE_CALL;
    expression->expression.subroutine_call.identifier = identifier;
    expression->expression.subroutine_call.params = params;
    expression->expression.subroutine_call.param_size = param_size;
    return expression;
}

/*
 * Creates a new expression in dynamic memory and returns pointer to it.
 */
Expression* create_operation(enum OperationType operation, Expression* lhs, Expression* rhs) {
    Expression* expression = (Expression*) malloc(sizeof(Expression));
    expression->type = E_OPERATION;
    expression->expression.operation.type = operation;
    expression->expression.operation.lhs = lhs;
    expression->expression.operation.rhs = rhs;
    return expression;
}

/*
 * Creates a new expression in dynamic memory and returns pointer to it.
 */
Expression* create_litteral(enum PrimitiveDataType type, uint8_t radix, char* value) {
    Expression* expression = (Expression*) malloc(sizeof(Expression));
    expression->type = E_LITTERAL;
    expression->expression.litteral.type = type;
    expression->expression.litteral.radix = radix;
    expression->expression.litteral.value = value;
    return expression;
}

/*
 * Creates a new expression in dynamic memory and returns pointer to it.
 */
Expression* create_variable(char* identifier) {
    Expression* expression = (Expression*) malloc(sizeof(Expression));
    expression->type = E_VARIABLE;
    expression->expression.identifier = identifier;
    return expression;
}

/*
 * Creates a new DataType in dynamic memory and returns pointer to it.
 */
DataType* create_primitive_data_type(enum PrimitiveDataType type) {
    DataType* data_type = (DataType*) malloc(sizeof(DataType));
    data_type->type = T_PRIMITIVE;
    data_type->data_type.primitive = type;
    return data_type;
}

/*
 * Creates a new DataType in dynamic memory and returns pointer to it.
 */
DataType* create_subroutine_data_type(DataType** param_data_types, int param_size,
    DataType* return_type) {

    DataType* data_type = (DataType*) malloc(sizeof(DataType));
    data_type->type = T_SUBROUTINE;
    data_type->data_type.subroutine.param_data_types = param_data_types;
    data_type->data_type.subroutine.param_size = param_size;
    data_type->data_type.subroutine.return_type = return_type;
    return data_type;
}

/*
 * Deallocates memory from node and all expressions and datatypes within it.
 */
void free_node(Node* node) {
    // Note, we do not free datatypes of identifiers being declared as they are used by symbol tables
    switch (node->type) {
        case N_RETURN:
            if (node->node.expression == NULL) break;
        case N_EXPRESSION:
            free_expression(node->node.expression);
            break;

        case N_ASSIGNMENT:
            free_expression(node->node.assignment.expression);
            break;

        case N_SUBROUTINE:
            free(node->node.subroutine.param_identifiers);
            // Note we do not free body nodes for subroutines as this will already have been done
    }
    free(node);
}

/*
 * Deallocates memory from expression and all expressions and datatypes within it.
 */
void free_expression(Expression* expression) {
    switch (expression->type) {
        case E_SUBROUTINE_CALL:
            if (expression->expression.subroutine_call.param_size > 0) {
                for (int i = 0; i < expression->expression.subroutine_call.param_size; i++) {
                    free(expression->expression.subroutine_call.params[i]);
                }
                free(expression->expression.subroutine_call.params);
            }
            break;
        case E_OPERATION:
            if (expression->expression.operation.lhs != NULL) {
                free_expression(expression->expression.operation.lhs);
            }
            if (expression->expression.operation.rhs != NULL) {
                free_expression(expression->expression.operation.rhs);
            }
    }
    free(expression);
}

/*
 * Deallocates memory from datatype and all datatypes within it.
 */
void free_data_type(DataType* data_type) {
    if (data_type->type == T_SUBROUTINE) {
        free(data_type->data_type.subroutine.return_type);
        if (data_type->data_type.subroutine.param_size > 0) {
            for (int i = 0; i < data_type->data_type.subroutine.param_size; i++) {
                free(data_type->data_type.subroutine.param_data_types[i]);
            }
            free(data_type->data_type.subroutine.param_data_types);
        }
    }
    free(data_type);
}