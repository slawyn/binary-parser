#include <stdio.h>
#include <stdlib.h>

#include "types.h"
#include "misc/helpers.h"
#include "misc/memory.h"

/***************************************************************
* @param pxMemory Pointer to Memory
***************************************************************/
void vMemoryInit(Memory_t *pxMemory)
{
   pxMemory->ui32BlockCount    = 0;
   pxMemory->ui32BaseAddress   = 0;
   pxMemory->pxMemoryblockTail = NULL;
   pxMemory->pxMemoryblockHead = NULL;
}

/***************************************************************
* @param pxMemory Pointer to Memory
***************************************************************/
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

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui32SourceAddress Source Address
* @param ui32DestinationAddress Destination Address
* @param ui32SizeToCopy Size to Copy
***************************************************************/
int32_t i32MemoryCopy(Memory_t *pxMemory, uint32_t ui32SourceAddress, uint32_t ui32DestinationAddress, int32_t i32SizeToCopy)
{
   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemorySourceblock;


   uint32_t ui32CopyEndAddress = ui32SourceAddress + i32SizeToCopy;

   // Invalid Pointers
   if (pxMemory->pxMemoryblockHead == NULL || pxMemory->pxMemoryblockTail == NULL)
   {
      return(-1);
   }

   // Size is overlapping
   if (((ui32DestinationAddress > ui32SourceAddress) && ((ui32DestinationAddress - ui32SourceAddress) > i32SizeToCopy)) || (ui32SourceAddress - ui32DestinationAddress) > i32SizeToCopy)
   {
      return(-2);
   }

   // Find Block for Source
   pxMemorySourceblock = pxMemory->pxMemoryblockHead;
   while (pxMemorySourceblock->pxMemoryblockNext != NULL && (ui32SourceAddress <= pxMemorySourceblock->pxMemoryblockNext->ui32BlockAddress))
   {
      pxMemorySourceblock = pxMemorySourceblock->pxMemoryblockNext;
   }


   return(0);
}

static int32_t i32MemoryblockInsert(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock)
{
   Memoryblock_t *pxMemoryblockIteratee;
   uint8_t        ui8Inserted = 0;
   int32_t        i32Error    = 0;



   // Block is not first or not last, then inside the memory region somewhere
   if (!ui8Inserted)
   {
      // Insert between blocks
      pxMemoryblock->pxMemoryblockNext         = pxMemoryblockIteratee->pxMemoryblockNext;
      pxMemoryblockIteratee->pxMemoryblockNext = pxMemoryblock;
   }

   ++pxMemory->ui32BlockCount;
   return(i32Error);
}

static Memoryblock_t * i32MemoryCreateBlock(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[])
{
   Memoryblock_t *pxMemoryblock;
   pxMemoryblock = (Memoryblock_t *)malloc(sizeof(Memoryblock_t));
   if (pxMemoryblock == NULL)
   {
      return(NULL);
   }

   uint8_t *pui8Buffer = malloc(ui32BufferSize);
   if (pui8Buffer == NULL)
   {
      free(pxMemoryblock);
      return(NULL);
   }
   else
   {
      memcpy(pui8Buffer, rui8Buffer, ui32BufferSize);
   }


   // Init block

   pxMemoryblock->ui32BlockAddress  = ui32BlockAddress;
   pxMemoryblock->ui32BlockSize     = ui32BufferSize;
   pxMemoryblock->pui8Buffer        = pui8Buffer;
   pxMemoryblock->pxMemoryblockNext = NULL;


   return(pxMemoryblock);
}

/***************************************************************
* @param pxMemory Pointer to Memory
* @param ui32BlockAddress Block base address
* @param ui32BufferSize Byte Count
* @param pui8Buffer Buffer Pointer
***************************************************************/
int32_t i32MemoryAdd(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[])
{
   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemoryblockForward;
   Memoryblock_t *pxMemoryblockBackward;
   uint8_t        ui8Found             = 0;
   uint32_t       ui32FullBlockAddress = (ui32BlockAddress + pxMemory->ui32BaseAddress);
   int32_t        i32MemoryOverlap     = 0;

   if (pxMemory->pxMemoryblockHead == NULL)
   {
      pxMemoryblock = i32MemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
      pxMemory->pxMemoryblockHead = pxMemoryblock;
      pxMemory->pxMemoryblockTail = pxMemoryblock;
   }
   else
   {
      pxMemoryblockForward  = pxMemory->pxMemoryblockHead;
      pxMemoryblockBackward = pxMemory->pxMemoryblockTail;
      while (!ui8Found)
      {
         // Searching forward
         if (pxMemoryblockForward->pxMemoryblockNext != NULL)
         {
            if (ui32FullBlockAddress < pxMemoryblockForward->ui32BlockAddress)
            {
               pxMemoryblockForward = pxMemoryblockForward->pxMemoryblockNext;
            }

            if (ui32FullBlockAddress >= pxMemoryblockForward->ui32BlockAddress)
            {
            }
         }
         else
         {
            // Memory overlaps, then copy over
            i32MemoryOverlap = (pxMemoryblockForward->ui32BlockAddress + pxMemoryblockForward->ui32BlockSize) - ui32FullBlockAddress;
            if (i32MemoryOverlap > 0)
            {
               //
               // Overlap is bigger than current memory region
               // No new block needed, just copy over
               if (i32MemoryOverlap >= ui32BufferSize)
               {
                  memcpy(&pxMemoryblockForward->pui8Buffer[pxMemoryblockForward->ui32BlockSize - ui32BufferSize], rui8Buffer, ui32BufferSize);
               }
               // Partial copy, then new block
               else
               {
                  memcpy(&pxMemoryblockForward->pui8Buffer[pxMemoryblockForward->ui32BlockSize - i32MemoryOverlap], rui8Buffer, i32MemoryOverlap);
                  pxMemoryblock = i32MemoryCreateBlock(pxMemory, ui32FullBlockAddress + i32MemoryOverlap, ui32BufferSize - i32MemoryOverlap, &rui8Buffer[i32MemoryOverlap]);
               }
            }
         }


         /*
          * // Searching backward
          * if (ui32FullBlockAddress < pxMemoryblockBackward->ui32BlockAddress && (pxMemoryblockBackward->pxMemoryblockPrevious != NULL))
          * {
          * pxMemoryblockBackward = pxMemoryblockBackward->pxMemoryblockPrevious;
          * }
          * else if (pxMemoryblockBackward->pxMemoryblockPrevious == NULL)
          * {
          * pxMemoryblock = i32MemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
          * }
          * else
          * {
          * }
          */
      }
   }


   // Append and Prepend
   //------------------------------------------
   // Append to Last
   if (pxMemoryblock->ui32BlockAddress > pxMemory->pxMemoryblockTail->ui32BlockAddress)
   {
      pxMemory->pxMemoryblockTail->pxMemoryblockNext = pxMemoryblock;
      pxMemory->pxMemoryblockTail = pxMemoryblock;
   }

   // Prepend to Head
   if (pxMemoryblock->ui32BlockAddress < pxMemory->pxMemoryblockHead->ui32BlockAddress)
   {
      pxMemoryblock->pxMemoryblockNext = pxMemory->pxMemoryblockHead;
      pxMemory->pxMemoryblockHead      = pxMemoryblock;
   }

   // Insert block
   return(0);
}
