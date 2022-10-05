#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "types.h"
#include "misc/helpers.h"
#include "misc/memory.h"



static int32_t i32MemoryDestroyBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock);
static Memoryblock_t * pxMemoryCreateBlock(Memory_t *pxMemory, uint32_t ui32BlockAddress, uint32_t ui32BufferSize, uint8_t rui8Buffer[]);

/*
 * @param pxMemory Pointer to Memory
 */
void vMemoryInit(Memory_t *pxMemory)
{
   pxMemory->ui32BlockCount    = 0;
   pxMemory->ui32BaseAddress   = 0;
   pxMemory->pxMemoryblockTail = NULL;
   pxMemory->pxMemoryblockHead = NULL;
}

/*
 * @param pxMemory Pointer to Memory
 */
void vMemoryPrint(Memory_t *pxMemory)
{
   uint32_t       ui32BlockIndex;
   uint32_t       ui32InnerBufferIndex;
   Memoryblock_t *pxMemoryblock;

   // Print total count
   printf("Memory:[%-d]", pxMemory->ui32BlockCount);

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

/*
 * @param pxMemory Pointer to Memory
 * @param ui32SourceStartAddress Source Address
 * @param ui32DestinationStartAddress Destination Address
 * @param ui32SizeToCopy Size to Copy
 */
int32_t i32MemoryCopy(Memory_t *pxMemory, uint32_t ui32SourceStartAddress, uint32_t ui32DestinationStartAddress, int32_t i32SizeToCopy)
{
   Memoryblock_t *pxMemoryblock;
   Memoryblock_t *pxMemorySourceblock;
   Memoryblock_t *pxMemoryTempblock;

   uint32_t ui32SourceEndAddress      = ui32SourceStartAddress + i32SizeToCopy;
   uint32_t ui32DestinationEndAddress = ui32DestinationStartAddress + i32SizeToCopy;
   int32_t  i32MemoryOverlap;
   uint8_t  ui8Done = 0;

   // Invalid Pointers
   if (pxMemory->pxMemoryblockHead == NULL || pxMemory->pxMemoryblockTail == NULL)
   {
      LogTest("memory::MemoryCopy: Error:Head or Tail NULL");
      return(-1);
   }

   // Size is overlapping
   if (((ui32DestinationStartAddress > ui32SourceStartAddress) &&
        ((ui32DestinationStartAddress - ui32SourceStartAddress) < i32SizeToCopy)) ||
       ((ui32DestinationStartAddress <= ui32SourceStartAddress) &&
        (ui32SourceStartAddress - ui32DestinationStartAddress) < i32SizeToCopy))
   {
      LogTest("memory::MemoryCopy: Error:Regions overlap");
      return(-2);
   }

   // Free Destination blocks
   pxMemoryblock = pxMemory->pxMemoryblockHead;
   while (!ui8Done)
   {
      // Split the first intersecting block in the destination region
      LogTest("memory::MemoryCopy: Block at %x", pxMemoryblock->ui32BlockAddress);
      if (pxMemoryblock->ui32BlockAddress <= ui32DestinationStartAddress)
      {
         LogTest("memory::MemoryCopy: Traversing Before Destination Region");
         i32MemoryOverlap  = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32DestinationStartAddress;
         pxMemoryTempblock = pxMemoryblock->pxMemoryblockNext;
         if (i32MemoryOverlap > 0)
         {
            // Remove whole block
            if (i32MemoryOverlap == pxMemoryblock->ui32BlockSize)
            {
               i32MemoryDestroyBlock(pxMemory, pxMemoryblock);
            }
            // Split the block
            else
            {
               pxMemoryblock->ui32BlockSize -= i32MemoryOverlap;

               // Partial copy, free old and assign new
               LogTest("memory::MemoryCopy: Partial overlap-1 at %x of %d", pxMemoryblock->ui32BlockAddress, i32MemoryOverlap);
               uint8_t *pui8SplitBuffer = malloc(pxMemoryblock->ui32BlockSize);
               memcpy(pui8SplitBuffer, pxMemoryblock->pui8Buffer, pxMemoryblock->ui32BlockSize);
               free(pxMemoryblock->pui8Buffer);
               pxMemoryblock->pui8Buffer = pui8SplitBuffer;
            }
         }
         else if (i32MemoryOverlap == 0)
         {
            LogTest("memory::MemoryCopy: Full overlap-1 %x", pxMemoryblock->ui32BlockAddress);
            i32MemoryDestroyBlock(pxMemory, pxMemoryblock);
         }
         pxMemoryblock = pxMemoryTempblock;
      }

      else if (pxMemoryblock->ui32BlockAddress < ui32DestinationEndAddress)
      {
         LogTest("memory::MemoryCopy: Traversing Inside Destination Region");
         i32MemoryOverlap  = (pxMemoryblock->ui32BlockAddress + pxMemoryblock->ui32BlockSize) - ui32DestinationEndAddress;
         pxMemoryTempblock = pxMemoryblock->pxMemoryblockNext;

         if (i32MemoryOverlap <= 0)
         {
            LogTest("memory::MemoryCopy: Full overlap-2 %x", pxMemoryblock->ui32BlockAddress);
            i32MemoryDestroyBlock(pxMemory, pxMemoryblock);
         }
         else if (i32MemoryOverlap > 0)
         {
            // Partial copy, free old and assign new
            LogTest("memory::MemoryCopy: Partial overlap-2 at %x of %d", pxMemoryblock->ui32BlockAddress, i32MemoryOverlap);
            uint8_t *pui8SplitBuffer = malloc(i32MemoryOverlap);
            uint32_t ui32Offset      = pxMemoryblock->ui32BlockSize - i32MemoryOverlap;
            memcpy(pui8SplitBuffer, (pxMemoryblock->pui8Buffer + ui32Offset), i32MemoryOverlap);
            free(pxMemoryblock->pui8Buffer);
            pxMemoryblock->ui32BlockAddress += ui32Offset;
            pxMemoryblock->ui32BlockSize     = i32MemoryOverlap;
            pxMemoryblock->pui8Buffer        = pui8SplitBuffer;
         }
         pxMemoryblock = pxMemoryTempblock;
      }
      else
      {
         LogTest("memory::MemoryCopy: Traversing Done-1 at %x", pxMemoryblock->ui32BlockAddress);
         ui8Done = TRUE;
      }

      if (pxMemoryblock == NULL)
      {
         LogTest("memory::MemoryCopy: Traversing Done-2");
         ui8Done = TRUE;
      }
   }


   return(0);
}

/*
 * @param pxMemory Pointer to Memory
 * @param ui32BlockAddress Block base address
 * @param ui32BufferSize Byte Count
 * @param rui8Buffer Buffer Pointer
 */
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

/*
 * @param pxMemory Pointer to Memory
 * @param ui32BlockAddress Block base address
 * @param ui32BufferSize Byte Count
 * @param rui8Buffer Buffer Pointer
 */
static int32_t i32MemoryDestroyBlock(Memory_t *pxMemory, Memoryblock_t *pxMemoryblock)
{
   if (pxMemoryblock == NULL)
   {
      return(-1);
   }

   if (pxMemoryblock->pui8Buffer != NULL)
   {
      free(pxMemoryblock->pui8Buffer);
   }
   --pxMemory->ui32BlockCount;
   free(pxMemoryblock);
   return(0);
}

/*
 * @param pxMemory Pointer to Memory
 * @param ui32BlockAddress Block base address
 * @param ui32BufferSize Byte Count
 * @param rui8Buffer Buffer Pointer
 */
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
      LogTest("memory::MemoryAdd: Creating Head of %x at %x", ui32FullBlockAddress, pxMemoryblock->ui32BlockAddress);
   }
   else
   {
      // Searching forward
      // Until no blocks left
      pxMemoryblockForward  = pxMemory->pxMemoryblockHead;
      pxMemoryblockBackward = pxMemory->pxMemoryblockTail;
      while (pxMemoryblockForward->pxMemoryblockNext != NULL)
      {
         if (ui32FullBlockAddress >= pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress)
         {
            pxMemoryblockForward = pxMemoryblockForward->pxMemoryblockNext;
         }
         else
         {
            break;
         }
      }

      // Block preceeding new memory region
      if (pxMemoryblockForward->ui32BlockAddress <= ui32FullBlockAddress)
      {
         LogTest("memory::MemoryAdd: Searching inside at %x with previous %x", ui32FullBlockAddress, pxMemoryblockForward->ui32BlockAddress);


         // Previous block overlaps with the new region
         i32MemoryOverlap = (pxMemoryblockForward->ui32BlockAddress + pxMemoryblockForward->ui32BlockSize) - ui32FullBlockAddress;
         if (i32MemoryOverlap > 0)
         {
            //
            // Overlap is bigger than current memory region
            // No new block needed, region is absorbed by previous block
            if (i32MemoryOverlap > ui32BufferSize)
            {
               LogTest("memory::MemoryAdd: Overlap-0 of %d", ui32BufferSize);
               memcpy(&pxMemoryblockForward->pui8Buffer[pxMemoryblockForward->ui32BlockSize - ui32BufferSize], rui8Buffer, ui32BufferSize);
               ui32BufferSize = 0;
            }
            // Partial copy over previous block
            else
            {
               LogTest("memory::MemoryAdd: Overlap-1 of %d at %x", i32MemoryOverlap, pxMemoryblockForward->ui32BlockAddress);
               memcpy(&pxMemoryblockForward->pui8Buffer[pxMemoryblockForward->ui32BlockSize - i32MemoryOverlap], rui8Buffer, i32MemoryOverlap);
               ui32FullBlockAddress += i32MemoryOverlap;
               ui32BufferSize       -= i32MemoryOverlap;
               rui8Buffer            = &rui8Buffer[i32MemoryOverlap];
            }
         }

         // New region overlaps with the next block
         if (ui32BufferSize > 0)
         {
            if (pxMemoryblockForward->pxMemoryblockNext != NULL)
            {
               i32MemoryOverlap = (ui32FullBlockAddress + ui32BufferSize) - pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress;
               if (i32MemoryOverlap > 0)
               {
                  LogTest("memory::MemoryAdd: Overlap-3 at %x with previous %x of %d", ui32FullBlockAddress, pxMemoryblockForward->ui32BlockAddress, i32MemoryOverlap);
                  ui32BufferSize -= i32MemoryOverlap;
               }

               // Create block if there is anything left in space between the previous and next regions
               if (ui32BufferSize > 0)
               {
                  LogTest("memory::MemoryAdd: Creating Block-0 of %d at %x", ui32BufferSize, ui32FullBlockAddress);

                  pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
                  pxMemoryblock->pxMemoryblockNext        = pxMemoryblockForward->pxMemoryblockNext;
                  pxMemoryblockForward->pxMemoryblockNext = pxMemoryblock;
               }

               // Copy recursively forward
               if (i32MemoryOverlap > 0)
               {
                  LogTest("memory::MemoryAdd: Recursive-1 %x %d", pxMemoryblockForward->ui32BlockAddress, ui32BufferSize);
                  i32Error = i32MemoryAdd(pxMemory, pxMemoryblockForward->pxMemoryblockNext->ui32BlockAddress, i32MemoryOverlap, &rui8Buffer[ui32BufferSize]);
               }
            }
            else
            {
               LogTest("memory::MemoryAdd: Creating Block-1 of %d at %x", ui32BufferSize, ui32FullBlockAddress);

               // Create block
               pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
               pxMemoryblock->pxMemoryblockNext        = pxMemoryblockForward->pxMemoryblockNext;
               pxMemoryblockForward->pxMemoryblockNext = pxMemoryblock;
            }
         }
      }
      else
      {
         LogTest("memory::MemoryAdd: Searching outside at %x with previous %x", ui32FullBlockAddress, pxMemoryblockForward->ui32BlockAddress);
         i32MemoryOverlap = (ui32FullBlockAddress + ui32BufferSize) - pxMemoryblockForward->ui32BlockAddress;
         if (i32MemoryOverlap > 0)
         {
            LogTest("memory::MemoryAdd:Overlap-4 of %x", i32MemoryOverlap);
            ui32BufferSize -= i32MemoryOverlap;
         }

         // Create block
         pxMemoryblock = pxMemoryCreateBlock(pxMemory, ui32FullBlockAddress, ui32BufferSize, rui8Buffer);
         pxMemoryblock->pxMemoryblockNext = pxMemoryblockForward;

         // Copy recursively forward
         if (i32MemoryOverlap > 0)
         {
            LogTest("memory::MemoryAdd:Recursive-2 at %x of %d", pxMemoryblockForward->ui32BlockAddress, ui32BufferSize);
            i32Error = i32MemoryAdd(pxMemory, pxMemoryblockForward->ui32BlockAddress, i32MemoryOverlap, &rui8Buffer[ui32BufferSize]);
         }
      }


      LogTest("memory::MemoryAdd: Done");

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
