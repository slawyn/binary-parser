#include <stdio.h>
#include <stdlib.h>

#include "config.h"
#include "types.h"
#include "misc/memory.h"
#include "misc/file.h"
#include "misc/helpers.h"


typedef struct
{
   uint32_t ui32DestinationAddress;
   uint32_t ui32Size;
   uint8_t *pui8Data;
} TestAddMemory_t;

typedef struct
{
   uint32_t ui32SourceAddress;
   uint32_t ui32DestinationAddress;
   uint32_t ui32Size;
} TestCopyMemory_t;

uint8_t         rui8TestArray[]       = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff };
uint8_t         rui8TestArrayZeroes[] = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
uint8_t         rui8TestArrayFfs[]    = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
TestAddMemory_t rxMemoryAddTests[]    = { { 0x100, 16, rui8TestArray       },
                                          { 0x108, 16, rui8TestArray       },
                                          { 0x120, 16, rui8TestArray       },
                                          { 0x100, 16, rui8TestArrayZeroes },
                                          { 0x110, 16, rui8TestArrayZeroes },
                                          {  0x10, 16, rui8TestArray       },
                                          { 0x117,  1, &rui8TestArray[1]   },
                                          { 0x127,  7, &rui8TestArray[0]   },
                                          { 0x111, 16, rui8TestArrayFfs    },
                                          { 0x100, 16, rui8TestArray       } };


TestCopyMemory_t rxMemoryCopyTests[] = { { 0x100, 0x110, 15 } };

/*****************************************************************************
 * @param count Test count
 * @param
 ******************************************************************************/
void vTestMemory(Memory_t *pxMemory)
{
   uint8_t ui8Error = FALSE;

   LogTest("main::vTestMemory: Testing Commenced..\n");
   vMemoryInit(pxMemory);

   // Add test
   //------------------------------------------------------------------------------------------------------
   for (uint32_t ui32LoopIndex = 0; ui32LoopIndex < SIZEOF(rxMemoryAddTests) && !ui8Error; ++ui32LoopIndex)
   {
      LogTest("main::vTestMemory: Test-Add[%d]: Writing %d bytes at %x", ui32LoopIndex, rxMemoryAddTests[ui32LoopIndex].ui32Size, rxMemoryAddTests[ui32LoopIndex].ui32DestinationAddress);
      i32MemoryAdd(pxMemory, rxMemoryAddTests[ui32LoopIndex].ui32DestinationAddress, rxMemoryAddTests[ui32LoopIndex].ui32Size, rxMemoryAddTests[ui32LoopIndex].pui8Data);

      uint32_t ui32InnerLoop = ui32LoopIndex;
      //for (uint32_t ui32InnerLoop = 0; ui32InnerLoop < ui32LoopIndex; ++ui32InnerLoop)
      {
         if (i32MemoryCompare(pxMemory, rxMemoryAddTests[ui32InnerLoop].ui32DestinationAddress, rxMemoryAddTests[ui32InnerLoop].ui32Size, rxMemoryAddTests[ui32InnerLoop].pui8Data))
         {
            ui8Error = TRUE;
            //break;
         }
      }

      if (ui8Error)
      {
         LogTest("main::vTestMemory: Test-Add[%d] NOK!", ui32LoopIndex);
      }
      else
      {
         LogTest("main::vTestMemory: Test-Add[%d] OK!", ui32LoopIndex);
      }

      vMemoryPrint(pxMemory);
   }

   // Copy test
   //------------------------------------------------------------------------------------------------------
   for (uint32_t ui32LoopIndex = 0; ui32LoopIndex < SIZEOF(rxMemoryCopyTests) && !ui8Error; ++ui32LoopIndex)
   {
      LogTest("main::vTestMemory: Test-Copy[%d]: Copying %d bytes from %x to %x", ui32LoopIndex, rxMemoryCopyTests[ui32LoopIndex].ui32Size, rxMemoryCopyTests[ui32LoopIndex].ui32SourceAddress, rxMemoryCopyTests[ui32LoopIndex].ui32DestinationAddress);
      i32MemoryCopy(pxMemory, rxMemoryCopyTests[ui32LoopIndex].ui32SourceAddress, rxMemoryCopyTests[ui32LoopIndex].ui32DestinationAddress, rxMemoryCopyTests[ui32LoopIndex].ui32Size);

      if (ui8Error)
      {
         LogTest("main::vTestMemory: Test-Copy[%d] NOK!", ui32LoopIndex);
      }
      else
      {
         LogTest("main::vTestMemory: Test-Copy[%d] OK!", ui32LoopIndex);
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


   vTestMemory(&xMemory);
   return(i32Status);
}
