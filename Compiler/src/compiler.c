#include "compiler.h"

int main(int argc, char* argv[]) {
    // Parse to AST
    yyparse();

    // Code generation
    code_gen(first, "test.jc", "test");
    return 0;
}