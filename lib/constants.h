#ifndef CONSTANTS_H
#define CONSTANTS_H

// Libraries
#include <stdlib.h>

#define BUFFER 64

#define CALL_METHOD(STRUCT, FUNCTION) STRUCT.FUNCTION(&STRUCT)

// Returns length of array
#define LENGTH(array) (sizeof(array) / sizeof(array[0]))

#endif