#include <stdlib.h>
#include <stdio.h>

#include "config.h"
#include "types.h"
#include "assert.h"



void v__OnAssert__(char const *file, unsigned line)
{
   printf("ASSERT:: %s %d\n", file, line);
}
