#include "constants.h"

enum token_type {
	TT_INT,
	TT_FLOAT,

	TT_PLUS,
	TT_MINUS,

	TT_EQUALS,

	TT_OPEN_BRAC,
	TT_CLOSE_BRAC,

	TT_SEMICOLEN
};

union value {
	int val_int;
	float val_float;
};

struct token {
	enum token_type type;
	union value value;
};

bool get_tokens(char* code, struct token* tokens);

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