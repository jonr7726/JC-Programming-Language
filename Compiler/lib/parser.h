#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdio.h>

#include "error.h"
#include "ast_structure.h"

#define MAX_IDENTIFIERS 50
#define MAX_EXPRESSIONS 50
#define MAX_LITTERALS 50
#define MAX_STATEMENTS 50

/*
 * Stores identifier in litteral table at current index (if it does not already exist).
 * v_type is the litteral value union type.
 * l_type is the litteral type enum.
 * value is the value of the litteral.
 * store is where to to store the refrence to the litteral
 */
#define store_litteral(v_type, l_type, value, store) \
    /* See if exists already */\
    bool found = false;\
    for (int i = 0; i < litteral_table_size; i++) {\
        if (litteral_table[i].type == l_type) {\
            if (litteral_table[i].value.v_type == value) {\
                store = &litteral_table[i];\
                found = true;\
            }\
        }\
    }\
    if (!found) {\
        /* Add to table */\
        litteral_table[litteral_table_size].type = l_type;\
        litteral_table[litteral_table_size].value.v_type = value;\
        store = &litteral_table[litteral_table_size++];\
    }

extern void yyerror();
extern int yylex();
extern char* yytext;
extern int yylineno;

void print_symbol_table();
void print_litteral_table();
void print_ast();

/* All statements for code generation. */
struct Statement statements[MAX_STATEMENTS];
int statements_size = 0;

/* Identifier symbol table. */
struct Identifier symbol_table[MAX_IDENTIFIERS];
int symbol_table_size = 0;

/* Table of all litteral values (other than booleans). */
struct Litteral litteral_table[MAX_LITTERALS];
int litteral_table_size = 0;

/* Place to store all non-primitive data type structures. */
struct DataType data_types[MAX_IDENTIFIERS];
int data_types_size = 0;

/* Place to store all expressions. */
struct Expression expressions[MAX_EXPRESSIONS];
int expressions_size = 0;

// Initialize boolean litteral values
struct Litteral true_litteral = (struct Litteral) { .type = P_CHAR, .value.l_char = 1 };
struct Litteral false_litteral = (struct Litteral) { .type = P_CHAR, .value.l_char = 0 };

// Initialize primitive data types
struct DataType long_data_type = (struct DataType) { .type = PRIMITIVE, .data_type.primitive = P_LONG };
struct DataType int_data_type = (struct DataType) { .type = PRIMITIVE, .data_type.primitive = P_INT };
struct DataType short_data_type = (struct DataType) { .type = PRIMITIVE, .data_type.primitive = P_SHORT };
struct DataType double_data_type = (struct DataType) { .type = PRIMITIVE, .data_type.primitive = P_DOUBLE };
struct DataType float_data_type = (struct DataType) { .type = PRIMITIVE, .data_type.primitive = P_FLOAT };
struct DataType bool_data_type = (struct DataType) { .type = PRIMITIVE, .data_type.primitive = P_BOOL };
struct DataType char_data_type = (struct DataType) { .type = PRIMITIVE, .data_type.primitive = P_CHAR };
struct DataType string_data_type = (struct DataType) { .type = PRIMITIVE, .data_type.primitive = P_STRING };

/* Returns whether identifier name is already in symbol table. */
bool identifier_declared(char* name) {
    for (int i = 0; i < symbol_table_size; i++) {
        if (strcmp(name, symbol_table[i].name) == 0) {
            return true;
        }
    }
    return false;
}

/* Returns identifier in symbol table by name. */
struct Identifier* get_identifier(char* name) {
    for (int i = 0; i < symbol_table_size; i++) {
        if (strcmp(name, symbol_table[i].name) == 0) {
            return &symbol_table[i];
        }
    }
    return NULL;
}

/* Returns last statement in linked list. */
struct Statement* get_last_statment(struct Statement* statement) {
    while (statement->next != NULL) {
        statement = statement->next;
    }
    return statement;
}

struct DataType* get_litteral_type(struct Litteral* litteral) {
    switch (litteral->type) {
        case P_LONG:
            return &long_data_type;
        case P_INT:
            return &int_data_type;
        case P_SHORT:
            return &short_data_type;
        case P_DOUBLE:
            return &double_data_type;
        case P_FLOAT:
            return &float_data_type;
        case P_BOOL:
            return &bool_data_type;
        case P_CHAR:
            return &char_data_type;
        case P_STRING:
            return &string_data_type;
    }
}

/* Converts a data type to a string and stores it at buffer. */
void type_to_string(char* buffer, struct DataType* type) {
    // Get type as string
    switch (type->type) {
        case PRIMITIVE:
            // Get primitive data type as string
            switch (type->data_type.primitive) {
                case P_LONG:
                    strcpy(buffer, "Long");
                    break;
                case P_INT:
                    strcpy(buffer, "Int");
                    break;
                case P_SHORT:
                    strcpy(buffer, "Short");
                    break;
                case P_DOUBLE:
                    strcpy(buffer, "Double");
                    break;
                case P_FLOAT:
                    strcpy(buffer, "Float");
                    break;
                case P_BOOL:
                    strcpy(buffer, "Bool");
                    break;
                case P_CHAR:
                    strcpy(buffer, "Char");
                    break;
                case P_STRING:
                    strcpy(buffer, "String");
                    break;
                default:
                    strcpy(buffer, "Void");
            }
            break;
        case SUBROUTINE:
            // Get parameters recursively
            char parameters[MAX_PARAMS * 50];
            for (int i = 0; i < type->data_type.subroutine.parameter_size; i++) {
                type_to_string(parameters + strlen(parameters),
                    type->data_type.subroutine.parameters[i]->type);
                if (i < type->data_type.subroutine.parameter_size - 1) {
                    // Add parameter seperator
                    sprintf(parameters + strlen(parameters), ", ");
                }
            }

            // Get return type recursively
            char return_type[50];
            type_to_string(return_type,
                type->data_type.subroutine.return_type);

            // Get subroutine information as string
            sprintf(buffer, "(%s) -> %s", parameters, return_type);
    }
}