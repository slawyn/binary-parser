#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/helpers.h"
#include "misc/memory.h"
#include "misc/dump.h"


/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui8FreeByte Fill Byte between the blocks
* @return Pointer to Dump struct
***************************************************************/
Dump_t * pxConvertMemoryToDump(Memory_t *pxMemory, uint8_t ui8FreeByte)
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
