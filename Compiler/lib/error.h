extern void exit(int);

void error(char* error_type, char* error_message, int line) {
	fprintf(stderr, "%s on line %d:\n%s\n", error_type, line, error_message);
	exit(0);
}

void declaration_error(char* error_message, int line) {
	error("declaration error", error_message, line);
}

void assignment_error(char* expected_type, char* actual_type, int line) {
	char error_message[250];
	sprintf(error_message, "Cannot convert type %s to type %s", actual_type, expected_type);
	error("Assignment error", error_message, line);
}