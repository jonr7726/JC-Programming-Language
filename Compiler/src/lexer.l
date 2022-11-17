%{
	#include <string.h>
	#include <stdlib.h>
	#include "parser.h"

	void extern yyerror(char*);
	void invalid_token();
%}

whitespace		[ \t\r\v\f]+

name			[A-Za-z][A-Za-z0-9]*

integer			-?[0-9]+
real			-?[0-9]*\.?[0-9]+

commentSingle	\/\/.*
commentMulti	\/\*(.*\n)*.*\*\/

%%

{commentSingle}			{ ; }
{commentMulti}			{ ; }

";"						{ return SEMICOLON; }
"="						{ return EQUALS; }
"+"						{ return PLUS; }
"-"						{ return MINUS; }
"("						{ return BRACKET_OPEN; }
")"						{ return BRACKET_CLOSE; }
"{"						{ return BRACKET_CURLY_OPEN; }
"}"						{ return BRACKET_CURLY_CLOSE; }

"return"				{ return RETURN; }

"int"					{ return INT_TYPE; }
"float"					{ return FLOAT_TYPE; }
"void"					{ return VOID_TYPE; }

{integer}l				{ yylval.string = strdup(yytext); yylval.string[strlen(yylval.string) - 1] = 0; return LONG_VALUE; }
{integer}				{ yylval.string = strdup(yytext); return INT_VALUE; }
{integer}s				{ yylval.string = strdup(yytext); yylval.string[strlen(yylval.string) - 1] = 0; return SHORT_VALUE; }
{real}					{ yylval.string = strdup(yytext); return DOUBLE_VALUE; }
{real}f					{ yylval.string = strdup(yytext); yylval.string[strlen(yylval.string) - 1] = 0; return FLOAT_VALUE; }

{name}					{ yylval.string = strdup(yytext); return IDENTIFIER; }

{whitespace}			{ ; }
\n						{ yylineno++; }
.						{ invalid_token(); }

%%

int yywrap(void) {
	return 1;
}

void yyerror(char *e) {
	fprintf(stderr, "Syntax error on line %d:\n%s\n", yylineno, e);
	exit(0);
}

void invalid_token() {
	fprintf(stderr, "Syntax error on line %d:\nInvalid token %s\n", yylineno, yytext);
	exit(0);
}
