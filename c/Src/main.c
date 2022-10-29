#include <stdio.h>
#include <stdlib.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/file.h"



// Set Version here
#define BUILD_VERSION    "0.1"
#define BUILD_AUTHOR     "Alexander Malyugin"
#ifndef BUILD_DATE
   #define BUILD_DATE    19910519
#endif

/*****************************************************************************
 * @return void
 ******************************************************************************/
STATIC void vDisplayHelp(void)
{
   printf("Usage:\n");
   printf("\tbinary-parser.exe <file.hex>\n");
   printf("\tbinary-parser.exe <file.s19>\n");
}

/*****************************************************************************
 * @param argc Argument count
 * @param argv String arguments
 * @return  Status
 ******************************************************************************/
int main(int argc, char *argv[])
{
   int32_t  i32Status = 0;
   Memory_t xMemory;

   printf("Build Date: %u\n", BUILD_DATE);
   printf("Version:    %s\n", BUILD_VERSION);
   printf("Author:     %s\n", BUILD_AUTHOR);

   if (argc > 1)
   {
      i32Status  = i32MemoryInitialize(&xMemory);
      i32Status |= i32FileLoad(argv[1], &xMemory);
      i32Status |= i32MemoryPrint(&xMemory);
   }
   // Print help
   else
   {
      vDisplayHelp();
   }


   return(i32Status);
}
