#include "types.h"
#include <stdio.h>
#include <stdlib.h>


#include "misc/memory.h"
#include "misc/file.h"


uint8_t rui8TestArray[]  = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
uint8_t rui8TestArray0[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };

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
   else
   {
      vMemoryInit(&xMemory);


      // Test
      printf("Test Start");
      i32MemoryAdd(&xMemory, 0x100, 16, rui8TestArray);
      vMemoryPrint(&xMemory);

      // Insert
      i32MemoryAdd(&xMemory, 0x108, 16, rui8TestArray);
      vMemoryPrint(&xMemory);

      // Append

      i32MemoryAdd(&xMemory, 0x120, 16, rui8TestArray);
      vMemoryPrint(&xMemory);

      // Overwrite
      i32MemoryAdd(&xMemory, 0x100, 16, rui8TestArray0);
      vMemoryPrint(&xMemory);

      // Overwrite + Insert
      i32MemoryAdd(&xMemory, 0x110, 16, rui8TestArray0);
      vMemoryPrint(&xMemory);

      // Prpeend
      i32MemoryAdd(&xMemory, 0x10, 16, rui8TestArray);
      vMemoryPrint(&xMemory);

      printf("Test Done");
   }

   return(i32Status);
}
