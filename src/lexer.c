#include "lexer.h"

bool get_tokens(char* code, struct token* tokens) {

	for (int i = 0; code[i] != 0; i++) {

		switch(code[i]) {
			case '+':
				tokens[token_index] = (struct token) {.type = TT_PLUS};
				break;
			case '-':
				tokens[token_index] = (struct token) {.type = TT_MINUS};
				break;
			case '=':
				tokens[token_index] = (struct token) {.type = TT_EQUALS};
				break;
			case '(':
				tokens[token_index] = (struct token) {.type = TT_OPEN_BRAC};
				break;
			case ')':
				tokens[token_index] = (struct token) {.type = TT_CLOSE_BRAC};
				break;
			case ';':
				tokens[token_index] = (struct token) {.type = TT_SEMICOLEN};
				break;

			default:
				if (isdigit(code[i])) {
					tokens[token_index] = make_number(code, &i);
				} else if (isalpha(code[i])) {
					tokens[token_index] = 
				} else if (!isspace(code[i])) {
					printf("ERROR: Invalid character %c at index %d\n", code[i], i);
					return false;
				}
		}
	}
}

/*void copy_token(struct token from, struct token* to) {
	to->type = from.type;

	if (from.type == TT_INT) {
		to->value.val_int = from->value.val_int;
	} else if (from.type == TT_FLOAT) {
		to->value.val_float = from->value.val_float;
	}
}*/

struct token make_number(char* code, int* i) {
	struct token number = (struct token) {.type = TT_INT, .value.val_int = 0};

	for (; isdigit(code[*i]); *i++) {
		number.value.val_int *= 10;
		number.value.val_int += code[*i] - '0';
	}

	if (code[*i] == '.') {
		float multiplier = 1;
		for (; isdigit(code[*i]); *i++) {
			multiplier /= 10;
			number.value.val_float += multiplier * (code[*i] - '0');
		}
	}

	return number;
}