#include <stdio.h>
#include <stdlib.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/file.h"
#include "misc/helpers.h"

#define SIZEOF(x)    sizeof(x) / sizeof(x[0])

// Set Version here
#define BUILD_VERSION    "0.1"
#define BUILD_AUTHOR     "Alexander Malyugin"

typedef struct
{
   uint32_t ui32DestinationAddress;
   uint32_t ui32Size;
   uint8_t *pui8Data;
} Testmemory_t;

uint8_t      rui8TestArray[]       = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
uint8_t      rui8TestArrayZeroes[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
uint8_t      rui8TestArrayFfs[]    = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
Testmemory_t rxMemoryTests[]       = { { 0x100, 16, rui8TestArray       },
                                       { 0x108, 16, rui8TestArray       },
                                       { 0x120, 16, rui8TestArray       },
                                       { 0x100, 16, rui8TestArrayZeroes },
                                       { 0x110, 16, rui8TestArrayZeroes },
                                       {  0x10, 16, rui8TestArray       },
                                       { 0x117,  1, &rui8TestArray[1]   },
                                       { 0x127,  7, &rui8TestArray[0]   },
                                       { 0x111, 16, rui8TestArrayFfs    } };



/*****************************************************************************
 * @param count Test count
 * @param
 ******************************************************************************/
void vTestMemory(Memory_t *pxMemory)
{
   uint8_t ui8Error = 0;
   LogTest("main::vTestMemory: Testing Commenced..\n");
   vMemoryInit(pxMemory);
   for (uint32_t ui32LoopIndex = 0; ui32LoopIndex < SIZEOF(rxMemoryTests) && !ui8Error; ++ui32LoopIndex)
   {
      LogTest("main::vTestMemory: Test[%d]: Writing %d bytes at %x", ui32LoopIndex, rxMemoryTests[ui32LoopIndex].ui32Size, rxMemoryTests[ui32LoopIndex].ui32DestinationAddress);
      i32MemoryAdd(pxMemory, rxMemoryTests[ui32LoopIndex].ui32DestinationAddress, rxMemoryTests[ui32LoopIndex].ui32Size, rxMemoryTests[ui32LoopIndex].pui8Data);

      uint32_t ui32InnerLoop = ui32LoopIndex;
      //for (uint32_t ui32InnerLoop = 0; ui32InnerLoop < ui32LoopIndex; ++ui32InnerLoop)
      {
         if (i32MemoryCompare(pxMemory, rxMemoryTests[ui32InnerLoop].ui32DestinationAddress, rxMemoryTests[ui32InnerLoop].ui32Size, rxMemoryTests[ui32InnerLoop].pui8Data))
         {
            ui8Error = 1;
            break;
         }
      }

      if (ui8Error)
      {
         LogTest("main::vTestMemory: Test[%d] NOK!", ui32LoopIndex);
      }
      else
      {
         LogTest("main::vTestMemory: Test[%d] OK!", ui32LoopIndex);
      }

      vMemoryPrint(pxMemory);
   }
   LogTest("main::vTestMemory: Testing Finished!\n");
}

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
      vTestMemory(&xMemory);
   }

   return(i32Status);
}
