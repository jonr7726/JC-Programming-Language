%{
	#include <stdlib.h>
	#include <string.h>
	#include <stdbool.h>
	#include <stdio.h>

	#include "error.h"
	#include "ast_structure.h"

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

	struct ExpressionList {
		Expression** expressions;
		int size;
	} expressions;

	struct DeclarationList {
		char** identifiers;
		DataType** data_types;
		int size;
	} declarations;

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
%type <node> program nodes
%type <node> node

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
			get_last_node($1)->next = $2; // Chain next node
			$$ = $1; // Return first in linked list
		}
		;
  
node	: data_type IDENTIFIER SEMICOLON { $$ = create_declaration_node($2, $1); }
		| IDENTIFIER EQUALS expression SEMICOLON { $$ = create_assignment_node($1, $3); }
		| data_type IDENTIFIER BRACKET_OPEN BRACKET_CLOSE BRACKET_CURLY_OPEN nodes BRACKET_CURLY_CLOSE {
			$$ = create_subroutine_node($2, create_subroutine_data_type(NULL, NULL, 0, $1), $6);
		}
		| RETURN expression SEMICOLON { $$ = create_return_node($2); }
		| RETURN SEMICOLON { $$ = create_return_node(NULL); }
		;

expression	: IDENTIFIER { $$ = create_variable($1); }
			| litteral { $$ = $1; }
			| expression bin_operator expression { $$ = create_operation($2, $1, $3); }
			| expression pre_un_operator { $$ = create_operation($2, $1, NULL); }
			;

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