%{
    #include <string.h>
    #include <stdlib.h>
    #include "y.tab.h"

    void extern yyerror(char*);
    void invalid_token();
    void syntax_error();
%}

whitespace [ \t\r\v\f]+
linefeed   \n

name       [A-Za-z][A-Za-z0-9]*

integer    -?[0-9]+
floating   -?[0-9]*\.?[0-9]+

%%

";"                     {return SEMICOLON;}
"="                     {return EQUALS;}
"+"                     {return PLUS;}
"-"                     {return MINUS;}
"("                     {return BRACKET_OPEN;}
")"                     {return BRACKET_CLOSE;}

"int" |
"float"                 {yylval.str_val = strdup(yytext); return DATA_TYPE;}

{integer}               {yylval.int_val = atoi(yytext); return INTEGER_VALUE;}
{floating}              {yylval.float_val = atof(yytext); return FLOAT_VALUE;}

{name}                  {yylval.str_val = strdup(yytext); return IDENTIFIER;}

{linefeed}              {yylineno++;}
{whitespace}            {;}
.                       {invalid_token();}

%%

int yywrap(void){
    return 1;
}

void yyerror(char *e) {
    fprintf(stderr, "ERROR ON LINE %d:\n%s\n", yylineno, e);
    exit(0);
}

void invalid_token() {
    fprintf(stderr, "ERROR ON LINE %d:\nInvalid Token %s\n", yylineno, yytext);
    exit(0);
}
