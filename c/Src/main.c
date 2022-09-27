#include "types.h"
#include <stdio.h>
#include <stdlib.h>


#include "misc/memory.h"
#include "misc/file.h"



/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
 ******************************************************************************/
int main(int argc, char *argv[])
{
   int32_t  i32Status = 0;
   Memory_t xMemory;

   printf("Version: 0.1\nAuthor: Alexander Malyugin\n");

   if (argc > 1)
   {
      vMemoryInit(&xMemory);
      i32Status = i32FileLoad(argv[1], &xMemory);
      vMemoryPrint(&xMemory);
   }

   return(i32Status);
}
