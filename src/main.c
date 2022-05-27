#include "main.h"

int main(int argc, char** argv) {

	if (argc < 2) {
		printf("ERROR: Please enter argument to interpret\n");
		return 0;
	}

	struct statement lex;
	if (init_statement(&lex, argv[1])) {
		printf("Success\n");
	} else {
		printf("Failure\n");
	}

	return 0;
}