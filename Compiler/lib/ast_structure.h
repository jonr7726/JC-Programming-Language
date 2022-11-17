#ifndef AST_STRUCTURE_H
#define AST_STRUCTURE_H

#define MAX_PARAMS 5

struct Statement;
struct Declaration;
struct Assignement;

struct Expression;
struct SubroutineCall;
struct BinaryOperation;
struct UnaryOperation;
struct Identifier;
struct Litteral;

struct DataType;

/* Statement node in AST; umbrella for every valid line of code. */
struct Statement {
    enum StatementType {
        DECLARATION,
        ASSIGNMENT,
        EXPRESSION,
        SUBROUTINE,
        SUBROUTINE_RETURN
    } type; // Type of the statement
    union Statements {
        /* Declaration of an identifier. */
        struct Declaration {
            struct Identifier* identifier;
        } declaration;
        /* (Re)assignment of an identifier. */
        struct VarAssignement {
            struct Identifier* identifier;
            struct Expression* expression;
        } assignment;
        /* Expression (used for calling subroutines, also used when returning expression) */
        struct Expression* expression;
        /* Subroutine definition */
        struct Subroutine {
            struct Identifier* identifier;
            struct Statement* body;
        } subroutine;
    } statement; // Statement (use type to determine which in union to use)
    struct Statement* next; // Next statement (or null pointer)
};

/* Umbrella for everything that will resolve to a value at run time. */
struct Expression {
    enum ExpressionType {
        SUBROUTINE_CALL,
        BINARY_OPERATION,
        UNARY_OPERATION,
        VARIABLE,
        LITTERAL
    } type; // Type of the expression
    union Expressions {
        struct SubroutineCall {
            struct Identifier* subroutine; // Subroutine identifier
            struct Expression* parameters[MAX_PARAMS]; // Parameters
            int parameter_size; // Number of parameters
        } subroutine_call;
        struct BinaryOperation {
            struct Expression* lhs; // Left hand side expression
            struct Expression* rhs; // Right hand side expression
            enum BinaryOperationType { 
                O_ADD,
                O_SUBTRACT
            } type; // Operation
        } binary_operation;
        struct UnaryOperation {
            struct Expression* operand; // Expression
            enum UnaryOperationType {
                O_COMPLEMENT
            } type; // Operation
        } unary_operation;
        struct Identifier* variable;
        struct Litteral* litteral;
    } expression; // Expression (use type to determine which in union to use)
    struct DataType* data_type; // Data type the expression resolves to
};

/* Identifier (variables, subroutines, etc.). */
struct Identifier { 
    char* name;
    struct DataType* type;
};

/* Primitive data type */
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

/* Litteral value (expression). */
struct Litteral { 
    enum PrimitiveDataType type; // Type of the litteral
    union Value {
        long l_long;
        double l_double;
        char l_char;
        char* l_string;
    } value; // Value of the litteral (use type to determine which in union to use)
};

/*
 * Data type to represent both primitive and
 * more complex data types (i.e. subroutines).
 */
struct DataType {
    enum Type {
        PRIMITIVE,
        SUBROUTINE_TYPE
    } type; // Type of the datatype
    union DataTypes {
        /* Primitive data type */
        enum PrimitiveDataType primitive;

        /* Subroutine data type */
        struct SubroutineDataType {
            struct Identifier* parameters[MAX_PARAMS];
            int parameter_size;
            struct DataType* return_type;
        } subroutine;
    } data_type; // Datatype (use type to determine which in union to use)
};

#endif