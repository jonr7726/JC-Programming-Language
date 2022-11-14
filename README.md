# JC-Programming-Language
A self-made programming language.
This is a WIP compiler written in C using Yacc and Bison that compiles to LLVM-IR assembly language, (which can then be further compiled to machine code).

## Structure
Yacc and Bison are used to generate a parser (which handles lexical and syntactical analysis). From there, code-generation is done to output LLVM-IR code.