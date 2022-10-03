#include <stdio.h>
#include <stdlib.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/file.h"
#include "misc/helpers.h"


// Set Version here
#define BUILD_VERSION    "0.1"
#define BUILD_AUTHOR     "Alexander Malyugin"

/*****************************************************************************
 * @param argc argument count
 * @param argv string arguments
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
      vMemoryInit(&xMemory);
      i32Status = i32FileLoad(argv[1], &xMemory);
      vMemoryPrint(&xMemory);
   }
   else
   {
      uint8_t rui8TestArray[]       = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
      uint8_t rui8TestArrayZeroes[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
      LogNormal("main: Testing Commenced..\n");
      vMemoryInit(&xMemory);

      LogNormal("main: Test[1]: Append 16 bytes at 0x100");
      i32MemoryAdd(&xMemory, 0x100, 16, rui8TestArray);
      vMemoryPrint(&xMemory);

      LogNormal("main: Test[2]: Replace 8 bytes at 0x108 and append 8 bytes at 0x110");
      i32MemoryAdd(&xMemory, 0x108, 16, rui8TestArray);
      vMemoryPrint(&xMemory);

      LogNormal("main: Test[3]: Append 16 bytes at 0x120");
      i32MemoryAdd(&xMemory, 0x120, 16, rui8TestArray);
      vMemoryPrint(&xMemory);

      LogNormal("main: Test[4]: Replace 16 bytes at 0x100");
      i32MemoryAdd(&xMemory, 0x100, 16, rui8TestArrayZeroes);
      vMemoryPrint(&xMemory);

      LogNormal("main: Test[5]: Replace 8 bytes at 0x110 and in sert 8 bytes at 0x118");
      i32MemoryAdd(&xMemory, 0x110, 16, rui8TestArrayZeroes);
      vMemoryPrint(&xMemory);

      LogNormal("main: Test[6]: Preprend 16 bytes at 0x10");
      i32MemoryAdd(&xMemory, 0x10, 16, rui8TestArray);
      vMemoryPrint(&xMemory);

      LogNormal("main: Test[7]: Replace 1 byte at 0x117");
      i32MemoryAdd(&xMemory, 0x117, 1, &rui8TestArray[1]);
      vMemoryPrint(&xMemory);

      LogNormal("main: Test[8]: Insert 7 bytes at 0x127");
      i32MemoryAdd(&xMemory, 0x127, 7, &rui8TestArray[0]);
      vMemoryPrint(&xMemory);

      LogNormal("main: Testing Finished!\n");
   }

   return(i32Status);
}
