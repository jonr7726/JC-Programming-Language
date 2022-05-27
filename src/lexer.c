#include "lexer.h"

int eval_value(struct value* value) {
	switch (value->type) {
		case OPERATION:
			return value->operation->evaluate(value->operation);
		case LITERAL:
			return atoi(value->literal);
	}

	// (ERROR)
	return 0;
}

int eval_operation(struct operation* operation) {
	//int a = CALL_METHOD(*operation->value_a, evaluate)
	int a = operation->value_a->evaluate(operation->value_a);
	int b = operation->value_b->evaluate(operation->value_b);

	switch (operation->type) {
		case ADDITION:
			return a + b;
		case SUBTRACTION:
			return a - b;
	}

	// (ERROR)
	return 0;
}

bool init_value(struct value* value, char* literal) {
	value->evaluate = eval_value;

	value->literal = literal;
	// (assuming only values, no operations)
}

bool init_operation(struct operation* operation, char* literal) {
	operation->evaluate = eval_operation;
}

bool init_statement(struct statement* statement, struct variable* variables, char* literal) {
	struct value values[BUFFER];
	int values_index = 0;
	struct operation operations[BUFFER];
	int operations_index = 0;

	enum read_state state = START;
	enum letter_type letter;

	char arg[BUFFER];
	int arg_index = 0;
	bool separated = false;

	for (int i = 0; literal[i] != 0; i++) {

		letter = get_letter_type(literal[i]);

		switch (state) {
			case START:
				if (letter == OPEN_FUNCTION) {
					arg[arg_index] = 0;
					if (strcmp(arg, PRINT_FUN) == 0) {
						statement->type = PRINT_STATEMENT;
						state = VALUE;
						arg_index = 0;
						separated = false;
					} else {
						return false;
					}
				} else if (letter == ASSIGNMENT) {
					arg[arg_index] = 0;
					if (strcmp(arg, PRINT_FUN) != 0) {
						statement->type = ASSIGNMENT_STATEMENT;
						statement->assignment.variable = init_variable(variables, arg); // (find variable if applicable, otherwise return new vraiable)
						state = VALUE;
						arg_index = 0;
						separated = false;
					} else {
						return false;
					}
				} else if ((letter == LETTER || letter == DIGIT) && !(separated)) {
					arg[arg_index] = literal[i];
					arg_index++;
				} else if (letter == SEPERATOR) {
					separated = true;
				} else {
					return false;
				}
				break;
			case VALUE:
				if (letter == OPERATOR) {
					if (init_value(&values[values_index], arg)) {
						operations[operations_index].value_a = &values[values_index];
						operations[operations_index].operator = literal[i];
						values_index++;
						state = OPERATION;
						arg_index = 0;
						separated = false;
					} else {
						return false;
					}
				} else if (letter == END_STATEMENT) {
					if (init_value(&values[values_index], arg)) {
						
					} else {
						return false;
					}
				} else if (letter == SEPERATOR) {
					separated = true;
				} else if ((letter == LETTER || letter == DIGIT) && !separated) {
					arg[arg_index] = literal[i];
					arg_index++;
				} else {
					return false;
				}
				break;
			case OPERATION:
				if (letter == OPERATOR) {
					// string another operator together
				}
		}

		switch (letter) {
			case DIGIT:

			case LETTER:
				if (state == START || state == VARIABLE || state == VALUE) {
					arg[arg_index] = literal[i];
					arg_index++;
				} else if ()

			case OPERATOR:
				if (state == VALUE) {
					state = OPERATION;
					operations[operations_index].value_a = &values[values_index];
					operations[operations_index].operator = literal[i];
					values_index++;
				} else {
					return false;
				}

	ASSIGNMENT,
	ADD,
	SUBTRACT,
	END_STATEMENT,

	OPEN_FUNCTION,
	CLOSE_FUNCTION,

	SEPERATOR,

	INVALID

		}
	}

	if (letter == END_STATEMENT) {
		//
	} else {
		return false;
	}
}

enum letter_type get_letter_type(char letter) {
	if (letter == ADD_CHAR) {
		return ADD;
	} else if (letter == SUBTRACT_CHAR) {
		return SUBTRACT;
	} else if (letter == END_STATEMENT_CHAR) {
		return END_STATEMENT;
	} else if (letter == ASSIGNMENT_CHAR) {
		return ASSIGNMENT;
	} else {
		char letters[] = LETTER_CHARS;
		for (int i = 0; i < LENGTH(letters); i++) {
			if (letter == letters[i]) {
				return LETTER;
			}
		}

		char digits[] = DIGIT_CHARS;
		for (int i = 0; i < LENGTH(digits); i++) {
			if (letter == digits[i]) {
				return DIGIT;
			}
		}

		char seperators[] = SEPERATOR_CHARS;
		for (int i = 0; i < LENGTH(seperators); i++) {
			if (letter == seperators[i]) {
				return SEPERATOR;
			}
		}

		return INVALID;
	}
}