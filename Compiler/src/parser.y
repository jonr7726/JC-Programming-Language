%{
	#include <stdlib.h>
	#include <string.h>
	#include <stdbool.h>
	#include <stdio.h>

	#include "error.h"
	#include "ast_structure.h"

	struct ExpressionList { // Linked list of expressions
		Expression* expression;
		struct ExpressionList* next; // Next in linked list, or NULL
	};

	struct DeclarationList { // Linked list of (parameter) declarations
		char* identifier;
		DataType* data_type;
		struct DeclarationList* next; // Next in linked list, or NULL
	};

	struct DeclarationList* create_param_decl(char* identifier, DataType* data_type);
	struct ExpressionList* create_param_expr(Expression* expression);
	
	Node* create_subroutine_node_wrapper(char* identifier,
		struct DeclarationList* param_decls, DataType* return_type, Node* body);
	Expression* create_subroutine_call_wrapper(char* identifier,
		struct ExpressionList* param_exprs);

	extern void yyerror();
	extern int yylex();
	extern char* yytext;
	extern int yylineno;

	Node* first;
%}


/* Union for all the ways to can access data nodes */
%union {
	Node* node;
	Expression* expression;
	DataType* data_type;

	enum OperationType operation;
	enum PrimitiveDataType primitive;

	struct ExpressionList* expressions;
	struct DeclarationList* declarations;

	char* string;
	int token;
}


/* Terminal Symbols */
%token <token> SEMICOLON COMMA BRACKET_OPEN BRACKET_CLOSE BRACKET_CURLY_OPEN BRACKET_CURLY_CLOSE EQUALS PLUS MINUS
%token <token> INT_TYPE FLOAT_TYPE VOID_TYPE
%token <token> RETURN
%token <string> LONG_VALUE INT_VALUE SHORT_VALUE DOUBLE_VALUE FLOAT_VALUE
%token <string> IDENTIFIER

/* Non-terminal Symbols */
%type <node> program nodes node

%type <declarations> param_decls param_decl
%type <expressions> param_exprs param_expr

%type <expression> expression litteral
%type <operation> bin_operator pre_un_operator
%type <data_type> data_type

/* Operator precedence */
%left PLUS MINUS

/* Top node of AST */
%start program

%%

program	: nodes { first = $1; }
		;

nodes	: node { $$ = $1; }
		| nodes node {
			$$ = $1; // Return first in linked list
			GET_LAST($1)->next = $2; // Chain next node
		}
		;
  
node	: data_type IDENTIFIER SEMICOLON { $$ = create_declaration_node($2, $1); }
		| IDENTIFIER EQUALS expression SEMICOLON { $$ = create_assignment_node($1, $3); }
		| data_type IDENTIFIER BRACKET_OPEN BRACKET_CLOSE BRACKET_CURLY_OPEN nodes BRACKET_CURLY_CLOSE {
			// Subroutine with no parameters
			$$ = create_subroutine_node($2, NULL, create_subroutine_data_type(NULL, 0, $1), $6);
		}
		| data_type IDENTIFIER BRACKET_OPEN param_decls BRACKET_CLOSE BRACKET_CURLY_OPEN nodes BRACKET_CURLY_CLOSE {
			// Subroutine with parameters
			$$ = create_subroutine_node_wrapper($2, $4, $1, $7);
		}
		| RETURN expression SEMICOLON { $$ = create_return_node($2); }
		| RETURN SEMICOLON { $$ = create_return_node(NULL); }
		;

param_decls	: param_decl { $$ = $1; }
			| param_decls COMMA param_decl {
				$$ = $1; // Return first in linked list
				GET_LAST($1)->next = $3; // Chain next parameter declaration
			}

param_decl 	: data_type IDENTIFIER { $$ = create_param_decl($2, $1); }

expression	: IDENTIFIER BRACKET_OPEN BRACKET_CLOSE {
				// Subroutine call with no parameters
				$$ = create_subroutine_call($1, NULL, 0);
			}
			| IDENTIFIER BRACKET_OPEN param_exprs BRACKET_CLOSE {
				// Subroutine call with parameters
				$$ = create_subroutine_call_wrapper($1, $3);
			}
			| IDENTIFIER { $$ = create_variable($1); }
			| litteral { $$ = $1; }
			| expression bin_operator expression { $$ = create_operation($2, $1, $3); }
			| expression pre_un_operator { $$ = create_operation($2, $1, NULL); }
			;

param_exprs	: param_expr { $$ = $1; }
			| param_exprs COMMA param_expr {
				$$ = $1; // Return first in linked list
				GET_LAST($1)->next = $3; // Chain next parameter declaration
			}

param_expr	: expression { $$ = create_param_expr($1); }

data_type	: INT_TYPE { $$ = create_primitive_data_type(P_INT); }
			| FLOAT_TYPE { $$ = create_primitive_data_type(P_FLOAT); }
			| VOID_TYPE { $$ = NULL; }
			;

bin_operator	: PLUS { $$ = O_ADD; }
				| MINUS { $$ = O_SUBTRACT; }
				;

pre_un_operator	: MINUS { $$ = O_COMPLEMENT; }
				;

litteral	: LONG_VALUE { $$ = create_litteral(P_LONG, 10, $1); }
			| INT_VALUE { $$ = create_litteral(P_INT, 10, $1); }
			| SHORT_VALUE { $$ = create_litteral(P_SHORT, 10, $1); }
			| DOUBLE_VALUE { $$ = create_litteral(P_DOUBLE, 0, $1); }
			| FLOAT_VALUE { $$ = create_litteral(P_FLOAT, 0, $1); }
			;

%%

/*
 * Dynamically allocate memory for new parameter declaration in linked list.
 */
struct DeclarationList* create_param_decl(char* identifier, DataType* data_type) {
	struct DeclarationList* param_decl = (struct DeclarationList*) malloc(sizeof(struct DeclarationList));
    param_decl->identifier = identifier;
    param_decl->data_type = data_type;
    param_decl->next = NULL;
    return param_decl;
}

/*
 * Dynamically allocate memory for new parameter expression in linked list.
 */
struct ExpressionList* create_param_expr(Expression* expression) {
	struct ExpressionList* param_expr = (struct ExpressionList*) malloc(sizeof(struct ExpressionList));
    param_expr->expression = expression;
    param_expr->next = NULL;
    return param_expr;
}

/*
 * (Wrapper function for create_subroutine_node).
 * Creates a subroutine node in dynamic memory and returns pointer to it.
 */
Node* create_subroutine_node_wrapper(char* identifier,
	struct DeclarationList* param_decls, DataType* return_type, Node* body) {

	// Count parameters
	int param_size = 0;
	struct DeclarationList* param_decl = param_decls;
	while (param_decl != NULL) {
        param_decl = param_decl->next;
        param_size++;
    }
    
    // Allocate memory to arrays for parameter identifiers and datatypes
    char** param_identifiers = (char**) calloc(param_size, sizeof(char**));
    DataType** param_data_types = (DataType**) calloc(param_size, sizeof(DataType**));

    // Initialize parameter identifiers and datatypes
	param_decl = param_decls;
	for (int i = 0; i < param_size; i++) {
		param_identifiers[i] = param_decl->identifier;
		param_data_types[i] = param_decl->data_type;

		// Free memory of parameter declaration
		struct DeclarationList* next = param_decl->next;
		free(param_decl);
        param_decl = next;
    }

    // Create subroutine node
	return create_subroutine_node(identifier, param_identifiers,
		create_subroutine_data_type(param_data_types, param_size, return_type), body);
}

/*
 * (Wrapper function for create_subroutine_call).
 * Creates a subroutine call expression in dynamic memory and returns pointer to it.
 */
Expression* create_subroutine_call_wrapper(char* identifier,
	struct ExpressionList* param_exprs) {

	// Count parameters
	int param_size = 0;
	struct ExpressionList* param_expr = param_exprs;
	while (param_expr != NULL) {
        param_expr = param_expr->next;
        param_size++;
    }
    
    // Allocate memory to arrays for parameter identifiers and datatypes
    Expression** params = (Expression**) calloc(param_size, sizeof(Expression**));

    // Initialize parameter identifiers and datatypes
	param_expr = param_exprs;
	for (int i = 0; i < param_size; i++) {
		params[i] = param_expr->expression;

		// Free memory of parameter expression
		struct ExpressionList* next = param_expr->next;
		free(param_expr);
        param_expr = next;
    }

    // Create subroutine node
	return create_subroutine_call(identifier, params, param_size);
}
