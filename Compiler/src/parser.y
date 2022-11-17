%{
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
	void print_ast(struct Statement*, int);

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

	bool identifier_declared(char* name);
	struct Identifier* get_identifier(char* name);
	struct Statement* get_last_statment(struct Statement* statement);
	struct DataType* get_litteral_type(struct Litteral* litteral);
	void type_to_string(char* buffer, struct DataType* type);
	void print_symbol_table();
	void print_litteral_table();
	void print_ast(struct Statement* statement, int indent);

	struct Statement* first;
%}


/* Union for all the ways to can access data nodes */
%union {
	struct Statement* statement;

	struct Expression* expression;
	struct Litteral* litteral;
	struct Identifier* identifier;

	struct DataType* data_type;
	char* string;
	int token;
}


/* Terminal Symbols */
%token <token> SEMICOLON BRACKET_OPEN BRACKET_CLOSE BRACKET_CURLY_OPEN BRACKET_CURLY_CLOSE EQUALS PLUS MINUS
%token <token> INT_TYPE FLOAT_TYPE VOID_TYPE
%token <token> RETURN
%token <string> LONG_VALUE INT_VALUE SHORT_VALUE DOUBLE_VALUE FLOAT_VALUE
%token <string> IDENTIFIER

/* Non-terminal Symbols */
%type <statement> program statements
%type <statement> statement

%type <expression> expression
%type <litteral> litteral
%type <identifier> variable

%type <token> bin_operator

%type <data_type> data_type

/* Operator precedence */
%left PLUS MINUS

/* Top node of AST */
%start program

%%

program	: statements { first = $1; }
		;

statements	: statement { $$ = $1; }
			| statements statement {
				get_last_statment($1)->next = $2; // Chain next statement
				$$ = $1; // Return first in linked list
			}
			;
  
statement	: data_type IDENTIFIER SEMICOLON { // Variable eclaration
				// Ensure identifier does not already exist and has valid data type
				if (identifier_declared($2)) {
					declaration_error("Variable already declared", yylineno);
				} else if ($1 == NULL) {
					declaration_error("Variable cannot be declared as void type", yylineno);
				}
				
				// Store identifier in symbol table
				symbol_table[symbol_table_size] = (struct Identifier) {
					.name = $2,
					.type = $1
				};

				// Add statement node
				statements[statements_size] = (struct Statement) {
					.type = DECLARATION,
					.statement.declaration.identifier = &symbol_table[symbol_table_size++],
					.next = NULL
				};
				$$ = &statements[statements_size++];
			}
			| variable EQUALS expression SEMICOLON { // Variable (re)assignment
				// Ensure valid assignment data type
				if ($1->type != $3->data_type) {
					char expected[100];
					char actual[100];
					type_to_string(expected, $1->type);
					type_to_string(actual, $3->data_type);
					assignment_error(expected, actual, yylineno);
				}

				// Add statement node
				statements[statements_size] = (struct Statement) {
					.type = ASSIGNMENT,
					.statement.assignment.identifier = $1,
					.statement.assignment.expression = $3,
					.next = NULL
				};
				$$ = &statements[statements_size++];
			}
			| data_type IDENTIFIER BRACKET_OPEN BRACKET_CLOSE BRACKET_CURLY_OPEN statements BRACKET_CURLY_CLOSE { // Subroutine declaration
				// Ensure identifier does not already exist
				if (identifier_declared($2)) {
					declaration_error("Variable already declared", yylineno);
				}

				// Store parameter identifiers in symbol table
				// TODO: Add parameters

				// Create new data type for subroutine
				data_types[data_types_size] = (struct DataType) {
					.type = SUBROUTINE_TYPE,
					.data_type.subroutine = (struct SubroutineDataType) {
			            .parameter_size = 0,
			            .return_type = $1
					}
				};

				// Store subroutine identifier in symbol table
				symbol_table[symbol_table_size] = (struct Identifier) {
					.name = $2,
					.type = &data_types[data_types_size++]
				};

				// Add statement node
				statements[statements_size] = (struct Statement) {
					.type = SUBROUTINE,
					.statement.subroutine.identifier = &symbol_table[symbol_table_size++],
					.statement.subroutine.body = $6,
					.next = NULL
				};
				$$ = &statements[statements_size++];
			}
			| RETURN expression SEMICOLON { // Returning from function with value
				// Add statement node
				statements[statements_size] = (struct Statement) {
					.type = SUBROUTINE_RETURN,
					.statement.expression = $2,
					.next = NULL
				};
				$$ = &statements[statements_size++];
			}
			| RETURN SEMICOLON { // Returning from void function
				// Add statement node
				statements[statements_size] = (struct Statement) {
					.type = SUBROUTINE_RETURN,
					.statement.expression = NULL,
					.next = NULL
				};
				$$ = &statements[statements_size++];
			}
			;

expression	: variable {
				expressions[expressions_size] = (struct Expression) {
					.type = VARIABLE,
					.expression.variable = $1,
					.data_type = $1->type
				};
				$$ = &expressions[expressions_size++];
			}
			| litteral {
				expressions[expressions_size] = (struct Expression) {
					.type = LITTERAL,
					.expression.litteral = $1,
					.data_type = get_litteral_type($1)
				};
				$$ = &expressions[expressions_size++];
			}
			| expression bin_operator expression {
				;/* TODO: check operation can be perfomed on types, add expression to list */
			}
			;

variable	: IDENTIFIER {
				$$ = get_identifier($1);
				if ($$ == NULL) {
					declaration_error("Variable not declared before use", yylineno);
				}
			}
			;

data_type	: INT_TYPE { $$ = &int_data_type; }
			| FLOAT_TYPE { $$ = &float_data_type; }
			| VOID_TYPE { $$ = NULL; }
			;

bin_operator	: PLUS { $$ = $1; }
				| MINUS { $$ = $1; }
				;

litteral	: LONG_VALUE {
				long value = atol($1); // Convert to integer
				store_litteral(l_long, P_LONG, value, $$);
			}
			| INT_VALUE {
				long value = atoi($1); // Convert to integer
				store_litteral(l_long, P_INT, value, $$);
			}
			| SHORT_VALUE {
				long value = atoi($1); // Convert to integer
				store_litteral(l_long, P_SHORT, value, $$);
			}
			| DOUBLE_VALUE {
				double value = atof($1); // Convert to real
				store_litteral(l_double, P_DOUBLE, value, $$);
			}
			| FLOAT_VALUE {
				double value = atof($1); // Convert to real
				store_litteral(l_double, P_FLOAT, value, $$);
			}
			;

%%

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
    // Handle null type
    if (type == NULL) {
        strcpy(buffer, "void");
        return;
    }

    // Get type as string
    switch (type->type) {
        case PRIMITIVE:
            // Get primitive data type as string
            switch (type->data_type.primitive) {
                case P_LONG:
                    strcpy(buffer, "long");
                    break;
                case P_INT:
                    strcpy(buffer, "int");
                    break;
                case P_SHORT:
                    strcpy(buffer, "short");
                    break;
                case P_DOUBLE:
                    strcpy(buffer, "double");
                    break;
                case P_FLOAT:
                    strcpy(buffer, "float");
                    break;
                case P_BOOL:
                    strcpy(buffer, "bool");
                    break;
                case P_CHAR:
                    strcpy(buffer, "char");
                    break;
                case P_STRING:
                    strcpy(buffer, "string");
            }
            break;
        case SUBROUTINE_TYPE:
            // Get parameters recursively
            char parameters[MAX_PARAMS * 10];
            parameters[0] = 0; // Set to empty string in case no parameters exist
            for (int i = 0; i < type->data_type.subroutine.parameter_size; i++) {
                type_to_string(parameters + strlen(parameters),
                    type->data_type.subroutine.parameters[i]->type);
                if (i < type->data_type.subroutine.parameter_size - 1) {
                    // Add parameter seperator
                    sprintf(parameters + strlen(parameters), ", ");
                }
            }

            // Get return type recursively
            char return_type[10];
            type_to_string(return_type,
                type->data_type.subroutine.return_type);

            // Get subroutine information as string
            sprintf(buffer, "(%s) -> %s", parameters, return_type);
    }
}

void print_symbol_table() {
	// Print table header
	printf("SYMBOL TABLE:\n\n");
	printf("%-30s%s\n", "SYMBOL", "DATATYPE");
	for (int i = 0; i < 30 + 10 + 50; i++) {
		printf("_");
	}
	printf("\n");
	// Print table body
	for (int i = 0; i < symbol_table_size; i++) {
		char data_type[200];
		type_to_string(data_type, symbol_table[i].type);
		printf("%-30s%s\n", symbol_table[i].name, data_type);
	}
	printf("\n\n");
}

void print_litteral_table() {
	// Print table header
	printf("LITTERAL TABLE:\n\n");
	// Print table body
	for (int i = 0; i < litteral_table_size; i++) {
		// Get data as string
		switch (litteral_table[i].type) {
			case P_LONG:
			case P_INT:
			case P_SHORT:
				printf("%ld\n", litteral_table[i].value.l_long);
				break;
			case P_DOUBLE:
			case P_FLOAT:
				printf("%f\n", litteral_table[i].value.l_double);
				break;
			case P_CHAR:
				printf("'%c'\n", litteral_table[i].value.l_char);
				break;
			case P_STRING:
				printf("\"%s\"\n", litteral_table[i].value.l_string);
		}
	}
	printf("\n\n");
}

void print_ast(struct Statement* statement, int indent) {
	// Print each statement until has none left in linked list
	while (statement != NULL) {
		// Print indent
		for (int i = 0; i < indent; i++) { printf("\t"); }

		char data_type[100];
		switch (statement->type) {
	        case DECLARATION:
	        	type_to_string(data_type, statement->statement.declaration.identifier->type);
	            printf("Declaration of %s of type %s\n",
	                statement->statement.declaration.identifier->name, data_type);
	            break;
	        case ASSIGNMENT:
	            printf("Assignment of %s\n",
	                statement->statement.assignment.identifier->name);
	            break;
	        case EXPRESSION:
	            type_to_string(data_type, statement->statement.expression->data_type);
	            printf("Expression of type %s\n", data_type);
	            break;
	        case SUBROUTINE:
	            type_to_string(data_type, statement->statement.subroutine.identifier->type);
	            printf("Subroutine %s of type %s\n",
	            	statement->statement.subroutine.identifier->name, data_type);
	            // Recursively print subroutine
	            print_ast(statement->statement.subroutine.body, indent + 1);
	            break;
	        case SUBROUTINE_RETURN:
	        	if (statement->statement.expression == NULL) {
	        		printf("Return from subroutine\n");
	        	} else {
		            type_to_string(data_type, statement->statement.expression->data_type);
		            printf("Return from subroutine with value of type %s\n", data_type);
		        }
	    }
	    statement = statement->next;
	}
}

void parse() {
	// Parse to AST
	yyparse();
	printf("No Errors!\n");
	printf("\n\n");

	print_symbol_table();
	print_litteral_table();

	printf("ABSTRACT SYNTAX TREE:\n\n");
	print_ast(first, 0);
}