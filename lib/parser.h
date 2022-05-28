#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

int identifier_amount = 0;

struct identifier_structure
{
    char* identifier;
    char* data_type;
}identifiers[50];

char current_data_type[50];


void clear_data() {
	current_data_type[0] = 0;
}

void store_current_data_type(char* identifier) {
	for(int i = 0; i < identifier_amount; i++){
        if(strcmp(identifier, identifiers[i].identifier) == 0){
			strcpy(current_data_type, identifiers[i].data_type);
		}
	}
}

void store_data_type(char* type, char* identifier) {
	identifiers[identifier_amount].identifier = identifier;
	identifiers[identifier_amount].data_type = type;
	identifier_amount++;
}

bool variable_declared(char* identifier) {
	for(int i = 0; i < identifier_amount; i++){
        if(strcmp(identifier, identifiers[i].identifier) == 0){
            return true;
        }
    }
    return false;
}

bool valid_data_type(char* type) {
	return (strcmp(current_data_type, type) == 0);
}

char* get_data_type(char* identifier) {
	for(int i = 0; i < identifier_amount; i++){
        if(strcmp(identifier, identifiers[i].identifier) == 0){
            return identifiers[i].data_type;
        }
    }
	return "";
}