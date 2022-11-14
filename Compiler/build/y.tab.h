/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_YY_BUILD_Y_TAB_H_INCLUDED
# define YY_YY_BUILD_Y_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    SEMICOLON = 258,               /* SEMICOLON  */
    EQUALS = 259,                  /* EQUALS  */
    BRACKET_OPEN = 260,            /* BRACKET_OPEN  */
    BRACKET_CLOSE = 261,           /* BRACKET_CLOSE  */
    PLUS = 262,                    /* PLUS  */
    MINUS = 263,                   /* MINUS  */
    INT_TYPE = 264,                /* INT_TYPE  */
    FLOAT_TYPE = 265,              /* FLOAT_TYPE  */
    VOID_TYPE = 266,               /* VOID_TYPE  */
    LONG_VALUE = 267,              /* LONG_VALUE  */
    INT_VALUE = 268,               /* INT_VALUE  */
    SHORT_VALUE = 269,             /* SHORT_VALUE  */
    DOUBLE_VALUE = 270,            /* DOUBLE_VALUE  */
    FLOAT_VALUE = 271,             /* FLOAT_VALUE  */
    IDENTIFIER = 272               /* IDENTIFIER  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif
/* Token kinds.  */
#define YYEMPTY -2
#define YYEOF 0
#define YYerror 256
#define YYUNDEF 257
#define SEMICOLON 258
#define EQUALS 259
#define BRACKET_OPEN 260
#define BRACKET_CLOSE 261
#define PLUS 262
#define MINUS 263
#define INT_TYPE 264
#define FLOAT_TYPE 265
#define VOID_TYPE 266
#define LONG_VALUE 267
#define INT_VALUE 268
#define SHORT_VALUE 269
#define DOUBLE_VALUE 270
#define FLOAT_VALUE 271
#define IDENTIFIER 272

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
union YYSTYPE
{
#line 7 "src/parser.y"

	struct Statement* statement;

	struct Expression* expression;
	struct Litteral* litteral;
	struct Identifier* identifier;

	struct DataType* data_type;
	char* string;
	int token;

#line 113 "build/y.tab.h"

};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_BUILD_Y_TAB_H_INCLUDED  */
