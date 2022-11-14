%{
	#include "parser.h"
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
%token <token> SEMICOLON EQUALS BRACKET_OPEN BRACKET_CLOSE PLUS MINUS
%token <token> INT_TYPE FLOAT_TYPE VOID_TYPE
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

program	: statements
		;

statements	: statement { $$ = $1; }
			| statements statement {
				get_last_statment($1)->next = $2; // Chain next statement
				$$ = $1; // Return first in linked list
			}
			;
  
statement	: data_type IDENTIFIER SEMICOLON { // Declaration
				// Ensure identifier does not already exist and has valid data type
				if (identifier_declared($2)) {
					declaration_error("Variable already declared", yylineno);
				} else if ($1 == NULL) {
					declaration_error("Variable cannot be declared as void type", yylineno);
				}
				
				// Store identifier in symbol table
				symbol_table[symbol_table_size].name = $2;
    			symbol_table[symbol_table_size].type = $1;

				// Add statement node
				statements[statements_size] = (struct Statement) {
					.type = DECLARATION,
					.statement.declaration.identifier = &symbol_table[symbol_table_size++],
					.next = NULL
				};
				$$ = &statements[statements_size++];
			}
			| variable EQUALS expression SEMICOLON { // (Re)assignment
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
		char data_type[100];
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

void print_ast() {
	// Print title
	printf("ABSTRACT SYNTAX TREE:\n\n");
	// Print each statement until has none left in linked list
	struct Statement* statement = statements;
	do {
		switch (statement->type) {
	        case DECLARATION:
	            printf("Declaration of identifier %s\n",
	                statement->statement.declaration.identifier->name);
	            break;
	        case ASSIGNMENT:
	            printf("Assignment of identifier %s\n",
	                statement->statement.assignment.identifier->name);
	            break;
	        case EXPRESSION:
	            char data_type[100];
	            type_to_string(data_type, statement->statement.expression->data_type);
	            printf("Expression of type %s\n", data_type);
	    }
	    statement = statement->next;
	} while (statement->next != NULL);
	printf("\n\n");
}

int main() {
	yyparse();
	printf("No Errors!\n");
	printf("\n\n");

	print_symbol_table();
	print_litteral_table();
	print_ast();
	return 0;
}