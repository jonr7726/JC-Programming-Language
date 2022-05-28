%{
    #include <stdio.h>
    #include <string.h>
    #include <stdbool.h>

    #include "lib/error.h"
    #include "lib/parser.h"

    extern char current_data_type[50];

    extern void yyerror();
    extern int yylex();
    extern char* yytext;
    extern int yylineno;

    void declaration_error(char*, int);
    void assignment_error(char*, int);

    void clear_data();
    void store_data_type(char*, char*);
    bool variable_declared(char*);
    bool valid_data_type(char*);
    char* get_data_type(char*);

%}



%union {
    int int_val;
    float float_val;
    char* str_val;
}



%token SEMICOLON

%token EQUALS

%token BRACKET_OPEN
%token BRACKET_CLOSE

%token PLUS
%token MINUS

%token <int_val> INTEGER_VALUE
%token <float_val> FLOAT_VALUE

%token <str_val> IDENTIFIER
%token <str_val> DATA_TYPE


%type <str_val> STATEMENT
%type <str_val> EXPRESSION

%type <str_val> VARIABLE
%type <str_val> VALUE

%type <str_val> OPERATION
%type <str_val> OPERATOR


%%
  
STATEMENT           : STATEMENT EXPRESSION SEMICOLON  {clear_data();}
                    | EXPRESSION SEMICOLON            {clear_data();}
                    | error '>'                       {;/*Stops excecution*/}
                    ;

EXPRESSION          : VARIABLE_DECLARE EQUALS OPERATION {;}
                    ;

VARIABLE_DECLARE    : DATA_TYPE IDENTIFIER {
                        if (variable_declared($2)) {
                            declaration_error("Variable already declared", yylineno);
                        } else {
                            store_data_type($1, $2);
                            store_current_data_type($2);
                        }
                    }
                    ;

VARIABLE            : IDENTIFIER {
                        if (!variable_declared($1)) {
                            declaration_error("Variable not declared before use", yylineno);
                        } else {
                            store_current_data_type($1);
                        }
                    }
                    ;

OPERATION           : OPERATION OPERATOR VALUE {;}
                    | VALUE                    {;}
                    ;

VALUE               : INTEGER_VALUE {
                        if(!valid_data_type("int")) {
                            assignment_error("int", yylineno);
                        }
                    }
                    | FLOAT_VALUE   {
                        if(!valid_data_type("float")) {
                            assignment_error("float", yylineno);
                        }
                    }
                    | VARIABLE      {
                        if(!valid_data_type(get_data_type($1))) {
                            assignment_error(get_data_type($1), yylineno);
                        }
                    }
                    ;

OPERATOR            : PLUS  {;}
                    | MINUS {;}
                    ;

%%


int main(){

    yyparse();
    printf("No Errors!!\n");
    return 0;
}