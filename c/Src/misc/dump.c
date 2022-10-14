#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/helpers.h"
#include "misc/memory.h"
#include "misc/dump.h"


/***************************************************************
 * @param pxMemory Pointer to Memory
 * @param ui32DestinationAddress Destination Address
 * @param ui32Size Size of Data
 * @param pui8Data Poiinter to Data
 * @return -1: different addresses
 *         -2: different sizes
 *         -3: different data
 *          0: dumps are equal
 **************************************************************/
int32_t i32DumpCompare(Dump_t *pxOriginalDump, Dump_t *pxSecondaryDump)
{
   uint8_t  i8Comparison = 0;
   uint32_t ui32Size     = pxOriginalDump->ui32Size;
   if (pxOriginalDump->ui32BaseAddress != pxSecondaryDump->ui32BaseAddress)
   {
      LogTest("memory::i32MemoryCompareDump: Error! Dump different Base Addrresses %d %d", (pxOriginalDump->ui32BaseAddress), pxSecondaryDump->ui32BaseAddress);
      i8Comparison = -1;
   }

   if (pxOriginalDump->ui32Size != pxSecondaryDump->ui32Size)
   {
      LogTest("memory::i32MemoryCompareDump: Error! Dump different sizes %d %d", (pxOriginalDump->ui32Size), pxSecondaryDump->ui32Size);
      i8Comparison = -2;
   }

   // Continue of there is no error
   if (!i8Comparison)
   {
      for (uint32_t ui32ArrayIndex = 0; ui32ArrayIndex < ui32Size; ++ui32ArrayIndex)
      {
         if (pxOriginalDump->pui8Data[ui32ArrayIndex] != pxSecondaryDump->pui8Data[ui32ArrayIndex])
         {
            LogTest("memory::i32MemoryCompareDump: Error! Dump different at %x %x %x", (pxOriginalDump->ui32BaseAddress + ui32ArrayIndex), pxOriginalDump->pui8Data[ui32ArrayIndex], pxSecondaryDump->pui8Data[ui32ArrayIndex]);
            i8Comparison = -3;
         }
      }
   }

   return(i8Comparison);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui8FreeByte Fill Byte between the blocks
* @return Pointer to Dump struct
***************************************************************/
Dump_t * pxMemoryGenerateDump(Memory_t *pxMemory, uint8_t ui8FreeByte)
{
   Memoryblock_t *pxMemoryblock;
   uint32_t       ui32DumpSize = ui32MemoryGetTotalSize(pxMemory);


   Dump_t *pxDump = NULL;
   if (ui32DumpSize > 0)
   {
      pxDump = malloc(sizeof(Dump_t));

      // Update base if 0
      if (pxMemory->ui32BaseAddress == 0 && (pxMemory->pxMemoryblockHead != NULL))
      {
         pxDump->ui32BaseAddress = pxMemory->pxMemoryblockHead->ui32BlockAddress;
      }
      else
      {
         pxDump->ui32BaseAddress = pxMemory->ui32BaseAddress;
      }

      pxDump->ui32Size = ui32DumpSize;
      pxDump->pui8Data = malloc(ui32DumpSize);

      // Fill with ui8Freebyte
      memset(pxDump->pui8Data, ui8FreeByte, ui32DumpSize);

      // Copy into memory
      pxMemoryblock = pxMemory->pxMemoryblockHead;
      while (pxMemoryblock != NULL)
      {
         memcpy(pxDump->pui8Data + (pxMemoryblock->ui32BlockAddress - pxDump->ui32BaseAddress), pxMemoryblock->pui8Buffer, pxMemoryblock->ui32BlockSize);
         pxMemoryblock = pxMemoryblock->pxMemoryblockNext;
      }
   }

   return(pxDump);
}
