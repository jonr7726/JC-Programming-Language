extern char current_data_type[50];
extern void exit(int);

void error(char* error_type, char* error_message, int line) {
	fprintf(stderr, "%s ON LINE %d:\n%s\n", error_type, line, error_message);
	exit(0);
}

void declaration_error(char* error_message, int line) {
	error("DECLARATION ERROR", error_message, line);
}

void assignment_error(char* type, int line) {
	char error_message[150];
	sprintf(error_message, "Cannot convert type %s to type %s", current_data_type, type);
	error("ASSIGNMENT ERROR", error_message, line);
}