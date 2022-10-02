#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
   printf("\nMemory:[%-d]", pxMemory->ui32BlockCount);

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
   printf("\n");
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

static Memoryblock_t * pxMemoryCreateBlock(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[])
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

   ++pxMemory->ui32BlockCount;
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
   Memoryblock_t *pxMemoryblock = NULL;
   Memoryblock_t *pxMemoryblockForward;
   Memoryblock_t *pxMemoryblockBackward;
   uint8_t        ui8Found             = 0;
   uint32_t       ui32FullBlockAddress = (ui32BlockAddress + pxMemory->ui32BaseAddress);
   int32_t        i32MemoryOverlap     = 0;
   int32_t        i32Error             = 0;

   if (pxMemory->pxMemoryblockHead == NULL)
   {
      pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
      pxMemory->pxMemoryblockHead = pxMemoryblock;
      pxMemory->pxMemoryblockTail = pxMemoryblock;
      i32Log("**head** %x %x", ui32FullBlockAddress, pxMemoryblock->ui32BlockAddress);
   }
   else
   {
      // Searching forward
      // Until no blocks left
      pxMemoryblockForward  = pxMemory->pxMemoryblockHead;
      pxMemoryblockBackward = pxMemory->pxMemoryblockTail;
      while (pxMemoryblockForward->pxMemoryblockNext != NULL)
      {
         if (ui32FullBlockAddress <= pxMemoryblockForward->ui32BlockAddress)
         {
            break;
         }
         else
         {
            pxMemoryblockForward = pxMemoryblockForward->pxMemoryblockNext;
         }
      }

      // Block preceeding new memory region
      if (pxMemoryblockForward->ui32BlockAddress <= ui32FullBlockAddress)
      {
         i32Log("**after** %x %x", ui32FullBlockAddress, pxMemoryblockForward->ui32BlockAddress);


         // Previous memory overlaps, then copy over
         i32MemoryOverlap = (pxMemoryblockForward->ui32BlockAddress + pxMemoryblockForward->ui32BlockSize) - ui32FullBlockAddress;
         if (i32MemoryOverlap > 0)
         {
            //
            // Overlap is bigger than current memory region
            // No new block needed, region is absorbed by previous block
            if (i32MemoryOverlap > ui32BufferSize)
            {
               i32Log("test-0 %d", ui32BufferSize);
               memcpy(&pxMemoryblockForward->pui8Buffer[pxMemoryblockForward->ui32BlockSize - ui32BufferSize], rui8Buffer, ui32BufferSize);
            }
            // Partial copy over previous block
            else
            {
               i32Log("test-1 %d %d", i32MemoryOverlap, pxMemoryblockForward->ui32BlockSize - i32MemoryOverlap);
               memcpy(&pxMemoryblockForward->pui8Buffer[pxMemoryblockForward->ui32BlockSize - i32MemoryOverlap], rui8Buffer, i32MemoryOverlap);
               ui32FullBlockAddress += i32MemoryOverlap;
               ui32BufferSize       -= i32MemoryOverlap;
               rui8Buffer            = &rui8Buffer[i32MemoryOverlap];
            }
         }

         if (ui32BufferSize > 0)
         {
            // Next memory region overlaps
            if (pxMemoryblockForward->pxMemoryblockNext != NULL)
            {
               i32Log("test-2 %x %x", ui32FullBlockAddress, pxMemoryblockForward->ui32BlockAddress);
               i32MemoryOverlap = (ui32FullBlockAddress + ui32BufferSize) - pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress;
               if (i32MemoryOverlap > 0)
               {
                  ui32BufferSize -= i32MemoryOverlap;
               }

               // Create block
               pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
               pxMemoryblock->pxMemoryblockNext        = pxMemoryblockForward->pxMemoryblockNext;
               pxMemoryblockForward->pxMemoryblockNext = pxMemoryblock;

               i32Log("test-3");

               // Copy recursively forward
               if (i32MemoryOverlap > 0)
               {
                  i32Log("recursive-1 %x %d", pxMemoryblockForward->ui32BlockAddress, ui32BufferSize);
                  i32Error = i32MemoryAdd(pxMemory, pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress, i32MemoryOverlap, &rui8Buffer[ui32BufferSize]);
               }
            }
            else
            {
               i32Log("test-4");

               // Create block
               pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
               pxMemoryblock->pxMemoryblockNext        = pxMemoryblockForward->pxMemoryblockNext;
               pxMemoryblockForward->pxMemoryblockNext = pxMemoryblock;
            }
         }
      }
      else
      {
         i32Log("**before** %x %x", ui32FullBlockAddress, pxMemoryblockForward->ui32BlockAddress);

         i32MemoryOverlap = (ui32FullBlockAddress + ui32BufferSize) - pxMemoryblockForward->ui32BlockAddress;
         if (i32MemoryOverlap > 0)
         {
            ui32BufferSize -= i32MemoryOverlap;
         }

         // Create block
         pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
         pxMemoryblock->pxMemoryblockNext = pxMemoryblockForward;

         // Copy recursively forward
         if (i32MemoryOverlap > 0)
         {
            i32Log("recursive-2 %x %d", pxMemoryblockForward->ui32BlockAddress, ui32BufferSize);
            i32Error = i32MemoryAdd(pxMemory, pxMemoryblockForward->ui32BlockAddress, i32MemoryOverlap, &rui8Buffer[ui32BufferSize]);
         }
      }


      i32Log("run");

      /*
       * // Searching backward
       * if (ui32FullBlockAddress < pxMemoryblockBackward->ui32BlockAddress && (pxMemoryblockBackward->pxMemoryblockPrevious != NULL))
       * {
       * pxMemoryblockBackward = pxMemoryblockBackward->pxMemoryblockPrevious;
       * }
       * else if (pxMemoryblockBackward->pxMemoryblockPrevious == NULL)
       * {
       * pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
       * }
       * else
       * {
       * }
       */


      // Append and Prepend
      //------------------------------------------
      if (pxMemoryblock != NULL)
      {
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
      }
   }
   // Insert block
   return(i32Error);
}
