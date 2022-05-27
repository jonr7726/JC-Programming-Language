#include "main.h"

int main(int argc, char** argv) {

	if (argc < 2) {
		printf("ERROR: Please enter file name to compile\n");
		return 0;
	} else if (argc < 3) {
		printf("ERROR: Please enter output file name\n");
		return 0;
	}

	char* buffer = NULL;
	long length;
	FILE* code_file = fopen(filename, "rb");

	if (code_file != NULL) {
		// Find and allocate space for file
		fseek(code_file, 0, SEEK_END);
		length = ftell(code_file);
		fseek(code_file, 0, SEEK_SET);
		buffer = malloc(length);

		if (buffer != NULL) {
			// Read file to string
			fread(buffer, 1, length, code_file);
		}
		fclose(code_file);
	}

	if (buffer == NULL) {
		printf("ERROR: File could not be opened\n");
		return 0;
	}

	struct token* tokens = malloc(length * sizeof(struct token));

	if (tokens == NULL) {
		printf("ERROR: Could not allocate memory for tokens\n");
		return 0;
	}

	if (!get_tokens(buffer, tokens)) {
		// (Error logged in lexer)
		return 0;
	}

	printf("Success!\n");

	return 0;
}