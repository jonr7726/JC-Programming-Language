#include "constants.h"

struct operation;
struct value;

enum value_type {
	LITERAL,
	OPERATION
};

struct value {
	enum value_type type;
	char* literal;
	struct operation* operation;

	int (*evaluate)(struct value*);
};

enum operator_type {
	ADDITION,
	SUBTRACTION
};

struct operation {
	enum operator_type type;
	struct value* value_a;
	struct value* value_b;

	int (*evaluate)(struct operation*);
};

struct variable {
	char* name;
	int value;
};

struct assignment {
	struct variable* variable;
	struct value* value;
};

struct print {
	struct value* value;
};

enum statement_type {
	ASSIGNMENT_STATEMENT,
	PRINT_STATEMENT
};

struct statement {
	enum statement_type type;
	struct assignment assignment;
	struct print print;
};


#define OPERATOR_CHARS = {'+', '-'}

#define DIGIT_CHARS {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}

#define LETTER_CHARS { \
	'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', \
	'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', \
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', \
	'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', \
	'_' \
}

#define SEPERATOR_CHARS {' ', '\t', '\n'}

#define ASSIGNMENT_CHAR '='
#define END_STATEMENT_CHAR ';'
#define OPEN_FUNCTION_CHAR '('
#define CLOSE_FUNCTION_CHAR ')'

#define PRINT_FUN "print"

enum letter_type {
	DIGIT,
	LETTER,

	ASSIGNMENT,
	OPERATOR
	END_STATEMENT,

	OPEN_FUNCTION,
	CLOSE_FUNCTION,

	SEPERATOR,

	INVALID
};

enum read_state {
	START,

	VARIABLE,
	VALUE,

	OPERATION
};

int eval_value(struct value* value);

int eval_operation(struct operation* operation);

bool init_value(struct value* value, char* literal);

bool init_operation(struct operation* operation, char* literal);

bool init_statement(struct statement* statement, char* literal);

enum letter_type get_letter_type(char letter);

// EBNF language (only maths with integers for now)
/*
statement: (<print>|<assignment>);

print: print\(<value>\)

assignment: <variable> = <value>

value: <operation>|<literal>|<variable>

operation: <value> <operator> <value>
operator: (+|-)

literal: [-]<number>
number: <digit>{<digit>}
digit: (0|1|2|3|4|5|6|7|8|9)
*/