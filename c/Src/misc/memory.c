#include <stdio.h>
#include <stdlib.h>

#include "types.h"
#include "misc/helpers.h"
#include "misc/memory.h"


void vMemoryInit(Memory_t *pxMemory)
{
   pxMemory->ui32BlockCount    = 0;
   pxMemory->ui32BaseAddress   = 0;
   pxMemory->pxMemoryblockLast = NULL;
   pxMemory->pxMemoryblockHead = NULL;
}

void vMemoryPrint(Memory_t *pxMemory)
{
   uint32_t       ui32BlockIndex;
   uint32_t       ui32InnerBufferIndex;
   Memoryblock_t *pxMemoryblock;

   // Print total count
   printf("\nMemory:[%-6d]", pxMemory->ui32BlockCount);

   // Print contents
   pxMemoryblock = pxMemory->pxMemoryblockHead;
   for (ui32BlockIndex = 0; ui32BlockIndex < pxMemory->ui32BlockCount; ++ui32BlockIndex)
   {
      printf("\n%010x[ %-4d]", pxMemoryblock->ui32BlockAddress, pxMemoryblock->ui32BlockSize);
      for (ui32InnerBufferIndex = 0; ui32InnerBufferIndex < pxMemoryblock->ui32BlockSize; ++ui32InnerBufferIndex)
      {
         printf(" %02x", pxMemoryblock->pui8Buffer[ui32InnerBufferIndex]);
      }
      pxMemoryblock = pxMemoryblock->pxMemoryblockNext;
   }
}

int32_t i32MemoryblockInit(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t *pui8Buffer)
{
   Memoryblock_t *pxMemoryblock;

   pxMemoryblock = (Memoryblock_t *)malloc(sizeof(Memoryblock_t));
   if (pxMemoryblock == NULL)
   {
      return(-1);
   }

   pxMemoryblock->ui32BlockAddress  = (ui32BlockAddress + pxMemory->ui32BaseAddress);
   pxMemoryblock->ui32BlockSize     = ui32BufferSize;
   pxMemoryblock->pui8Buffer        = pui8Buffer;
   pxMemoryblock->pxMemoryblockNext = NULL;

   if (pxMemory->pxMemoryblockLast != NULL)
   {
      pxMemory->pxMemoryblockLast->pxMemoryblockNext = pxMemoryblock;
   }
   // Set head
   else if (pxMemory->pxMemoryblockHead == NULL)
   {
      pxMemory->pxMemoryblockHead = pxMemoryblock;
   }

   pxMemory->pxMemoryblockLast = pxMemoryblock;
   ++pxMemory->ui32BlockCount;

   return(0);
}
