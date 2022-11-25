# JC-Programming-Language
A self-made programming language.
This is a WIP compiler written entirely in C using Yacc, Bison and LLVM-IR.

## Structure
Yacc and Bison are used to generate a parser (which handles lexical and syntactical analysis, producing an Abstract Syntax Tree). From there, code-generation is done with the LLVM-C API to output machine code.

## Language
The language is currently in a very basic form and syntactically matches C for the features that it does facilitate. In the future I intend to implement object oriented capabilities, which will likely make it similar to C# or Java.