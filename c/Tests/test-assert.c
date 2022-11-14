#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/file.h"
#include "assert.h"

/* Unity */
#include "unity_config.h "
#include "unity.h "


PROTOTYPE size_t xGetLine(uint8_t **ppui8LineBuffer, const size_t xReadMax, FILE *pxFileHandle);

/*****************************************************************************
 * @brief Unity Setup and Teardowns
 ******************************************************************************/
void setUp(void)
{
}

void tearDown(void)
{
}

void test00_AssertingWorks(void)
{
   ASSERT(1 != 0);
}

/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
 ******************************************************************************/
int main(int argc, char *argv[])
{
   UnityBegin(__FILE__);
   RUN_TEST(test00_AssertingWorks, 0);
   return(UnityEnd());
}
