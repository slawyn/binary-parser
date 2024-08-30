

#include <stdio.h>
#include <stdint.h>
#include "test.h"

typedef struct
{
   uint8_t inner_member;
} structure_t;

structure_t public_str;

void main()
{   
    structure_t str;
    printf("Hello");
    test_function();
}