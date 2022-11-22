#ifndef AST_STRUCTURE_H
#define AST_STRUCTURE_H

#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>

typedef struct Nodes Node;
typedef struct Expressions Expression;
typedef struct DataTypes DataType;
typedef struct Declarations Declaration;

typedef struct DeclarationLists DeclarationList;
typedef struct ExpressionLists ExpressionList;

/*
 * Primitive data types allowed.
 */
enum PrimitiveDataType {
    P_LONG,
    P_INT,
    P_SHORT,
    P_DOUBLE,
    P_FLOAT,
    P_BOOL,
    P_CHAR,
    P_STRING
};

/*
 * Node in AST, includes statements, subroutines, control structures, etc.
 */
struct Nodes {
    enum NodeType {
        N_DECLARATION,
        N_ASSIGNMENT,
        N_EXPRESSION,
        N_SUBROUTINE,
        N_RETURN
    } type; // Type of the node

    union NodeTypes {
        /* Declaration of a identifier. */
        struct Declaration {
            char* identifier;
            DataType* data_type;
        } declaration;

        /* (Re)assignment of an identifier. */
        struct Assignement {
            char* identifier;
            Expression* expression;
        } assignment;

        /* Expression (used for calling subroutines, also used when returning expression) */
        Expression* expression;

        /* Subroutine definition */
        struct Subroutine {
            char* identifier;
            char** param_identifiers; // Array of identifier strings
            DataType* data_type; // (Contains return type, and parameter types and number of parameters)
            Node* body; // First statement of body
        } subroutine;
    } node; // (Use type to determine which in union to use)
    Node* next; // Next statement in linked list (or null pointer)
};

/*
 * Umbrella for everything that will resolve to a value at run time.
 */
struct Expressions {
    enum ExpressionType {
        E_SUBROUTINE_CALL,
        E_OPERATION,
        E_LITTERAL,
        E_VARIABLE
    } type; // Type of the expression

    union ExpressionTypes {
        struct SubroutineCall {
            char* identifier; // Subroutine to call
            Expression** params; // Array of Parameters to pass in
            int param_size; // Number of parameters
        } subroutine_call;

        struct Operation {
            enum OperationType { 
                O_ADD,
                O_SUBTRACT,
                O_COMPLEMENT
            } type; // Operator
            Expression* lhs; // Left hand side of operator
            Expression* rhs; // Right hand side of operator
        } operation;

        struct Litteral {
            enum PrimitiveDataType type;
            uint8_t radix; // Base of litteral (if integer)
            char* value; // Value of the litteral (use type to determine which in union to use)
        } litteral;

        char* identifier; // For variable refrence
    } expression; // Expression (use type to determine which in union to use)
};

/*
 * Data type to represent both primitive and
 * more complex data types (i.e. subroutines).
 */
struct DataTypes {
    enum DataTypeType {
        T_PRIMITIVE,
        T_SUBROUTINE
    } type; // Type of the datatype

    union DataTypeTypes {
        /* Primitive data type */
        enum PrimitiveDataType primitive;

        /* Subroutine data type */
        struct SubroutineDataType {
            DataType** param_data_types; // Array of DataType pointers
            int param_size;
            DataType* return_type;
        } subroutine;
    } data_type; // (Use type to determine which in union to use)
};

/*
 * Creates a new Node in dynamic memory and returns pointer to it.
 */
Node* create_declaration_node(char* identifier, DataType* data_type);
Node* create_assignment_node(char* identifier, Expression* expression);
Node* create_expression_node(Expression* expression);
Node* create_subroutine_node(char* identifier, char** param_identifiers,
    DataType* data_type, Node* body);
Node* create_return_node(Expression* expression);

/*
 * Creates a new Expression in dynamic memory and returns pointer to it.
 */
Expression* create_subroutine_call(char* identifier, Expression** params, int param_size);
Expression* create_operation(enum OperationType operation, Expression* lhs, Expression* rhs);
Expression* create_litteral(enum PrimitiveDataType type, uint8_t radix, char* value);
Expression* create_variable(char* identifier);

/*
 * Creates a new DataType in dynamic memory and returns pointer to it.
 */
DataType* create_primitive_data_type(enum PrimitiveDataType type);
DataType* create_subroutine_data_type(DataType** param_data_types, int param_size,
    DataType* return_type);

/*
 * Deallocates memory from struct pointer and all data within it (expressions, etc.).
 */
void free_node(Node* node);
void free_expression(Expression* expression);
void free_data_type(DataType* data_type);

#endif